"""Full regression pack — module coverage across all API domains."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.fixtures.app import analytics_period_params, bound_principal, workspace_headers

pytestmark = pytest.mark.regression


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method", "path", "params"),
    [
        ("GET", "/api/v1/assets", None),
        ("GET", "/api/v1/assets/search", {"q": "launch"}),
        ("GET", "/api/v1/content", None),
        ("GET", "/api/v1/publish/history", None),
        ("GET", "/api/v1/schedule", None),
        ("GET", "/api/v1/analytics/dashboard", analytics_period_params()),
        ("GET", "/api/v1/analytics/posts", None),
        ("GET", "/api/v1/analytics/platforms", analytics_period_params()),
        ("GET", "/api/v1/notifications", None),
        ("GET", "/api/v1/admin/jobs", None),
        ("GET", "/api/v1/admin/queues", None),
        ("GET", "/api/v1/admin/providers", None),
        ("GET", "/api/v1/admin/system", None),
    ],
)
async def test_read_routes_regression(
    api_client: AsyncClient,
    method: str,
    path: str,
    params: dict[str, str] | None,
) -> None:
    async with bound_principal():
        response = await api_client.request(
            method,
            path,
            headers=workspace_headers(),
            params=params,
        )
    assert response.status_code == 200
    assert response.json()["success"] is True
