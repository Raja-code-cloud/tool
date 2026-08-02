"""Contract tests for stable error codes documented in ERROR_CODES.md."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.fixtures.app import bound_principal, workspace_headers

pytestmark = pytest.mark.contract

DOCUMENTED_CODES = {
    401: {"authentication_required"},
    403: {"permission_denied"},
    422: {"validation_failed"},
}


@pytest.mark.asyncio
async def test_authentication_required_code(api_client: AsyncClient) -> None:
    response = await api_client.get("/api/v1/assets", headers=workspace_headers())
    body = response.json()
    assert body["error"]["code"] in DOCUMENTED_CODES[401]


@pytest.mark.asyncio
async def test_permission_denied_code(api_client: AsyncClient) -> None:
    async with bound_principal(permissions=frozenset({"profile:read"})):
        response = await api_client.get("/api/v1/assets", headers=workspace_headers())
    body = response.json()
    assert body["error"]["code"] in DOCUMENTED_CODES[403]


@pytest.mark.asyncio
async def test_validation_failed_code(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            "/api/v1/assets",
            headers={"Authorization": "Bearer token"},
        )
    body = response.json()
    assert body["error"]["code"] in DOCUMENTED_CODES[422]
