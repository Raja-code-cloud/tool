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
    response = await api_client.get("/health/live")
    assert response.json()["data"]["status"] == "live"


@pytest.mark.asyncio
async def test_readiness_reports_ready(api_client: AsyncClient) -> None:
    response = await api_client.get("/health/ready")
    assert response.json()["data"]["status"] == "ready"


@pytest.mark.asyncio
async def test_legacy_liveness_alias_reports_live(api_client: AsyncClient) -> None:
    response = await api_client.get("/live")
    assert response.json()["data"]["status"] == "live"


@pytest.mark.asyncio
async def test_legacy_readiness_alias_reports_ready(api_client: AsyncClient) -> None:
    response = await api_client.get("/ready")
    assert response.json()["data"]["status"] == "ready"


@pytest.mark.asyncio
async def test_liveness_alias_matches_canonical(api_client: AsyncClient) -> None:
    canonical = await api_client.get("/health/live")
    legacy = await api_client.get("/live")
    assert canonical.status_code == legacy.status_code
    assert canonical.json() == legacy.json()


@pytest.mark.asyncio
async def test_readiness_alias_matches_canonical(api_client: AsyncClient) -> None:
    canonical = await api_client.get("/health/ready")
    legacy = await api_client.get("/ready")
    assert canonical.status_code == legacy.status_code
    assert canonical.json() == legacy.json()


@pytest.mark.asyncio
async def test_openapi_exposes_canonical_probe_paths_only(api_client: AsyncClient) -> None:
    response = await api_client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert "/health/live" in paths
    assert "/health/ready" in paths
    assert "/live" not in paths
    assert "/ready" not in paths
