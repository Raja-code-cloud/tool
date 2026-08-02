"""Outbox polling and batch dispatch performance validation."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from cloud_content_hub.infrastructure.events.dispatcher import OutboxDispatcher
from cloud_content_hub.infrastructure.events.models import OutboxAppendRequest, OutboxDispatchRecord
from cloud_content_hub.infrastructure.events.registry import create_default_registry
from cloud_content_hub.infrastructure.events.testing.fakes import (
    FakeCeleryBroker,
    InMemoryOutboxStore,
)
from tests.performance.helpers.metrics import collect_latencies
from tests.performance.helpers.targets import PERFORMANCE_TARGETS, assert_within_target

pytestmark = pytest.mark.performance


@pytest.fixture
def outbox_store() -> InMemoryOutboxStore:
    store = InMemoryOutboxStore()
    now = datetime.now(tz=UTC)
    for index in range(200):
        store.append(
            OutboxAppendRequest(
                workspace_id=uuid4(),
                organization_id=None,
                aggregate_type="notification",
                aggregate_id=uuid4(),
                event_type="notification.created",
                event_version=1,
                payload={"index": index},
                headers={"correlation_id": f"perf-{index}"},
                occurred_at=now,
                available_at=now - timedelta(seconds=1),
                created_by=uuid4(),
            )
        )
    return store


@pytest.mark.asyncio
async def test_outbox_fetch_due_latency(outbox_store: InMemoryOutboxStore) -> None:
    now = datetime.now(tz=UTC)

    async def fetch_once() -> None:
        rows = outbox_store.fetch_due(limit=100, now=now)
        assert len(rows) == 100

    stats = await collect_latencies(
        label="InMemoryOutboxStore.fetch_due",
        iterations=100,
        operation=fetch_once,
    )
    assert_within_target(stats, p95_seconds=0.010, label="outbox fetch_due")


@pytest.mark.asyncio
async def test_outbox_dispatch_batch_latency(
    celery_broker: FakeCeleryBroker,
    event_config: object,
) -> None:
    from cloud_content_hub.infrastructure.events.config import EventPublishingConfig

    config = (
        event_config
        if isinstance(event_config, EventPublishingConfig)
        else EventPublishingConfig()
    )
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
            headers={"correlation_id": f"perf-{index}"},
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

    async def dispatch_once() -> None:
        count = await dispatcher.dispatch_batch(session, now=now)
        assert count == config.batch_size

    stats = await collect_latencies(
        label="OutboxDispatcher.dispatch_batch",
        iterations=20,
        operation=dispatch_once,
    )
    assert_within_target(
        stats,
        p95_seconds=PERFORMANCE_TARGETS.outbox_batch_p95_seconds,
        label="outbox dispatch batch",
    )
    assert len(celery_broker.tasks) >= config.batch_size


@pytest.mark.asyncio
async def test_outbox_append_throughput(outbox_store: InMemoryOutboxStore) -> None:
    now = datetime.now(tz=UTC)

    async def append_once() -> None:
        outbox_store.append(
            OutboxAppendRequest(
                workspace_id=uuid4(),
                organization_id=None,
                aggregate_type="asset",
                aggregate_id=uuid4(),
                event_type="asset.uploaded",
                event_version=1,
                payload={"filename": "perf.png"},
                headers={"correlation_id": "perf-append"},
                occurred_at=now,
                available_at=now,
                created_by=uuid4(),
            )
        )

    stats = await collect_latencies(
        label="InMemoryOutboxStore.append",
        iterations=500,
        operation=append_once,
    )
    assert_within_target(stats, p95_seconds=0.005, label="outbox append")
