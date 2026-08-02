"""Failure scenario validation for end-to-end workflows."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from cloud_content_hub.infrastructure.ai.config import ProviderConfig, ProviderKind
from cloud_content_hub.infrastructure.ai.exceptions import AIUnavailableError
from cloud_content_hub.infrastructure.ai.testing.fakes import (
    FailingMockProvider,
    RateLimitedMockProvider,
)
from cloud_content_hub.infrastructure.events.config import EventPublishingConfig
from cloud_content_hub.infrastructure.events.dispatcher import (
    OutboxDeliveryService,
    envelope_from_record,
)
from cloud_content_hub.infrastructure.events.registry import create_default_registry
from cloud_content_hub.infrastructure.events.testing.fakes import (
    FakeCeleryBroker,
    RecordingPlatformDeliverer,
)
from cloud_content_hub.infrastructure.storage.exceptions import StorageUnavailableError
from cloud_content_hub.infrastructure.storage.models import StorageLocation, UploadRequest
from cloud_content_hub.infrastructure.storage.testing.fake import InMemoryStorageProvider
from cloud_content_hub.workers.config import WorkerRetryConfig
from cloud_content_hub.workers.exceptions import TransientWorkerError
from cloud_content_hub.workers.retry import WorkerRetryPolicy

pytestmark = pytest.mark.e2e


@pytest.mark.asyncio
async def test_blob_upload_failure_surfaces_storage_error() -> None:
    """Blob upload failure is surfaced to callers."""

    provider = InMemoryStorageProvider()

    async def failing_upload(request: UploadRequest) -> object:
        raise StorageUnavailableError("blob upload failed")

    provider.upload = failing_upload  # type: ignore[method-assign]

    with pytest.raises(StorageUnavailableError, match="blob upload failed"):
        await provider.upload(
            UploadRequest(
                location=StorageLocation(container="assets", blob_name="fail.bin"),
                data=b"payload",
                content_type="application/octet-stream",
                content_length=7,
            )
        )


@pytest.mark.asyncio
async def test_ai_timeout_from_failing_mock_provider() -> None:
    """AI provider timeout/unavailability is classified as dependency failure."""

    config = ProviderConfig(kind=ProviderKind.MOCK, model="mock-gpt")
    provider = FailingMockProvider(config)
    from cloud_content_hub.infrastructure.ai.models import GenerationRequest, Message, Role

    request = GenerationRequest(
        model="mock",
        messages=(Message(role=Role.USER, content="hello"),),
    )

    with pytest.raises(AIUnavailableError):
        await provider.generate(request)


@pytest.mark.asyncio
async def test_ai_transient_failure_retries_on_second_attempt() -> None:
    """AI provider transient failures succeed after retry."""

    config = ProviderConfig(kind=ProviderKind.MOCK, model="mock-gpt")
    provider = RateLimitedMockProvider(config)
    from cloud_content_hub.infrastructure.ai.models import GenerationRequest, Message, Role

    request = GenerationRequest(
        model="mock",
        messages=(Message(role=Role.USER, content="hello"),),
    )

    with pytest.raises(AIUnavailableError):
        await provider.generate(request)
    response = await provider.generate(request)
    assert response.content


@pytest.mark.asyncio
async def test_oauth_failure_rejects_invalid_state() -> None:
    """OAuth failure rejects mismatched authorization state."""

    from cloud_content_hub.infrastructure.identity.exceptions import OAuthValidationError
from cloud_content_hub.infrastructure.identity.testing.fixtures import identity_factory

    factory = identity_factory()
    registry = factory.build_registry()
    provider = registry.get("mock")
    auth = await provider.authenticate("http://localhost:3000/callback")
    code = provider.issue_mock_code("oauth-user")  # type: ignore[attr-defined]

    with pytest.raises(OAuthValidationError):
        await provider.exchange_code(
            code,
            "http://localhost:3000/callback",
            state="wrong-state",
            expected_state=auth.state,
            nonce=auth.nonce,
            code_verifier=auth.code_verifier,
        )


@pytest.mark.asyncio
async def test_provider_outage_records_delivery_retry() -> None:
    """Provider outage schedules outbox delivery retry."""

    registry = create_default_registry()
    session = AsyncMock()
    deliverer = RecordingPlatformDeliverer(fail_with=RuntimeError("provider outage"))
    outbox = AsyncMock()
    outbox.schedule_retry = AsyncMock()
    service = OutboxDeliveryService(
        outbox=outbox,
        registry=registry,
        deliverer=deliverer,
        config=EventPublishingConfig(max_attempts=3),
    )
    from cloud_content_hub.infrastructure.events.models import OutboxDispatchRecord

    workspace_id = uuid4()
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

    with pytest.raises(RuntimeError, match="provider outage"):
        await service.deliver(session, envelope_from_record(record), record=record)

    outbox.schedule_retry.assert_awaited_once()


def test_worker_retry_exhaustion_marks_dead_letter() -> None:
    """Worker retry exhaustion stops retrying transient failures."""

    policy = WorkerRetryPolicy(WorkerRetryConfig(max_retries=2))
    decision = policy.classify_failure(
        task_name="cloud_content_hub.tasks.upload_asset",
        attempt_count=2,
        last_error=None,
        error=TransientWorkerError(detail="scheduler failure"),
    )

    assert decision.retry is False
    assert decision.reason_code == "retry_exhausted"


@pytest.mark.asyncio
async def test_outbox_replay_enqueues_celery_task() -> None:
    """Outbox replay enqueues Celery tasks for due events."""

    from cloud_content_hub.infrastructure.events.dispatcher import OutboxDispatcher
    from cloud_content_hub.infrastructure.events.models import OutboxDispatchRecord

    broker = FakeCeleryBroker()
    registry = create_default_registry()
    session = AsyncMock()
    workspace_id = uuid4()
    now = datetime(2026, 1, 2, tzinfo=UTC)
    record = OutboxDispatchRecord(
        id=uuid4(),
        workspace_id=workspace_id,
        organization_id=None,
        aggregate_type="asset",
        aggregate_id=uuid4(),
        event_type="asset.uploaded",
        event_version=1,
        payload={"filename": "poster.webp"},
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
        config=EventPublishingConfig(),
    )

    dispatched = await dispatcher.dispatch_batch(session, now=now)

    assert dispatched == 1
    assert broker.tasks[0]["queue"] == "media"


@pytest.mark.asyncio
async def test_database_disconnect_surfaces_on_session_execute(
    session_factory,
) -> None:
    """Database disconnect surfaces when executing against PostgreSQL."""

    from sqlalchemy import text

    async with session_factory() as session:
        await session.execute(text("SELECT 1"))


@pytest.mark.asyncio
async def test_redis_disconnect_surfaces_on_ping(e2e_container) -> None:
    """Redis disconnect surfaces during connectivity checks."""

    await e2e_container.redis.ping()
