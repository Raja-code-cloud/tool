"""Smoke tests for core API surface areas."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from uuid import UUID

pytestmark = pytest.mark.smoke

WORKSPACE_ID = UUID("01900000-0000-7000-8000-000000000001")

HEADERS = {
    "Authorization": "Bearer smoke-token",
    "X-Workspace-ID": str(WORKSPACE_ID),
}


@pytest.mark.asyncio
async def test_asset_list(local_client: AsyncClient, bind_admin: None) -> None:
    response = await local_client.get("/api/v1/assets", headers=HEADERS)
    assert response.status_code == 200
    assert response.json()["message"] == "Assets retrieved."


@pytest.mark.asyncio
async def test_content_list(local_client: AsyncClient, bind_admin: None) -> None:
    response = await local_client.get("/api/v1/content", headers=HEADERS)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_publishing_history(local_client: AsyncClient, bind_admin: None) -> None:
    response = await local_client.get("/api/v1/publish/history", headers=HEADERS)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_scheduler_list(local_client: AsyncClient, bind_admin: None) -> None:
    response = await local_client.get("/api/v1/schedule", headers=HEADERS)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_analytics_dashboard(local_client: AsyncClient, bind_admin: None) -> None:
    response = await local_client.get("/api/v1/analytics/dashboard", headers=HEADERS)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_notifications_list(local_client: AsyncClient, bind_admin: None) -> None:
    response = await local_client.get("/api/v1/notifications", headers=HEADERS)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_administration_system_status(local_client: AsyncClient, bind_admin: None) -> None:
    response = await local_client.get("/api/v1/admin/system", headers=HEADERS)
    assert response.status_code == 200


@pytest.mark.asyncio
@pytest.mark.external
async def test_external_health_summary(external_client: AsyncClient) -> None:
    response = await external_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body.get("success") is True or body.get("status") == "healthy"
