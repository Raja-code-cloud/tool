"""Validate container recovery via health probes."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, MagicMock

from cloud_content_hub.api.routers.v1.health import router as health_router


@pytest.mark.asyncio
async def test_container_liveness_probe_succeeds_without_container_state() -> None:
    """Liveness must pass when only the process is running (ACA restart signal)."""

    app = FastAPI()
    app.include_router(health_router)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/live")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_container_readiness_probe_requires_database_and_redis() -> None:
    container = MagicMock()
    connection = AsyncMock()
    connection.execute = AsyncMock(return_value=None)
    connect_cm = AsyncMock()
    connect_cm.__aenter__.return_value = connection
    connect_cm.__aexit__.return_value = None
    container.database_engine.connect.return_value = connect_cm
    container.redis.ping = AsyncMock(return_value=True)
    container.settings.database_timeout_seconds = 2.0
    container.settings.redis_timeout_seconds = 2.0

    app = FastAPI()
    app.include_router(health_router)
    app.state.container = container

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/ready")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["status"] == "ready"


@pytest.mark.asyncio
async def test_container_summary_health_returns_version() -> None:
    container = MagicMock()
    container.settings.service_version = "0.1.0"

    app = FastAPI()
    app.include_router(health_router)
    app.state.container = container

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["version"] == "0.1.0"


def test_implemented_probe_routes_match_release_checklist() -> None:
    """Documented application routes used for recovery verification."""

    expected_routes = frozenset({"/live", "/ready", "/health"})
    route_paths = frozenset(route.path for route in health_router.routes)

    assert expected_routes.issubset(route_paths)
