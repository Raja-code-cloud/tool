"""Validate pagination, filtering, and sorting query contracts."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.fixtures.app import bound_principal, workspace_headers

pytestmark = pytest.mark.api


@pytest.mark.asyncio
async def test_list_assets_honors_limit(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            "/api/v1/assets",
            headers=workspace_headers(),
            params={"limit": 10},
        )

    assert response.status_code == 200
    page = response.json()["meta"]["page"]
    assert page["limit"] == 10


@pytest.mark.asyncio
async def test_list_assets_rejects_unknown_query_field(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            "/api/v1/assets",
            headers=workspace_headers(),
            params={"unknownFilter": "value"},
        )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_failed"


@pytest.mark.asyncio
async def test_list_assets_accepts_sort_parameter(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            "/api/v1/assets",
            headers=workspace_headers(),
            params={"sort": "-updatedAt"},
        )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_list_schedules_accepts_state_filter(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            "/api/v1/schedule",
            headers=workspace_headers(),
            params={"state": "scheduled"},
        )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_publication_history_supports_occurred_range(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            "/api/v1/publish/history",
            headers=workspace_headers(),
            params={
                "occurredAfter": "2026-08-01T00:00:00Z",
                "occurredBefore": "2026-08-03T00:00:00Z",
            },
        )

    assert response.status_code == 200
