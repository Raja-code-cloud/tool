"""Content API automation tests."""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient

from tests.fixtures.app import bound_principal, workspace_headers

pytestmark = pytest.mark.api


@pytest.mark.asyncio
async def test_list_content(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get("/api/v1/content", headers=workspace_headers())

    assert response.status_code == 200
    assert response.json()["message"] == "Content retrieved."


@pytest.mark.asyncio
async def test_get_content_returns_version(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            f"/api/v1/content/{uuid4()}",
            headers=workspace_headers(),
        )

    assert response.status_code == 200
    assert response.json()["data"]["version"] == 1


@pytest.mark.asyncio
async def test_generate_content_returns_operation(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.post(
            "/api/v1/content/generate",
            headers=workspace_headers(extra={"Idempotency-Key": "api-generate-001"}),
            json={
                "assetId": str(uuid4()),
                "sourceVersionId": str(uuid4()),
                "modelId": str(uuid4()),
                "scope": "whole",
            },
        )

    assert response.status_code == 202
    assert response.json()["data"]["type"] == "generation"
