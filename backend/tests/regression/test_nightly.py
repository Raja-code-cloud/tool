"""Nightly regression pack — extended coverage marked slow."""

from __future__ import annotations

from uuid import uuid4

import pytest
from httpx import AsyncClient

from tests.fixtures.app import bound_principal, workspace_headers

pytestmark = [pytest.mark.regression, pytest.mark.nightly, pytest.mark.slow]


@pytest.mark.asyncio
async def test_all_health_probes(api_client: AsyncClient) -> None:
    for path in ("/health", "/live", "/ready"):
        response = await api_client.get(path)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_administration_full_surface(api_client: AsyncClient) -> None:
    async with bound_principal():
        for path in (
            "/api/v1/admin/jobs",
            "/api/v1/admin/queues",
            "/api/v1/admin/providers",
            "/api/v1/admin/system",
        ):
            response = await api_client.get(path, headers=workspace_headers())
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_analytics_detail_endpoints(api_client: AsyncClient) -> None:
    async with bound_principal():
        posts = await api_client.get("/api/v1/analytics/posts", headers=workspace_headers())
        assert posts.status_code == 200

        post = await api_client.get(
            f"/api/v1/analytics/post/{uuid4()}",
            headers=workspace_headers(),
        )
        assert post.status_code == 200
