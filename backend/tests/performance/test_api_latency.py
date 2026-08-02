"""API endpoint latency validation across delivery-layer hot paths."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from tests.performance.helpers.metrics import collect_latencies, run_concurrent
from tests.performance.helpers.targets import PERFORMANCE_TARGETS, assert_within_target

pytestmark = pytest.mark.performance


@pytest.mark.asyncio
async def test_health_endpoint_latency(perf_client: AsyncClient) -> None:
    stats = await collect_latencies(
        label="GET /health",
        iterations=50,
        operation=lambda: _get(perf_client, "/health"),
    )
    assert_within_target(stats, p95_seconds=0.050, label="health")


@pytest.mark.asyncio
async def test_list_assets_crud_latency(
    perf_client: AsyncClient,
    perf_headers: dict[str, str],
    principal_token: object,
) -> None:
    _ = principal_token
    stats = await collect_latencies(
        label="GET /api/v1/assets",
        iterations=50,
        operation=lambda: _get(perf_client, "/api/v1/assets", headers=perf_headers),
    )
    assert_within_target(stats, p95_seconds=PERFORMANCE_TARGETS.api_crud_p95_seconds)


@pytest.mark.asyncio
async def test_get_asset_crud_latency(
    perf_client: AsyncClient,
    perf_headers: dict[str, str],
    principal_token: object,
) -> None:
    from uuid import uuid4

    _ = principal_token
    asset_id = uuid4()
    stats = await collect_latencies(
        label="GET /api/v1/assets/{id}",
        iterations=50,
        operation=lambda: _get(
            perf_client,
            f"/api/v1/assets/{asset_id}",
            headers=perf_headers,
        ),
    )
    assert_within_target(stats, p95_seconds=PERFORMANCE_TARGETS.api_crud_p95_seconds)


@pytest.mark.asyncio
async def test_search_assets_latency(
    perf_client: AsyncClient,
    perf_headers: dict[str, str],
    principal_token: object,
) -> None:
    _ = principal_token
    stats = await collect_latencies(
        label="GET /api/v1/assets/search",
        iterations=50,
        operation=lambda: _get(
            perf_client,
            "/api/v1/assets/search?q=launch",
            headers=perf_headers,
        ),
    )
    assert_within_target(stats, p95_seconds=PERFORMANCE_TARGETS.api_search_p95_seconds)


@pytest.mark.asyncio
async def test_list_content_latency(
    perf_client: AsyncClient,
    perf_headers: dict[str, str],
    principal_token: object,
) -> None:
    _ = principal_token
    stats = await collect_latencies(
        label="GET /api/v1/content",
        iterations=50,
        operation=lambda: _get(perf_client, "/api/v1/content", headers=perf_headers),
    )
    assert_within_target(stats, p95_seconds=PERFORMANCE_TARGETS.api_crud_p95_seconds)


@pytest.mark.asyncio
async def test_generate_content_acceptance_latency(
    perf_client: AsyncClient,
    perf_headers: dict[str, str],
    principal_token: object,
) -> None:
    from uuid import uuid4

    _ = principal_token
    headers = {
        **perf_headers,
        "Idempotency-Key": f"perf-gen-{uuid4().hex}",
    }
    body = {
        "assetId": "01900000-0000-7000-8000-000000000301",
        "sourceVersionId": "01900000-0000-7000-8000-000000000302",
        "modelId": "01900000-0000-7000-8000-000000000303",
        "scope": "headline",
        "parameters": {"count": 3},
    }
    stats = await collect_latencies(
        label="POST /api/v1/content/generate",
        iterations=30,
        operation=lambda: _post(perf_client, "/api/v1/content/generate", headers, body),
    )
    assert_within_target(stats, p95_seconds=PERFORMANCE_TARGETS.api_crud_p95_seconds)


@pytest.mark.asyncio
async def test_analytics_dashboard_latency(
    perf_client: AsyncClient,
    perf_headers: dict[str, str],
    principal_token: object,
) -> None:
    _ = principal_token
    stats = await collect_latencies(
        label="GET /api/v1/analytics/dashboard",
        iterations=50,
        operation=lambda: _get(
            perf_client,
            "/api/v1/analytics/dashboard",
            headers=perf_headers,
        ),
    )
    assert_within_target(stats, p95_seconds=PERFORMANCE_TARGETS.api_search_p95_seconds)


@pytest.mark.asyncio
async def test_admin_system_status_latency(
    perf_client: AsyncClient,
    perf_headers: dict[str, str],
    principal_token: object,
) -> None:
    _ = principal_token
    stats = await collect_latencies(
        label="GET /api/v1/admin/system",
        iterations=50,
        operation=lambda: _get(
            perf_client,
            "/api/v1/admin/system",
            headers=perf_headers,
        ),
    )
    assert_within_target(stats, p95_seconds=PERFORMANCE_TARGETS.api_crud_p95_seconds)


@pytest.mark.asyncio
@pytest.mark.parametrize("concurrency", [1, 10])
async def test_list_assets_concurrent_latency(
    perf_client: AsyncClient,
    perf_headers: dict[str, str],
    principal_token: object,
    concurrency: int,
) -> None:
    _ = principal_token
    stats = await run_concurrent(
        concurrency=concurrency,
        per_worker=10,
        operation=lambda: _get(perf_client, "/api/v1/assets", headers=perf_headers),
    )
    assert stats.count == concurrency * 10
    assert_within_target(stats, p95_seconds=PERFORMANCE_TARGETS.api_crud_p95_seconds * 2)


async def _get(
    client: AsyncClient,
    path: str,
    *,
    headers: dict[str, str] | None = None,
) -> None:
    response = await client.get(path, headers=headers)
    assert response.status_code in {200, 202, 204}


async def _post(
    client: AsyncClient,
    path: str,
    headers: dict[str, str],
    body: dict[str, object],
) -> None:
    response = await client.post(path, headers=headers, json=body)
    assert response.status_code in {200, 201, 202}
