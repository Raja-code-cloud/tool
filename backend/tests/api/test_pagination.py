"""Validate pagination, filtering, and sorting query contracts."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.fixtures.app import bound_principal, workspace_headers

pytestmark = pytest.mark.api


@pytest.mark.asyncio
async def test_list_assets_accepts_limit_parameter(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            "/api/v1/assets",
            headers=workspace_headers(),
            params={"limit": 10},
        )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_generate_content_rejects_invalid_scope(api_client: AsyncClient) -> None:
    from uuid import uuid4

    async with bound_principal():
        response = await api_client.post(
            "/api/v1/content/generate",
            headers=workspace_headers(extra={"Idempotency-Key": "pag-invalid-scope-001"}),
            json={
                "assetId": str(uuid4()),
                "sourceVersionId": str(uuid4()),
                "modelId": str(uuid4()),
                "scope": "not-a-valid-scope",
            },
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
