"""Notifications and administration API automation tests."""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient

from tests.fixtures.app import bound_principal, workspace_headers

pytestmark = pytest.mark.api


@pytest.mark.asyncio
async def test_list_notifications(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            "/api/v1/notifications",
            headers=workspace_headers(),
        )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_mark_notification_read(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.patch(
            f"/api/v1/notifications/{uuid4()}/read",
            headers=workspace_headers(extra={"If-Match": "1"}),
        )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_system_status(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            "/api/v1/admin/system",
            headers=workspace_headers(),
        )

    assert response.status_code == 200
    assert response.json()["data"]["status"] in {"healthy", "degraded"}


@pytest.mark.asyncio
async def test_admin_jobs(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            "/api/v1/admin/jobs",
            headers=workspace_headers(),
        )

    assert response.status_code == 200
