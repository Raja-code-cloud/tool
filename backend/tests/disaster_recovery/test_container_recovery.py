"""Validate container recovery via health probes."""

from __future__ import annotations

from pathlib import Path

import pytest

from cloud_content_hub.infrastructure.observability.health import (
    ApplicationHealthCheck,
    HealthStatus,
)
from tests.disaster_recovery.helpers.simulation import (
    DependencyState,
    build_recovery_health_checker,
)

HEALTH_ROUTER_SOURCE = (
    Path(__file__).resolve().parents[3]
    / "src"
    / "cloud_content_hub"
    / "api"
    / "routers"
    / "v1"
    / "health.py"
)


@pytest.mark.asyncio
async def test_container_liveness_probe_succeeds_without_dependencies() -> None:
    """Liveness must pass when only the process is running (ACA restart signal)."""

    checker = ApplicationHealthCheck()
    result = await checker.check()

    assert result.status is HealthStatus.HEALTHY


@pytest.mark.asyncio
async def test_container_readiness_requires_database_and_redis() -> None:
    checker = build_recovery_health_checker(DependencyState())
    aggregate = await checker.check()
    database = next(r for r in aggregate.checks if r.name == "database")
    redis = next(r for r in aggregate.checks if r.name == "redis")

    assert database.status is HealthStatus.HEALTHY
    assert redis.status is HealthStatus.HEALTHY


@pytest.mark.asyncio
async def test_container_recovery_restores_full_health() -> None:
    checker = build_recovery_health_checker(
        DependencyState(database=False, redis=False, storage=False)
    )
    failed = await checker.check()
    assert failed.status is HealthStatus.UNHEALTHY

    recovered = await build_recovery_health_checker(DependencyState()).check()
    assert recovered.status is HealthStatus.HEALTHY


def test_implemented_probe_routes_documented_in_health_module() -> None:
    """Release checklist routes are defined in the canonical health router source."""

    source = HEALTH_ROUTER_SOURCE.read_text(encoding="utf-8")

    assert '@router.get("/live"' in source
    assert '@router.get("/ready"' in source
    assert '@router.get("/health"' in source
