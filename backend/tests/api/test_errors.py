"""Validate stable error codes and RFC 9457 problem details."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.fixtures.app import bound_principal, workspace_headers
from tests.fixtures.problem import assert_problem_response

pytestmark = pytest.mark.api


@pytest.mark.asyncio
async def test_delete_asset_requires_if_match(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.delete(
            "/api/v1/assets/01900000-0000-7000-8000-000000000099",
            headers=workspace_headers(),
        )

    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")
    assert_problem_response(response.json(), status=422, code="validation_failed")


@pytest.mark.asyncio
async def test_invalid_uuid_path_returns_validation_failed(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            "/api/v1/assets/not-a-uuid",
            headers=workspace_headers(),
        )

    assert response.status_code == 422
    assert_problem_response(response.json(), status=422, code="validation_failed")


@pytest.mark.asyncio
async def test_malformed_json_returns_validation_failed(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.post(
            "/api/v1/publish",
            headers={
                **workspace_headers(extra={"Idempotency-Key": "bad-json-001"}),
                "Content-Type": "application/json",
            },
            content=b"{invalid",
        )

    assert response.status_code in {400, 422}
    assert response.headers["content-type"].startswith("application/problem+json")
