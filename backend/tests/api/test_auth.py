"""Validate authentication and authorization on API routes."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.fixtures.app import bound_principal, workspace_headers

pytestmark = pytest.mark.api


@pytest.mark.asyncio
async def test_health_routes_are_public(api_client: AsyncClient) -> None:
    for path in ("/health", "/live", "/ready"):
        response = await api_client.get(path)
        assert response.status_code == 200
        assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_assets_read_requires_permission(api_client: AsyncClient) -> None:
    async with bound_principal(permissions=frozenset({"content:read"})):
        response = await api_client.get("/api/v1/assets", headers=workspace_headers())

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "permission_denied"


@pytest.mark.asyncio
async def test_assets_write_required_for_upload(api_client: AsyncClient) -> None:
    async with bound_principal(permissions=frozenset({"assets:read"})):
        response = await api_client.post(
            "/api/v1/assets/upload",
            headers=workspace_headers(extra={"Idempotency-Key": "auth-upload-001"}),
            data={"assetType": "poster", "title": "Denied"},
            files={"file": ("poster.webp", b"RIFF", "image/webp")},
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_routes_require_admin_read(api_client: AsyncClient) -> None:
    async with bound_principal(permissions=frozenset({"assets:read"})):
        response = await api_client.get("/api/v1/admin/system", headers=workspace_headers())

    assert response.status_code == 403
