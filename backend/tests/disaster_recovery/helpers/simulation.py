"""Simulate dependency failures for recovery validation tests."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import StrEnum

from cloud_content_hub.infrastructure.observability.health import (
    ApplicationHealthCheck,
    HealthChecker,
    HealthStatus,
    create_ping_health_check,
)


class DependencyName(StrEnum):
    DATABASE = "database"
    REDIS = "redis"
    STORAGE = "storage"
    OUTBOX = "outbox_dispatch"


@dataclass(frozen=True, slots=True)
class DependencyState:
    """Runtime availability flags for simulated infrastructure."""

    database: bool = True
    redis: bool = True
    storage: bool = True
    outbox: bool = True


def build_recovery_health_checker(state: DependencyState) -> HealthChecker:
    """Build a health checker mirroring bootstrap dependency probes."""

    async def database_ping() -> bool:
        return state.database

    async def redis_ping() -> bool:
        return state.redis

    async def storage_ping() -> bool:
        return state.storage

    async def outbox_ping() -> bool:
        return state.outbox

    return HealthChecker(
        [
            ApplicationHealthCheck(),
            create_ping_health_check(DependencyName.DATABASE, database_ping),
            create_ping_health_check(DependencyName.REDIS, redis_ping),
            create_ping_health_check(
                DependencyName.STORAGE,
                storage_ping,
                degraded_on_failure=True,
            ),
            create_ping_health_check(DependencyName.OUTBOX, outbox_ping),
        ],
        timeout_seconds=1.0,
    )


async def simulate_recovery_sequence(
    states: tuple[DependencyState, ...],
    *,
    checker_factory: Callable[[DependencyState], HealthChecker] = build_recovery_health_checker,
) -> list[HealthStatus]:
    """Run health checks across a sequence of simulated recovery states."""

    results: list[HealthStatus] = []
    for state in states:
        checker = checker_factory(state)
        aggregate = await checker.check()
        results.append(aggregate.status)
    return results


async def run_ping(probe: Callable[[], Awaitable[bool]]) -> bool:
    """Execute a single async ping probe."""

    return await probe()
