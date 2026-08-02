"""Negative regression tests — auth, permissions, and invalid payloads."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.fixtures.app import bound_principal, workspace_headers
from tests.fixtures.problem import assert_problem_response

pytestmark = pytest.mark.regression


@pytest.mark.asyncio
async def test_unauthenticated_request_rejected(api_client: AsyncClient) -> None:
    response = await api_client.get(
        "/api/v1/assets",
        headers=workspace_headers(),
    )

    assert response.status_code == 401
    assert_problem_response(response.json(), status=401)


@pytest.mark.asyncio
async def test_missing_workspace_header_rejected(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            "/api/v1/assets",
            headers={"Authorization": "Bearer token"},
        )

    assert response.status_code == 422
    assert_problem_response(response.json(), status=422, code="validation_failed")


@pytest.mark.asyncio
async def test_missing_permissions_denied(api_client: AsyncClient) -> None:
    async with bound_principal(permissions=frozenset({"profile:read"})):
        response = await api_client.get("/api/v1/assets", headers=workspace_headers())

    assert response.status_code == 403
    assert_problem_response(response.json(), status=403, code="permission_denied")


@pytest.mark.asyncio
async def test_invalid_payload_rejected(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.post(
            "/api/v1/schedule",
            headers=workspace_headers(extra={"Idempotency-Key": "negative-schedule-001"}),
            json={"timeZone": "UTC"},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_upload_without_idempotency_key_rejected(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.post(
            "/api/v1/assets/upload",
            headers=workspace_headers(),
            data={"assetType": "poster", "title": "No Key"},
            files={"file": ("poster.webp", b"data", "image/webp")},
        )

    assert response.status_code == 422
