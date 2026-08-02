"""Validate event replay through outbox after recovery."""

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


@pytest.fixture
def registry():
    return create_default_registry()


@pytest.fixture
def config() -> EventPublishingConfig:
    return EventPublishingConfig(batch_size=10, max_attempts=3, poison_message_threshold=2)


@pytest.mark.asyncio
async def test_event_replay_delivers_unpublished_outbox_record(
    registry,
    config: EventPublishingConfig,
) -> None:
    session = AsyncMock()
    deliverer = RecordingPlatformDeliverer()
    outbox = AsyncMock()
    outbox.mark_published = AsyncMock()
    service = OutboxDeliveryService(
        outbox=outbox,
        registry=registry,
        deliverer=deliverer,
        config=config,
    )
    envelope = envelope_from_record(
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
            occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
            available_at=datetime(2026, 1, 1, tzinfo=UTC),
            attempt_count=0,
            last_error=None,
        )
    )

    await service.deliver(session, envelope)

    assert len(deliverer.envelopes) == 1
    outbox.mark_published.assert_awaited_once()


@pytest.mark.asyncio
async def test_event_replay_schedules_retry_on_transient_provider_outage(
    registry,
    config: EventPublishingConfig,
) -> None:
    session = AsyncMock()
    deliverer = RecordingPlatformDeliverer(fail_with=RuntimeError("provider timeout"))
    outbox = AsyncMock()
    outbox.schedule_retry = AsyncMock()
    service = OutboxDeliveryService(
        outbox=outbox,
        registry=registry,
        deliverer=deliverer,
        config=config,
    )
    envelope = envelope_from_record(
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
            occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
            available_at=datetime(2026, 1, 1, tzinfo=UTC),
            attempt_count=0,
            last_error=None,
        )
    )

    await service.deliver(session, envelope)

    outbox.schedule_retry.assert_awaited_once()
