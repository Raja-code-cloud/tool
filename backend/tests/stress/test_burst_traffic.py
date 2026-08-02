"""Burst traffic stress validation."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.performance.helpers.http import ANALYTICS_QUERY
from tests.performance.helpers.metrics import run_concurrent

pytestmark = [pytest.mark.stress, pytest.mark.performance]


@pytest.mark.asyncio
async def test_burst_concurrent_api_reads(
    perf_client: AsyncClient,
    perf_headers: dict[str, str],
    principal_token: object,
) -> None:
    _ = principal_token
    paths = (
        "/api/v1/assets",
        "/api/v1/content",
        f"/api/v1/analytics/dashboard?{ANALYTICS_QUERY}",
        "/api/v1/notifications",
    )
    index = {"value": 0}

    async def burst_read() -> None:
        path = paths[index["value"] % len(paths)]
        index["value"] += 1
        response = await perf_client.get(path, headers=perf_headers)
        assert response.status_code == 200

    stats = await run_concurrent(
        concurrency=50,
        per_worker=4,
        warmup=10,
        operation=burst_read,
    )
    assert stats.count == 200
    assert stats.p99 < 5.0, f"Burst read P99 {stats.p99 * 1000:.1f}ms exceeds 5000ms"
