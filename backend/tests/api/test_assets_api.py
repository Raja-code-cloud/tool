"""Asset API automation tests."""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient

from tests.fixtures.app import bound_principal, workspace_headers
from tests.fixtures.constants import SAMPLE_WEBP_BYTES

pytestmark = pytest.mark.api


@pytest.mark.asyncio
async def test_list_assets_returns_paged_collection(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get("/api/v1/assets", headers=workspace_headers())

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["data"], list)
    assert "page" in body["meta"]


@pytest.mark.asyncio
async def test_get_asset_returns_etag(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            f"/api/v1/assets/{uuid4()}",
            headers=workspace_headers(),
        )

    assert response.status_code == 200
    assert response.headers["etag"] == '"1"'


@pytest.mark.asyncio
async def test_upload_asset_returns_accepted(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.post(
            "/api/v1/assets/upload",
            headers=workspace_headers(extra={"Idempotency-Key": "api-upload-001"}),
            data={"assetType": "poster", "title": "API Poster"},
            files={"file": ("poster.webp", SAMPLE_WEBP_BYTES, "image/webp")},
        )

    assert response.status_code == 202
    assert response.json()["data"]["type"] == "upload"


@pytest.mark.asyncio
async def test_search_assets_endpoint(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            "/api/v1/assets/search",
            headers=workspace_headers(),
            params={"q": "launch"},
        )

    assert response.status_code == 200
