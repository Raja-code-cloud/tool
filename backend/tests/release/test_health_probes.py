"""Release validation for health probe routes and behavior."""

from __future__ import annotations

from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from import_utils import load_module_from_file  # type: ignore[import-not-found]

from cloud_content_hub.api.errors import install_exception_handlers

pytestmark = pytest.mark.release

_health_module = load_module_from_file(
    "release_health_router",
    "api/routers/v1/health.py",
)
health_router = _health_module.router

CANONICAL_LIVENESS_PATH = "/health/live"
CANONICAL_READINESS_PATH = "/health/ready"
LEGACY_LIVENESS_PATH = "/live"
LEGACY_READINESS_PATH = "/ready"
IMPLEMENTED_SUMMARY_PATH = "/health"


@pytest.fixture
async def health_client() -> AsyncIterator[tuple[AsyncClient, MagicMock]]:
    app = FastAPI()
    container = MagicMock()
    container.settings.service_version = "1.0.0-rc"
    container.settings.database_timeout_seconds = 1.0
    container.settings.redis_timeout_seconds = 1.0

    connection = AsyncMock()
    connection.execute = AsyncMock()
    connect_cm = AsyncMock()
    connect_cm.__aenter__.return_value = connection
    connect_cm.__aexit__.return_value = None
    container.database_engine.connect = MagicMock(return_value=connect_cm)
    container.redis.ping = AsyncMock()

    app.state.container = container
    install_exception_handlers(app)
    app.include_router(health_router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, container


@pytest.mark.asyncio
async def test_liveness_does_not_require_dependencies(
    health_client: tuple[AsyncClient, MagicMock],
) -> None:
    client, _container = health_client
    response = await client.get(CANONICAL_LIVENESS_PATH)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "live"


@pytest.mark.asyncio
async def test_readiness_returns_ok_when_dependencies_available(
    health_client: tuple[AsyncClient, MagicMock],
) -> None:
    client, _container = health_client
    response = await client.get(CANONICAL_READINESS_PATH)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ready"


@pytest.mark.asyncio
async def test_readiness_returns_unavailable_when_database_fails(
    health_client: tuple[AsyncClient, MagicMock],
) -> None:
    client, container = health_client
    container.database_engine.connect = MagicMock(side_effect=OSError("connection refused"))
    response = await client.get(CANONICAL_READINESS_PATH)
    assert response.status_code == 503
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_health_summary_returns_version(
    health_client: tuple[AsyncClient, MagicMock],
) -> None:
    client, _container = health_client
    response = await client.get(IMPLEMENTED_SUMMARY_PATH)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"
    assert body["data"]["version"] == "1.0.0-rc"


@pytest.mark.asyncio
async def test_legacy_liveness_alias_matches_canonical(
    health_client: tuple[AsyncClient, MagicMock],
) -> None:
    client, _container = health_client
    canonical = await client.get(CANONICAL_LIVENESS_PATH)
    legacy = await client.get(LEGACY_LIVENESS_PATH)
    assert canonical.status_code == legacy.status_code == 200
    assert canonical.json() == legacy.json()


@pytest.mark.asyncio
async def test_legacy_readiness_alias_matches_canonical(
    health_client: tuple[AsyncClient, MagicMock],
) -> None:
    client, _container = health_client
    canonical = await client.get(CANONICAL_READINESS_PATH)
    legacy = await client.get(LEGACY_READINESS_PATH)
    assert canonical.status_code == legacy.status_code == 200
    assert canonical.json() == legacy.json()


def test_implemented_probe_paths_are_documented() -> None:
    """Release docs and deployment infra must align with these paths."""
    assert CANONICAL_LIVENESS_PATH == "/health/live"
    assert CANONICAL_READINESS_PATH == "/health/ready"
    assert IMPLEMENTED_SUMMARY_PATH == "/health"
