"""Validate dependency unavailability detection and recovery signals."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock

from cloud_content_hub.api.errors import install_exception_handlers
from cloud_content_hub.api.routers.v1.health import router as health_router
from cloud_content_hub.core.errors import DependencyUnavailableError
from cloud_content_hub.infrastructure.observability.health import HealthStatus
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
async def test_readiness_endpoint_fails_when_database_unavailable() -> None:
    container = MagicMock()
    connection = AsyncMock()
    connection.execute = AsyncMock(side_effect=ConnectionError("database down"))
    connect_cm = AsyncMock()
    connect_cm.__aenter__.return_value = connection
    connect_cm.__aexit__.return_value = None
    container.database_engine.connect.return_value = connect_cm
    container.redis.ping = AsyncMock(return_value=True)
    container.settings.database_timeout_seconds = 1.0
    container.settings.redis_timeout_seconds = 1.0

    app = FastAPI()
    install_exception_handlers(app)
    app.include_router(health_router)
    app.state.container = container

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/ready")

    assert response.status_code == 503


@pytest.mark.asyncio
async def test_readiness_endpoint_fails_when_redis_unavailable() -> None:
    container = MagicMock()
    connection = AsyncMock()
    connection.execute = AsyncMock(return_value=None)
    connect_cm = AsyncMock()
    connect_cm.__aenter__.return_value = connection
    connect_cm.__aexit__.return_value = None
    container.database_engine.connect.return_value = connect_cm
    container.redis.ping = AsyncMock(side_effect=ConnectionError("redis down"))
    container.settings.database_timeout_seconds = 1.0
    container.settings.redis_timeout_seconds = 1.0

    app = FastAPI()
    install_exception_handlers(app)
    app.include_router(health_router)
    app.state.container = container

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/ready")

    assert response.status_code == 503


@pytest.mark.asyncio
async def test_liveness_succeeds_without_dependencies() -> None:
    app = FastAPI()
    app.include_router(health_router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/live")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["status"] == "live"


def test_dependency_unavailable_error_is_readiness_signal() -> None:
    error = DependencyUnavailableError(detail="Required dependencies are unavailable.")
    assert error.code == "dependency_unavailable"
