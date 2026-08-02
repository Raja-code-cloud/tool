"""Validate worker and scheduler recovery behavior."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from cloud_content_hub.infrastructure.observability.health import HealthChecker, HealthStatus
from cloud_content_hub.workers.exceptions import PermanentWorkerError, TransientWorkerError
from cloud_content_hub.workers.retry import WorkerRetryPolicy, is_transient_error


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


def test_transient_worker_errors_are_retried_after_recovery(
    worker_retry_policy: WorkerRetryPolicy,
) -> None:
    decision = worker_retry_policy.classify_failure(
        task_name="cloud_content_hub.tasks.deliver_outbox_event",
        attempt_count=0,
        last_error=None,
        error=TransientWorkerError(detail="redis timeout"),
    )

    assert decision.retry is True
    assert is_transient_error(TransientWorkerError()) is True


def test_permanent_worker_errors_are_not_retried(worker_retry_policy: WorkerRetryPolicy) -> None:
    decision = worker_retry_policy.classify_failure(
        task_name="cloud_content_hub.tasks.deliver_outbox_event",
        attempt_count=0,
        last_error=None,
        error=PermanentWorkerError(detail="invalid payload"),
    )

    assert decision.retry is False


def test_worker_retry_policy_supports_recovery_after_transient_failure(
    worker_retry_policy: WorkerRetryPolicy,
) -> None:
    first = worker_retry_policy.classify_failure(
        task_name="cloud_content_hub.tasks.deliver_outbox_event",
        attempt_count=0,
        last_error=None,
        error=TransientWorkerError(detail="redis timeout"),
    )
    second = worker_retry_policy.classify_failure(
        task_name="cloud_content_hub.tasks.deliver_outbox_event",
        attempt_count=1,
        last_error="different error",
        error=TransientWorkerError(detail="redis timeout"),
    )

    assert first.retry is True
    assert second.retry is True


@pytest.mark.asyncio
async def test_worker_health_reports_unhealthy_when_database_down() -> None:
    from cloud_content_hub.infrastructure.observability.health import create_ping_health_check

    async def failing_ping() -> bool:
        raise ConnectionError("database unavailable")

    checker = HealthChecker(
        [create_ping_health_check("database", failing_ping)],
        timeout_seconds=1.0,
    )
    aggregate = await checker.check()

    assert aggregate.status is HealthStatus.UNHEALTHY
