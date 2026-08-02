"""Smoke regression pack — fast PR validation."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.fixtures.app import analytics_period_params, bound_principal, workspace_headers

pytestmark = [pytest.mark.regression, pytest.mark.smoke]


@pytest.mark.asyncio
async def test_health_smoke(api_client: AsyncClient) -> None:
    response = await api_client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_assets_smoke(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get("/api/v1/assets", headers=workspace_headers())
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_content_smoke(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get("/api/v1/content", headers=workspace_headers())
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_publishing_smoke(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get("/api/v1/publish/history", headers=workspace_headers())
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_scheduler_smoke(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get("/api/v1/schedule", headers=workspace_headers())
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_analytics_smoke(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            "/api/v1/analytics/dashboard",
            headers=workspace_headers(),
            params=analytics_period_params(),
        )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_notifications_smoke(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get("/api/v1/notifications", headers=workspace_headers())
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_administration_smoke(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get("/api/v1/admin/system", headers=workspace_headers())
    assert response.status_code == 200
