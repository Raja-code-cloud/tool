"""Release validation for health probe routes and behavior."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from cloud_content_hub.api.errors import install_exception_handlers
from helpers.import_utils import load_module_from_file

pytestmark = pytest.mark.release

_health_module = load_module_from_file(
    "release_health_router",
    "api/routers/v1/health.py",
)
health_router = _health_module.router

IMPLEMENTED_LIVENESS_PATH = "/live"
IMPLEMENTED_READINESS_PATH = "/ready"
IMPLEMENTED_SUMMARY_PATH = "/health"


@pytest.fixture
async def health_client() -> AsyncClient:
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
    container.database_engine.connect.return_value = connect_cm
    container.redis.ping = AsyncMock()

    app.state.container = container
    install_exception_handlers(app)
    app.include_router(health_router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_liveness_does_not_require_dependencies(health_client: AsyncClient) -> None:
    response = await health_client.get(IMPLEMENTED_LIVENESS_PATH)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "live"


@pytest.mark.asyncio
async def test_readiness_returns_ok_when_dependencies_available(
    health_client: AsyncClient,
) -> None:
    response = await health_client.get(IMPLEMENTED_READINESS_PATH)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ready"


@pytest.mark.asyncio
async def test_readiness_returns_unavailable_when_database_fails(
    health_client: AsyncClient,
) -> None:
    health_client.app.state.container.database_engine.connect.side_effect = OSError(  # type: ignore[attr-defined]
        "connection refused"
    )
    response = await health_client.get(IMPLEMENTED_READINESS_PATH)
    assert response.status_code == 503
    body = response.json()
    assert body["success"] is False


@pytest.mark.asyncio
async def test_health_summary_returns_version(health_client: AsyncClient) -> None:
    response = await health_client.get(IMPLEMENTED_SUMMARY_PATH)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"
    assert body["data"]["version"] == "1.0.0-rc"


def test_implemented_probe_paths_are_documented() -> None:
    """Release docs and deployment infra must align with these paths."""
    assert IMPLEMENTED_LIVENESS_PATH == "/live"
    assert IMPLEMENTED_READINESS_PATH == "/ready"
    assert IMPLEMENTED_SUMMARY_PATH == "/health"
