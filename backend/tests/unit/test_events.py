"""Unit tests for transactional outbox event publishing infrastructure."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from cloud_content_hub.application.administration.events import MaintenanceModeEnabled
from cloud_content_hub.application.assets.events import AssetUploaded
from cloud_content_hub.application.assets.interfaces.asset_repository import AssetType
from cloud_content_hub.application.notifications.events import NotificationCreated
from cloud_content_hub.application.notifications.interfaces.notification_repository import (
    NotificationSeverity,
)
from cloud_content_hub.core.context import bind_request_context, clear_request_context
from cloud_content_hub.infrastructure.events.config import EventPublishingConfig
from cloud_content_hub.infrastructure.events.dispatcher import (
    OutboxDeliveryService,
    OutboxDispatcher,
    RetryPolicy,
    envelope_from_record,
)
from cloud_content_hub.infrastructure.events.exceptions import (
    OutboxRetryExhaustedError,
    PoisonMessageError,
    UnknownEventTypeError,
)
from cloud_content_hub.infrastructure.events.factory import create_event_infrastructure
from cloud_content_hub.infrastructure.events.models import OutboxDispatchRecord
from cloud_content_hub.infrastructure.events.registry import create_default_registry
from cloud_content_hub.infrastructure.events.testing.fakes import (
    FakeCeleryBroker,
    RecordingPlatformDeliverer,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.unit_of_work import (
    SqlAlchemyUnitOfWork,
)


@pytest.fixture
def workspace_id() -> UUID:
    return uuid4()


@pytest.fixture
def actor_id() -> UUID:
    return uuid4()


@pytest.fixture
def registry():
    return create_default_registry()


@pytest.fixture
def broker() -> FakeCeleryBroker:
    return FakeCeleryBroker()


@pytest.fixture
def config() -> EventPublishingConfig:
    return EventPublishingConfig(batch_size=10, max_attempts=3, poison_message_threshold=2)


def test_registry_serializes_asset_uploaded(registry, workspace_id, actor_id) -> None:
    event = AssetUploaded(
        workspace_id=workspace_id,
        asset_id=uuid4(),
        asset_type=AssetType.POSTER,
        actor_id=actor_id,
        checksum_sha256="abc",
        byte_size=100,
        filename="photo.png",
        occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    result = registry.serialize(event)

    assert result.event_type == "asset.uploaded"
    assert result.event_version == 1
    assert result.aggregate_type == "asset"
    assert result.payload["filename"] == "photo.png"
    assert result.celery_queue == "media"


def test_registry_serializes_global_maintenance_event(registry, actor_id) -> None:
    event = MaintenanceModeEnabled(
        actor_id=actor_id,
        message="planned maintenance",
        occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    result = registry.serialize(event)

    assert result.event_type == "administration.maintenance_mode_enabled"
    assert result.workspace_id is None
    assert result.aggregate_type == "global"


def test_registry_rejects_unknown_event(registry) -> None:
    with pytest.raises(UnknownEventTypeError):
        registry.serialize(object())


def test_envelope_from_record_includes_metadata(workspace_id) -> None:
    record = OutboxDispatchRecord(
        id=uuid4(),
        workspace_id=workspace_id,
        organization_id=None,
        aggregate_type="notification",
        aggregate_id=uuid4(),
        event_type="notification.created",
        event_version=1,
        payload={"notification_id": str(uuid4())},
        headers={"correlation_id": "corr-1", "trace_id": "trace-1"},
        occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
        available_at=datetime(2026, 1, 1, tzinfo=UTC),
        attempt_count=0,
        last_error=None,
    )

    envelope = envelope_from_record(record)

    assert envelope.schema_version == 1
    assert envelope.event_type == "notification.created"
    assert envelope.metadata.correlation_id == "corr-1"
    assert envelope.metadata.trace_id == "trace-1"


@pytest.mark.asyncio
async def test_asset_publisher_appends_outbox_row(registry, workspace_id, actor_id) -> None:
    session = AsyncMock()
    session.flush = AsyncMock()
    unit_of_work = MagicMock(spec=SqlAlchemyUnitOfWork)
    unit_of_work.session = session

    bundle = create_event_infrastructure(registry=registry, broker=FakeCeleryBroker())
    event = AssetUploaded(
        workspace_id=workspace_id,
        asset_id=uuid4(),
        asset_type=AssetType.VIDEO,
        actor_id=actor_id,
        checksum_sha256="def",
        byte_size=200,
        filename="clip.mp4",
        occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    tokens = bind_request_context("req-1", "corr-1")
    try:
        await bundle.publishers.assets.publish(event, unit_of_work=unit_of_work)
    finally:
        clear_request_context(tokens)

    session.add.assert_called_once()
    added = session.add.call_args.args[0]
    assert added.event_type == "asset.uploaded"
    assert added.workspace_id == workspace_id
    assert added.headers["correlation_id"] == "corr-1"
    session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_dispatcher_enqueues_celery_tasks(registry, broker, config, workspace_id) -> None:
    session = AsyncMock()
    now = datetime(2026, 1, 2, tzinfo=UTC)
    record = OutboxDispatchRecord(
        id=uuid4(),
        workspace_id=workspace_id,
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
    dispatcher = OutboxDispatcher(
        outbox=outbox,
        registry=registry,
        broker=broker,
        config=config,
    )

    dispatched = await dispatcher.dispatch_batch(session, now=now)

    assert dispatched == 1
    assert len(broker.tasks) == 1
    assert broker.tasks[0]["queue"] == "notification"
    assert broker.tasks[0]["kwargs"]["envelope"]["event_type"] == "notification.created"


@pytest.mark.asyncio
async def test_delivery_service_marks_published(registry, config, workspace_id) -> None:
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
            workspace_id=workspace_id,
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
async def test_delivery_service_schedules_retry(registry, config, workspace_id) -> None:
    session = AsyncMock()
    deliverer = RecordingPlatformDeliverer(fail_with=RuntimeError("transient"))
    outbox = AsyncMock()
    outbox.schedule_retry = AsyncMock()
    service = OutboxDeliveryService(
        outbox=outbox,
        registry=registry,
        deliverer=deliverer,
        config=config,
    )
    record = OutboxDispatchRecord(
        id=uuid4(),
        workspace_id=workspace_id,
        organization_id=None,
        aggregate_type="notification",
        aggregate_id=uuid4(),
        event_type="notification.created",
        event_version=1,
        payload={},
        headers={},
        occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
        available_at=datetime(2026, 1, 1, tzinfo=UTC),
        attempt_count=0,
        last_error=None,
    )

    with pytest.raises(RuntimeError, match="transient"):
        await service.deliver(session, envelope_from_record(record), record=record)

    outbox.schedule_retry.assert_awaited_once()


@pytest.mark.asyncio
async def test_delivery_service_dead_letters_after_exhaustion(registry, workspace_id) -> None:
    session = AsyncMock()
    deliverer = RecordingPlatformDeliverer(fail_with=RuntimeError("still failing"))
    outbox = AsyncMock()
    outbox.schedule_retry = AsyncMock()
    outbox.move_to_dead_letter = AsyncMock()
    config = EventPublishingConfig(max_attempts=1, poison_message_threshold=5)
    service = OutboxDeliveryService(
        outbox=outbox,
        registry=registry,
        deliverer=deliverer,
        config=config,
    )
    record = OutboxDispatchRecord(
        id=uuid4(),
        workspace_id=workspace_id,
        organization_id=None,
        aggregate_type="notification",
        aggregate_id=uuid4(),
        event_type="notification.created",
        event_version=1,
        payload={},
        headers={},
        occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
        available_at=datetime(2026, 1, 1, tzinfo=UTC),
        attempt_count=0,
        last_error=None,
    )

    with pytest.raises(OutboxRetryExhaustedError):
        await service.deliver(session, envelope_from_record(record), record=record)

    outbox.move_to_dead_letter.assert_awaited_once()


def test_retry_policy_detects_poison_messages(config) -> None:
    policy = RetryPolicy(config)
    record = OutboxDispatchRecord(
        id=uuid4(),
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
        attempt_count=1,
        last_error="bad payload",
    )

    decision = policy.classify_failure(
        record,
        PoisonMessageError("bad payload"),
        now=datetime(2026, 1, 2, tzinfo=UTC),
    )

    assert decision.retry is False
    assert decision.reason_code == "poison_message"


def test_notification_event_serialization(registry, workspace_id, actor_id) -> None:
    event = NotificationCreated(
        workspace_id=workspace_id,
        notification_id=uuid4(),
        recipient_user_id=uuid4(),
        type_code="content.approved",
        severity=NotificationSeverity.INFO,
        actor_id=actor_id,
        occurred_at=datetime(2026, 1, 1, tzinfo=UTC),
    )

    result = registry.serialize(event)

    assert result.event_type == "notification.created"
    assert result.payload["severity"] == "info"
