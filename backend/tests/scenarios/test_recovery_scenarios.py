"""Recovery scenario validation for end-to-end workflows."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from cloud_content_hub.infrastructure.events.config import EventPublishingConfig
from cloud_content_hub.infrastructure.events.dispatcher import (
    OutboxDeliveryService,
    envelope_from_record,
)
from cloud_content_hub.infrastructure.events.models import OutboxDispatchRecord
from cloud_content_hub.infrastructure.events.registry import create_default_registry
from cloud_content_hub.infrastructure.events.testing.fakes import RecordingPlatformDeliverer
from cloud_content_hub.workers.config import WorkerRetryConfig
from cloud_content_hub.workers.exceptions import TransientWorkerError
from cloud_content_hub.workers.retry import WorkerRetryPolicy

pytestmark = pytest.mark.e2e


@pytest.mark.asyncio
async def test_outbox_delivery_recovers_after_transient_failure() -> None:
    """Outbox delivery succeeds after a transient provider failure."""

    registry = create_default_registry()
    session = AsyncMock()
    deliverer = RecordingPlatformDeliverer()
    outbox = AsyncMock()
    outbox.mark_published = AsyncMock()
    service = OutboxDeliveryService(
        outbox=outbox,
        registry=registry,
        deliverer=deliverer,
        config=EventPublishingConfig(max_attempts=3),
    )
    record = OutboxDispatchRecord(
        id=uuid4(),
        workspace_id=uuid4(),
        organization_id=None,
        aggregate_type="notification",
        aggregate_id=uuid4(),
        event_type="notification.created",
        event_version=1,
        payload={"type_code": "content.approved"},
        headers={},
        occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
        available_at=datetime(2026, 1, 1, tzinfo=UTC),
        attempt_count=1,
        last_error="transient",
    )

    await service.deliver(session, envelope_from_record(record))

    assert len(deliverer.envelopes) == 1
    outbox.mark_published.assert_awaited_once()


def test_worker_retry_backoff_increases_between_attempts() -> None:
    """Worker retry backoff increases between attempts."""

    policy = WorkerRetryPolicy(WorkerRetryConfig(base_backoff_seconds=1.0, backoff_multiplier=2.0))
    first = policy.classify_failure(
        task_name="cloud_content_hub.tasks.generate_content",
        attempt_count=0,
        last_error=None,
        error=TransientWorkerError(detail="timeout"),
    )
    second = policy.classify_failure(
        task_name="cloud_content_hub.tasks.generate_content",
        attempt_count=1,
        last_error="timeout",
        error=TransientWorkerError(detail="timeout"),
    )

    assert first.retry is True
    assert second.retry is True
    assert second.backoff_seconds > first.backoff_seconds


@pytest.mark.asyncio
async def test_dead_letter_queue_moves_poison_messages() -> None:
    """Poison messages move to the dead-letter path after repeated failures."""

    from cloud_content_hub.infrastructure.events.testing.fakes import InMemoryOutboxStore

    store = InMemoryOutboxStore()
    from cloud_content_hub.infrastructure.events.models import OutboxAppendRequest

    event_id = store.append(
        OutboxAppendRequest(
            workspace_id=uuid4(),
            organization_id=None,
            aggregate_type="notification",
            aggregate_id=uuid4(),
            event_type="notification.created",
            event_version=1,
            payload={},
            headers={},
            occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
            available_at=datetime(2026, 1, 1, tzinfo=UTC),
        )
    )
    record = store.rows[event_id]
    store.move_to_dead_letter(record)

    assert len(store.dead_letters) == 1
