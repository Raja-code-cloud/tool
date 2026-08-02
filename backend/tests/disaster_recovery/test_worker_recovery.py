"""Validate worker and scheduler recovery behavior."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from cloud_content_hub.infrastructure.observability.health import HealthChecker, HealthStatus
from cloud_content_hub.workers.config import WorkerRetryConfig, WorkerRuntimeConfig
from cloud_content_hub.workers.exceptions import PermanentWorkerError, TransientWorkerError
from cloud_content_hub.workers.health import WorkerHealthService
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


@pytest.mark.asyncio
async def test_worker_health_service_builds_from_container() -> None:
    from cloud_content_hub.infrastructure.observability.health import create_ping_health_check

    async def ok_ping() -> bool:
        return True

    container = MagicMock()
    container.health_checker = HealthChecker(
        [create_ping_health_check("database", ok_ping)],
        timeout_seconds=1.0,
    )
    container.events = MagicMock()
    container.session_factory = MagicMock()

    with pytest.MonkeyPatch.context() as patcher:
        mock_outbox_check = MagicMock()
        mock_outbox_check.name = "outbox_dispatch"
        patcher.setattr(
            "cloud_content_hub.workers.health.create_outbox_health_check",
            lambda *_args, **_kwargs: mock_outbox_check,
        )
        config = WorkerRuntimeConfig(
            retry=WorkerRetryConfig(),
            health_timeout_seconds=1.0,
        )
        service = WorkerHealthService.from_container(container, config)

    check_names = {check.name for check in service.checker._checks}
    assert "outbox_dispatch" in check_names


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
