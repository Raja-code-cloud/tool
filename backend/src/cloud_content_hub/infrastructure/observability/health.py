"""Generic concurrent asynchronous health checks."""

import asyncio
import time
from collections.abc import Awaitable, Callable, Mapping, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol


class HealthStatus(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass(frozen=True, slots=True)
class HealthResult:
    name: str
    status: HealthStatus
    duration_ms: float
    message: str | None = None
    details: Mapping[str, str | int | float | bool] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AggregateHealth:
    status: HealthStatus
    checks: tuple[HealthResult, ...]
    duration_ms: float


class HealthCheck(Protocol):
    @property
    def name(self) -> str:
        """Stable, low-cardinality check name."""

    async def check(self) -> HealthResult:
        """Run a non-blocking dependency check."""


@dataclass(frozen=True, slots=True)
class ApplicationHealthCheck:
    """Reports process liveness without external dependencies."""

    _name: str = "application"

    @property
    def name(self) -> str:
        return self._name

    async def check(self) -> HealthResult:
        return HealthResult(
            name=self._name,
            status=HealthStatus.HEALTHY,
            duration_ms=0.0,
            message="Process is running",
        )


@dataclass(frozen=True, slots=True)
class PingHealthCheck:
    """Generic async ping check for database, Redis, blob, or external APIs."""

    _name: str
    _ping: Callable[[], Awaitable[bool]]
    _degraded_on_failure: bool = False

    @property
    def name(self) -> str:
        return self._name

    async def check(self) -> HealthResult:
        started = time.perf_counter()
        try:
            ok = await self._ping()
            status = (
                HealthStatus.HEALTHY
                if ok
                else (
                    HealthStatus.DEGRADED
                    if self._degraded_on_failure
                    else HealthStatus.UNHEALTHY
                )
            )
            return HealthResult(
                name=self._name,
                status=status,
                duration_ms=round((time.perf_counter() - started) * 1000, 2),
            )
        except Exception:
            return HealthResult(
                name=self._name,
                status=(
                    HealthStatus.DEGRADED
                    if self._degraded_on_failure
                    else HealthStatus.UNHEALTHY
                ),
                duration_ms=round((time.perf_counter() - started) * 1000, 2),
                message="Dependency check failed",
            )


def create_ping_health_check(
    name: str,
    ping: Callable[[], Awaitable[bool]],
    *,
    degraded_on_failure: bool = False,
) -> HealthCheck:
    """Create a reusable ping check for any async dependency probe."""
    return PingHealthCheck(name, ping, degraded_on_failure)


class HealthChecker:
    def __init__(self, checks: Sequence[HealthCheck], timeout_seconds: float = 5.0) -> None:
        self._checks = tuple(checks)
        self._timeout_seconds = timeout_seconds

    async def check(self) -> AggregateHealth:
        started = time.perf_counter()
        results = await asyncio.gather(*(self._run(check) for check in self._checks))
        status = _aggregate_status(results)
        return AggregateHealth(
            status=status,
            checks=tuple(results),
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
        )

    async def _run(self, check: HealthCheck) -> HealthResult:
        started = time.perf_counter()
        message = "Health check failed"
        try:
            async with asyncio.timeout(self._timeout_seconds):
                return await check.check()
        except TimeoutError:
            message = "Health check timed out"
        except asyncio.CancelledError:
            raise
        except Exception:
            message = "Health check failed"
        return HealthResult(
            name=check.name,
            status=HealthStatus.UNHEALTHY,
            duration_ms=round((time.perf_counter() - started) * 1000, 2),
            message=message,
        )


def _aggregate_status(results: Sequence[HealthResult]) -> HealthStatus:
    statuses = {result.status for result in results}
    if HealthStatus.UNHEALTHY in statuses:
        return HealthStatus.UNHEALTHY
    if HealthStatus.DEGRADED in statuses:
        return HealthStatus.DEGRADED
    return HealthStatus.HEALTHY
