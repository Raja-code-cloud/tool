"""Validate dependency unavailability detection and recovery signals."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from cloud_content_hub.core.errors import DependencyUnavailableError
from cloud_content_hub.infrastructure.observability.health import HealthStatus
from tests.disaster_recovery.helpers.readiness import probe_readiness
from tests.disaster_recovery.helpers.simulation import (
    DependencyState,
    build_recovery_health_checker,
    simulate_recovery_sequence,
)


@pytest.mark.asyncio
async def test_database_unavailable_marks_aggregate_unhealthy() -> None:
    checker = build_recovery_health_checker(DependencyState(database=False))
    aggregate = await checker.check()

    assert aggregate.status is HealthStatus.UNHEALTHY
    database_result = next(r for r in aggregate.checks if r.name == "database")
    assert database_result.status is HealthStatus.UNHEALTHY


@pytest.mark.asyncio
async def test_redis_unavailable_marks_aggregate_unhealthy() -> None:
    checker = build_recovery_health_checker(DependencyState(redis=False))
    aggregate = await checker.check()

    assert aggregate.status is HealthStatus.UNHEALTHY
    redis_result = next(r for r in aggregate.checks if r.name == "redis")
    assert redis_result.status is HealthStatus.UNHEALTHY


@pytest.mark.asyncio
async def test_blob_unavailable_marks_aggregate_degraded_not_unhealthy() -> None:
    checker = build_recovery_health_checker(DependencyState(storage=False))
    aggregate = await checker.check()

    assert aggregate.status is HealthStatus.DEGRADED
    storage_result = next(r for r in aggregate.checks if r.name == "storage")
    assert storage_result.status is HealthStatus.DEGRADED


@pytest.mark.asyncio
async def test_full_recovery_restores_healthy_status() -> None:
    sequence = (
        DependencyState(database=False, redis=True, storage=True),
        DependencyState(database=True, redis=False, storage=True),
        DependencyState(database=True, redis=True, storage=False),
        DependencyState(database=True, redis=True, storage=True, outbox=True),
    )
    statuses = await simulate_recovery_sequence(sequence)

    assert statuses == [
        HealthStatus.UNHEALTHY,
        HealthStatus.UNHEALTHY,
        HealthStatus.DEGRADED,
        HealthStatus.HEALTHY,
    ]


@pytest.mark.asyncio
async def test_readiness_probe_fails_when_database_unavailable() -> None:
    async def check_database() -> None:
        raise ConnectionError("database down")

    async def check_redis() -> None:
        return None

    result = await probe_readiness(
        check_database=check_database,
        check_redis=check_redis,
        database_timeout_seconds=1.0,
        redis_timeout_seconds=1.0,
    )

    assert result.ready is False
    assert result.checks["database"] == "unavailable"
    assert result.checks["redis"] == "ok"


@pytest.mark.asyncio
async def test_readiness_probe_fails_when_redis_unavailable() -> None:
    async def check_database() -> None:
        return None

    async def check_redis() -> None:
        raise ConnectionError("redis down")

    result = await probe_readiness(
        check_database=check_database,
        check_redis=check_redis,
        database_timeout_seconds=1.0,
        redis_timeout_seconds=1.0,
    )

    assert result.ready is False
    assert result.checks["database"] == "ok"
    assert result.checks["redis"] == "unavailable"


@pytest.mark.asyncio
async def test_readiness_probe_succeeds_when_dependencies_recover() -> None:
    database = AsyncMock()
    redis = AsyncMock()

    async def check_database() -> None:
        await database.execute()

    async def check_redis() -> None:
        await redis.ping()

    result = await probe_readiness(
        check_database=check_database,
        check_redis=check_redis,
        database_timeout_seconds=1.0,
        redis_timeout_seconds=1.0,
    )

    assert result.ready is True
    assert result.checks == {"database": "ok", "redis": "ok"}


def test_dependency_unavailable_error_is_readiness_signal() -> None:
    error = DependencyUnavailableError(detail="Required dependencies are unavailable.")
    assert error.code == "dependency_unavailable"
