"""Contract tests for the public API envelope and error shapes."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.fixtures.app import bound_principal, workspace_headers
from tests.fixtures.problem import assert_problem_response, assert_success_envelope

pytestmark = pytest.mark.contract


@pytest.mark.asyncio
async def test_success_envelope_contract(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get("/api/v1/assets", headers=workspace_headers())

    body = response.json()
    assert_success_envelope(body)
    assert isinstance(body["data"], list)
    assert set(body["meta"]["page"].keys()) == {"nextCursor", "hasMore", "limit"}


@pytest.mark.asyncio
async def test_problem_details_contract(api_client: AsyncClient) -> None:
    async with bound_principal():
        response = await api_client.get(
            "/api/v1/assets",
            headers={"Authorization": "Bearer token"},
        )

    assert response.headers["content-type"].startswith("application/problem+json")
    assert_problem_response(response.json(), status=422, code="validation_failed")


@pytest.mark.asyncio
async def test_health_probe_contract(api_client: AsyncClient) -> None:
    response = await api_client.get("/health")
    body = response.json()
    assert_success_envelope(body)
    assert body["data"]["status"] in {"healthy", "degraded"}
