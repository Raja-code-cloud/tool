"""Simulated load scenarios runnable via pytest (no external Locust/k6 required)."""

from __future__ import annotations

import time

import pytest
from httpx import AsyncClient

from tests.performance.helpers.metrics import LatencyStats, run_concurrent

pytestmark = [pytest.mark.load, pytest.mark.performance]


@pytest.mark.asyncio
@pytest.mark.parametrize("concurrency", [1, 10, 100])
async def test_simulated_concurrent_asset_listing(
    perf_client: AsyncClient,
    perf_headers: dict[str, str],
    principal_token: object,
    concurrency: int,
) -> None:
    _ = principal_token

    async def list_assets() -> None:
        response = await perf_client.get("/api/v1/assets", headers=perf_headers)
        assert response.status_code == 200

    start = time.perf_counter()
    stats = await run_concurrent(
        concurrency=concurrency,
        per_worker=5,
        warmup=10,
        operation=list_assets,
    )
    elapsed = time.perf_counter() - start
    threshold = 2.0 if concurrency < 100 else 10.0
    _report_load_stats(stats, elapsed, label=f"list_assets x{concurrency}", threshold=threshold)


@pytest.mark.asyncio
async def test_simulated_burst_health_probes(perf_client: AsyncClient) -> None:
    async def health_probe() -> None:
        response = await perf_client.get("/health")
        assert response.status_code == 200

    stats = await run_concurrent(
        concurrency=100,
        per_worker=3,
        operation=health_probe,
    )
    assert stats.p95 < 1.0, f"Burst health P95 {stats.p95 * 1000:.1f}ms exceeds 1000ms"


def _report_load_stats(
    stats: LatencyStats,
    elapsed: float,
    *,
    label: str,
    threshold: float = 2.0,
) -> None:
    rps = stats.requests_per_second(wall_seconds=elapsed)
    assert stats.p95 < threshold, (
        f"{label}: P95 {stats.p95 * 1000:.1f}ms, RPS {rps:.1f}, samples={stats.count}"
    )
