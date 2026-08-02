"""High worker and outbox activity stress validation."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from cloud_content_hub.infrastructure.events.dispatcher import OutboxDispatcher
from cloud_content_hub.infrastructure.events.models import OutboxDispatchRecord
from cloud_content_hub.infrastructure.events.registry import create_default_registry
from cloud_content_hub.infrastructure.events.testing.fakes import FakeCeleryBroker
from cloud_content_hub.workers.base import TaskExecutionContext, WorkerTaskPayload
from cloud_content_hub.workers.dispatcher import TaskDispatcher, WorkerHandlerRegistry
from cloud_content_hub.workers.routing import resolve_task_route
from tests.performance.helpers.metrics import run_concurrent

pytestmark = [pytest.mark.stress, pytest.mark.performance]


@pytest.mark.asyncio
async def test_high_worker_dispatch_saturation() -> None:
    payload = WorkerTaskPayload(
        workspace_id=uuid4(),
        actor_id=uuid4(),
        job_id=uuid4(),
        command={"action": "stress"},
    )
    route = resolve_task_route("cloud_content_hub.tasks.cleanup_temp_files")
    context = TaskExecutionContext(
        task_name="cloud_content_hub.tasks.cleanup_temp_files",
        task_id="stress-worker",
        queue=route.queue,
        retry_count=0,
        headers={"correlation_id": "stress"},
        payload=payload,
    )
    handler = AsyncMock(return_value=None)
    dispatcher = TaskDispatcher(
        WorkerHandlerRegistry({"cloud_content_hub.tasks.cleanup_temp_files": handler})
    )

    async def dispatch_once() -> None:
        await dispatcher.dispatch(context)

    stats = await run_concurrent(concurrency=50, per_worker=10, operation=dispatch_once)
    assert handler.await_count == 500
    assert stats.p99 < 0.5


@pytest.mark.asyncio
async def test_high_outbox_enqueue_saturation(celery_broker: FakeCeleryBroker) -> None:
    from cloud_content_hub.infrastructure.events.config import EventPublishingConfig

    config = EventPublishingConfig(batch_size=200)
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
            payload={"index": index},
            headers={"correlation_id": f"stress-{index}"},
            occurred_at=now,
            available_at=now,
            attempt_count=0,
            last_error=None,
        )
        for index in range(config.batch_size)
    ]
    session = AsyncMock()
    outbox = AsyncMock()
    outbox.fetch_due = AsyncMock(return_value=records)
    dispatcher = OutboxDispatcher(
        outbox=outbox,
        registry=registry,
        broker=celery_broker,
        config=config,
    )

    async def dispatch_batch() -> None:
        count = await dispatcher.dispatch_batch(session, now=now)
        assert count == config.batch_size

    stats = await run_concurrent(concurrency=10, per_worker=5, operation=dispatch_batch)
    assert len(celery_broker.tasks) >= config.batch_size
    assert stats.p99 < 2.0
