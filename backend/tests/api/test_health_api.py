"""Health endpoint API automation."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.api


@pytest.mark.asyncio
async def test_health_reports_version(api_client: AsyncClient) -> None:
    response = await api_client.get("/health")
    body = response.json()
    assert body["data"]["status"] == "healthy"
    assert body["data"]["version"]


@pytest.mark.asyncio
async def test_liveness_reports_live(api_client: AsyncClient) -> None:
    response = await api_client.get("/live")
    assert response.json()["data"]["status"] == "live"


@pytest.mark.asyncio
async def test_readiness_reports_ready(api_client: AsyncClient) -> None:
    response = await api_client.get("/ready")
    assert response.json()["data"]["status"] == "ready"
