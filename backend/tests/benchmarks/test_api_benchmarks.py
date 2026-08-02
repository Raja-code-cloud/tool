"""HTTP API micro-benchmarks using pytest-benchmark."""

from __future__ import annotations

from typing import Any

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.benchmark


def test_benchmark_health_endpoint(benchmark: Any, sync_client: Any) -> None:
    def run() -> None:
        response = sync_client.get("/health")
        assert response.status_code == 200

    benchmark(run)


def test_benchmark_liveness_probe(benchmark: Any, sync_client: Any) -> None:
    def run() -> None:
        response = sync_client.get("/live")
        assert response.status_code == 200

    benchmark(run)


@pytest.mark.asyncio
async def test_benchmark_list_assets(
    benchmark: Any,
    benchmark_client: AsyncClient,
    perf_headers: dict[str, str],
    principal_token: object,
) -> None:
    _ = principal_token

    async def run() -> None:
        response = await benchmark_client.get("/api/v1/assets", headers=perf_headers)
        assert response.status_code == 200

    await benchmark.pedantic(run, rounds=10, iterations=1)


@pytest.mark.asyncio
async def test_benchmark_get_asset(
    benchmark: Any,
    benchmark_client: AsyncClient,
    perf_headers: dict[str, str],
    principal_token: object,
) -> None:
    from uuid import uuid4

    _ = principal_token
    asset_id = uuid4()

    async def run() -> None:
        response = await benchmark_client.get(
            f"/api/v1/assets/{asset_id}",
            headers=perf_headers,
        )
        assert response.status_code == 200

    await benchmark.pedantic(run, rounds=10, iterations=1)


@pytest.mark.asyncio
async def test_benchmark_search_assets(
    benchmark: Any,
    benchmark_client: AsyncClient,
    perf_headers: dict[str, str],
    principal_token: object,
) -> None:
    _ = principal_token

    async def run() -> None:
        response = await benchmark_client.get(
            "/api/v1/assets/search?q=perf",
            headers=perf_headers,
        )
        assert response.status_code == 200

    await benchmark.pedantic(run, rounds=10, iterations=1)


@pytest.mark.asyncio
async def test_benchmark_analytics_dashboard(
    benchmark: Any,
    benchmark_client: AsyncClient,
    perf_headers: dict[str, str],
    principal_token: object,
) -> None:
    _ = principal_token

    async def run() -> None:
        response = await benchmark_client.get(
            "/api/v1/analytics/dashboard",
            headers=perf_headers,
        )
        assert response.status_code == 200

    await benchmark.pedantic(run, rounds=10, iterations=1)


def test_benchmark_pagination_encode(benchmark: Any) -> None:
    from cloud_content_hub.api.pagination import encode_cursor

    def run() -> None:
        encode_cursor({"updated_at": "2026-08-02T10:00:00Z", "id": "01900000-0000-7000-8000-000000000001"})

    benchmark(run)


def test_benchmark_pagination_decode(benchmark: Any) -> None:
    from cloud_content_hub.api.pagination import decode_cursor, encode_cursor

    token = encode_cursor({"updated_at": "2026-08-02T10:00:00Z", "id": "01900000-0000-7000-8000-000000000001"})

    def run() -> None:
        decoded = decode_cursor(token)
        assert "id" in decoded

    benchmark(run)
