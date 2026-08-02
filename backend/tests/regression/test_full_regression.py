"""Full regression pack — module coverage across all API domains."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.fixtures.app import bound_principal, workspace_headers

pytestmark = pytest.mark.regression


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("GET", "/api/v1/assets"),
        ("GET", "/api/v1/assets/search"),
        ("GET", "/api/v1/content"),
        ("GET", "/api/v1/publish/history"),
        ("GET", "/api/v1/schedule"),
        ("GET", "/api/v1/analytics/dashboard"),
        ("GET", "/api/v1/analytics/posts"),
        ("GET", "/api/v1/analytics/platforms"),
        ("GET", "/api/v1/notifications"),
        ("GET", "/api/v1/admin/jobs"),
        ("GET", "/api/v1/admin/queues"),
        ("GET", "/api/v1/admin/providers"),
        ("GET", "/api/v1/admin/system"),
    ],
)
async def test_read_routes_regression(api_client: AsyncClient, method: str, path: str) -> None:
    async with bound_principal():
        response = await api_client.request(method, path, headers=workspace_headers())
    assert response.status_code == 200
    assert response.json()["success"] is True
