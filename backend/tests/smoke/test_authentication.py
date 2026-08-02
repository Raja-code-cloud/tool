"""Smoke tests for authentication and public health endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.smoke


@pytest.mark.asyncio
async def test_health_is_public_without_auth(health_client: AsyncClient) -> None:
    response = await health_client.get("/health")
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_liveness_is_public(health_client: AsyncClient) -> None:
    response = await health_client.get("/live")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_protected_route_rejects_anonymous(local_client: AsyncClient) -> None:
    response = await local_client.get(
        "/api/v1/assets",
        headers={"X-Workspace-ID": "01900000-0000-7000-8000-000000000001"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_authenticated_asset_list_succeeds(
    local_client: AsyncClient,
    bind_admin: None,
) -> None:
    response = await local_client.get(
        "/api/v1/assets",
        headers={
            "Authorization": "Bearer smoke-token",
            "X-Workspace-ID": "01900000-0000-7000-8000-000000000001",
        },
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
@pytest.mark.external
async def test_external_liveness_when_configured(external_client: AsyncClient) -> None:
    for path in ("/live", "/health/live"):
        response = await external_client.get(path)
        if response.status_code == 200:
            return
    pytest.fail("Neither /live nor /health/live returned 200")


@pytest.mark.asyncio
@pytest.mark.external
async def test_external_readiness_when_configured(external_client: AsyncClient) -> None:
    for path in ("/ready", "/health/ready"):
        response = await external_client.get(path)
        if response.status_code == 200:
            return
    pytest.fail("Neither /ready nor /health/ready returned 200")
