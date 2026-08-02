"""Validate the public v1 success and failure envelopes."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.fixtures.app import bound_principal, workspace_headers
from tests.fixtures.problem import assert_problem_response, assert_success_envelope

pytestmark = pytest.mark.api


@pytest.mark.asyncio
async def test_list_assets_returns_success_envelope(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get("/api/v1/assets", headers=workspace_headers())

    assert response.status_code == 200
    assert_success_envelope(response.json(), message="Assets retrieved.")


@pytest.mark.asyncio
async def test_missing_workspace_returns_problem_envelope(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            "/api/v1/assets",
            headers={"Authorization": "Bearer token"},
        )

    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")
    assert_problem_response(response.json(), status=422, code="validation_failed")
