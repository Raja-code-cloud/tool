"""Validate outbox recovery and redispatch behavior."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from cloud_content_hub.infrastructure.events.config import EventPublishingConfig
from cloud_content_hub.infrastructure.events.dispatcher import OutboxDispatcher, OutboxHealthCheck
from cloud_content_hub.infrastructure.events.models import OutboxDispatchRecord
from cloud_content_hub.infrastructure.events.registry import create_default_registry
from cloud_content_hub.infrastructure.events.testing.fakes import FakeCeleryBroker
from cloud_content_hub.infrastructure.observability.health import HealthStatus


@pytest.fixture
def event_config() -> EventPublishingConfig:
    return EventPublishingConfig(
        batch_size=10,
        max_attempts=3,
        poison_message_threshold=2,
        dispatch_lag_warning_seconds=60.0,
    )


@pytest.mark.asyncio
async def test_outbox_health_healthy_when_no_unpublished_events(
    event_config: EventPublishingConfig,
) -> None:
    lag_probe = AsyncMock()
    lag_probe.oldest_unpublished_age_seconds = AsyncMock(return_value=None)
    session = AsyncMock()
    session.close = AsyncMock()
    session_factory = AsyncMock(return_value=session)

    check = OutboxHealthCheck(
        session_factory=session_factory,
        lag_probe=lag_probe,
        config=event_config,
    )
    result = await check.check()

    assert result.status is HealthStatus.HEALTHY
    assert result.message == "No unpublished outbox events"


@pytest.mark.asyncio
async def test_outbox_health_degraded_when_lag_exceeds_warning(
    event_config: EventPublishingConfig,
) -> None:
    lag_probe = AsyncMock()
    lag_probe.oldest_unpublished_age_seconds = AsyncMock(return_value=120.0)
    session = AsyncMock()
    session.close = AsyncMock()
    session_factory = AsyncMock(return_value=session)

    check = OutboxHealthCheck(
        session_factory=session_factory,
        lag_probe=lag_probe,
        config=event_config,
    )
    result = await check.check()

    assert result.status is HealthStatus.DEGRADED


@pytest.mark.asyncio
async def test_outbox_redispatch_after_broker_recovery(
    event_config: EventPublishingConfig,
) -> None:
    broker = FakeCeleryBroker()
    registry = create_default_registry()
    now = datetime(2026, 1, 2, tzinfo=UTC)
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
        occurred_at=now,
        available_at=now,
        attempt_count=0,
        last_error=None,
    )

    outbox = AsyncMock()
    outbox.fetch_due = AsyncMock(return_value=[record])
    session = AsyncMock()
    dispatcher = OutboxDispatcher(
        outbox=outbox,
        registry=registry,
        broker=broker,
        config=event_config,
    )

    dispatched = await dispatcher.dispatch_batch(session, now=now)

    assert dispatched == 1
    assert len(broker.tasks) == 1
    assert broker.tasks[0]["kwargs"]["envelope"]["event_type"] == "notification.created"
