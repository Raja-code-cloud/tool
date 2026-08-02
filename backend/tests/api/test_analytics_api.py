"""Analytics API automation tests."""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient

from tests.fixtures.app import bound_principal, workspace_headers

pytestmark = pytest.mark.api


@pytest.mark.asyncio
async def test_analytics_dashboard(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            "/api/v1/analytics/dashboard",
            headers=workspace_headers(),
        )

    assert response.status_code == 200
    data = response.json()["data"]
    assert "metrics" in data


@pytest.mark.asyncio
async def test_list_analytics_posts(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            "/api/v1/analytics/posts",
            headers=workspace_headers(),
        )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_analytics_post(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            f"/api/v1/analytics/post/{uuid4()}",
            headers=workspace_headers(),
        )

    assert response.status_code == 200
