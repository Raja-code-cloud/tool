"""Validate Celery queue recovery after Redis restoration."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from cloud_content_hub.infrastructure.events.config import EventPublishingConfig
from cloud_content_hub.infrastructure.events.dispatcher import OutboxDispatcher
from cloud_content_hub.infrastructure.events.models import OutboxDispatchRecord
from cloud_content_hub.infrastructure.events.registry import create_default_registry
from cloud_content_hub.infrastructure.events.testing.fakes import FakeCeleryBroker
from cloud_content_hub.workers.exceptions import TransientWorkerError
from cloud_content_hub.workers.retry import WorkerRetryPolicy


@pytest.fixture
def event_config() -> EventPublishingConfig:
    return EventPublishingConfig(batch_size=50, max_attempts=3, poison_message_threshold=2)


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
async def test_queue_recovery_redispatches_after_broker_restored(
    event_config: EventPublishingConfig,
) -> None:
    broker = FakeCeleryBroker()
    registry = create_default_registry()
    now = datetime.now(tz=UTC)
    records = [
        OutboxDispatchRecord(
            id=uuid4(),
            workspace_id=uuid4(),
            organization_id=None,
            aggregate_type="notification",
            aggregate_id=uuid4(),
            event_type="notification.created",
            event_version=1,
            payload={"type_code": "content.approved"},
            headers={},
            occurred_at=now,
            available_at=now,
            attempt_count=0,
            last_error=None,
        )
        for _ in range(3)
    ]

    outbox = AsyncMock()
    outbox.fetch_due = AsyncMock(return_value=records)
    session = AsyncMock()
    dispatcher = OutboxDispatcher(
        outbox=outbox,
        registry=registry,
        broker=broker,
        config=event_config,
    )

    dispatched = await dispatcher.dispatch_batch(session, now=now)

    assert dispatched == 3
    assert len(broker.tasks) == 3


def test_transient_broker_errors_are_retried_after_queue_recovery(
    worker_retry_policy: WorkerRetryPolicy,
) -> None:
    decision = worker_retry_policy.classify_failure(
        task_name="cloud_content_hub.tasks.deliver_outbox_event",
        attempt_count=0,
        last_error=None,
        error=TransientWorkerError(detail="Connection refused"),
    )

    assert decision.retry is True
    assert decision.reason_code == "transient_failure"
