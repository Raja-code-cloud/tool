"""Validate failover tier behavior through health and retry signals."""

from __future__ import annotations

import pytest

from cloud_content_hub.infrastructure.observability.health import HealthStatus
from cloud_content_hub.workers.exceptions import TransientWorkerError
from cloud_content_hub.workers.retry import WorkerRetryPolicy
from tests.disaster_recovery.helpers.simulation import (
    DependencyState,
    build_recovery_health_checker,
    simulate_recovery_sequence,
)


@pytest.fixture
def worker_retry_policy() -> WorkerRetryPolicy:
    from cloud_content_hub.workers.config import WorkerRetryConfig

    return WorkerRetryPolicy(
        WorkerRetryConfig(
            max_retries=3,
            base_backoff_seconds=1.0,
            max_backoff_seconds=30.0,
            backoff_multiplier=2.0,
            poison_message_threshold=2,
        )
    )


@pytest.mark.asyncio
async def test_t0_container_restart_liveness_only() -> None:
    """Process liveness succeeds even when all dependencies are down."""

    checker = build_recovery_health_checker(
        DependencyState(database=False, redis=False, storage=False, outbox=False)
    )
    aggregate = await checker.check()
    application = next(r for r in aggregate.checks if r.name == "application")

    assert application.status is HealthStatus.HEALTHY
    assert aggregate.status is HealthStatus.UNHEALTHY


@pytest.mark.asyncio
async def test_t1_failover_restores_readiness_after_dependency_recovery() -> None:
    sequence = (
        DependencyState(database=False, redis=True),
        DependencyState(database=True, redis=False),
        DependencyState(database=True, redis=True),
    )
    statuses = await simulate_recovery_sequence(sequence)

    assert statuses[0] is HealthStatus.UNHEALTHY
    assert statuses[1] is HealthStatus.UNHEALTHY
    assert statuses[2] is HealthStatus.HEALTHY


def test_t2_worker_failover_retries_transient_queue_errors(
    worker_retry_policy: WorkerRetryPolicy,
) -> None:
    decision = worker_retry_policy.classify_failure(
        task_name="cloud_content_hub.tasks.deliver_outbox_event",
        attempt_count=0,
        last_error=None,
        error=TransientWorkerError(detail="broker timeout"),
    )

    assert decision.retry is True
    assert decision.backoff_seconds is not None


@pytest.mark.asyncio
async def test_storage_failover_reports_degraded_service() -> None:
    checker = build_recovery_health_checker(
        DependencyState(database=True, redis=True, storage=False)
    )
    aggregate = await checker.check()

    assert aggregate.status is HealthStatus.DEGRADED
