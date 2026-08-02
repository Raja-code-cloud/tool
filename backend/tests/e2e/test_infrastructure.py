"""Infrastructure smoke tests for the end-to-end environment."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

pytestmark = pytest.mark.e2e


@pytest.mark.asyncio
async def test_health_endpoints_return_success(e2e_app) -> None:
    """Health, liveness, and readiness endpoints respond successfully."""

    transport = ASGITransport(app=e2e_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        health = await client.get("/health")
        live = await client.get("/live")
        ready = await client.get("/ready")

    assert health.status_code == 200
    assert live.status_code == 200
    assert ready.status_code == 200
    assert health.json()["data"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_handler_registry_is_fully_wired(e2e_container) -> None:
    """Core workflow handlers are registered in the composition root."""

    from cloud_content_hub.bootstrap.handlers import wire_handlers

    registry = wire_handlers(e2e_container)
    required = (
        "upload_asset",
        "generate_content",
        "create_publication",
        "dispatch_publication",
        "create_schedule",
        "get_analytics_dashboard",
        "list_notifications",
        "get_admin_system_status",
    )
    for name in required:
        assert registry.resolve(name) is not None


@pytest.mark.asyncio
async def test_postgres_redis_and_storage_are_reachable(e2e_container) -> None:
    """PostgreSQL, Redis, and storage providers are reachable in the E2E stack."""

    from sqlalchemy import text

    async with e2e_container.database_engine.connect() as connection:
        await connection.execute(text("SELECT 1"))

    assert await e2e_container.redis.ping() is True
    health = await e2e_container.storage_provider.health_check()
    assert health.healthy is True
