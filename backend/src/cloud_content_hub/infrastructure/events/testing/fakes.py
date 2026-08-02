"""In-memory fakes for outbox and Celery integration tests."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from cloud_content_hub.infrastructure.events.models import (
    EventEnvelope,
    OutboxAppendRequest,
    OutboxDispatchRecord,
)


class FakeCeleryBroker:
    """Records enqueued Celery tasks for assertions."""

    def __init__(self) -> None:
        self.tasks: list[dict[str, Any]] = []

    def enqueue(
        self,
        *,
        task_name: str,
        queue: str,
        kwargs: Mapping[str, Any],
        headers: Mapping[str, str] | None = None,
    ) -> str:
        task_id = str(uuid4())
        self.tasks.append(
            {
                "task_id": task_id,
                "task_name": task_name,
                "queue": queue,
                "kwargs": dict(kwargs),
                "headers": dict(headers or {}),
            }
        )
        return task_id


class InMemoryOutboxStore:
    """Mutable in-memory outbox used by unit tests."""

    def __init__(self) -> None:
        self.rows: dict[UUID, OutboxDispatchRecord] = {}
        self.dead_letters: list[OutboxDispatchRecord] = []
        self.published: set[UUID] = set()

    def append(self, request: OutboxAppendRequest) -> UUID:
        event_id = uuid4()
        self.rows[event_id] = OutboxDispatchRecord(
            id=event_id,
            workspace_id=request.workspace_id,
            organization_id=request.organization_id,
            aggregate_type=request.aggregate_type,
            aggregate_id=request.aggregate_id,
            event_type=request.event_type,
            event_version=request.event_version,
            payload=request.payload,
            headers=request.headers,
            occurred_at=request.occurred_at,
            available_at=request.available_at,
            attempt_count=0,
            last_error=None,
        )
        return event_id

    def fetch_due(self, *, limit: int, now: datetime) -> list[OutboxDispatchRecord]:
        due = [
            row
            for row in self.rows.values()
            if row.available_at <= now and row.id not in self.published
        ]
        due.sort(key=lambda row: (row.available_at, row.id))
        return due[:limit]

    def mark_published(self, event_id: UUID, *, published_at: datetime) -> None:
        _ = published_at
        self.published.add(event_id)

    def mark_terminal_failure(
        self, event_id: UUID, *, failed_at: datetime, last_error: str
    ) -> None:
        _ = failed_at
        row = self.rows[event_id]
        self.rows[event_id] = OutboxDispatchRecord(
            id=row.id,
            workspace_id=row.workspace_id,
            organization_id=row.organization_id,
            aggregate_type=row.aggregate_type,
            aggregate_id=row.aggregate_id,
            event_type=row.event_type,
            event_version=row.event_version,
            payload=row.payload,
            headers=row.headers,
            occurred_at=row.occurred_at,
            available_at=row.available_at,
            attempt_count=row.attempt_count,
            last_error=last_error,
        )
        self.published.add(event_id)

    def schedule_retry(
        self,
        event_id: UUID,
        *,
        attempt_count: int,
        available_at: datetime,
        last_error: str,
    ) -> None:
        row = self.rows[event_id]
        self.rows[event_id] = OutboxDispatchRecord(
            id=row.id,
            workspace_id=row.workspace_id,
            organization_id=row.organization_id,
            aggregate_type=row.aggregate_type,
            aggregate_id=row.aggregate_id,
            event_type=row.event_type,
            event_version=row.event_version,
            payload=row.payload,
            headers=row.headers,
            occurred_at=row.occurred_at,
            available_at=available_at,
            attempt_count=attempt_count,
            last_error=last_error,
        )

    def move_to_dead_letter(self, record: OutboxDispatchRecord) -> None:
        self.dead_letters.append(record)
        self.published.add(record.id)


class RecordingPlatformDeliverer:
    """Captures delivered envelopes and optionally fails."""

    def __init__(self, *, fail_with: Exception | None = None) -> None:
        self.envelopes: list[EventEnvelope] = []
        self.fail_with = fail_with

    async def __call__(self, envelope: EventEnvelope) -> None:
        if self.fail_with is not None:
            raise self.fail_with
        self.envelopes.append(envelope)

    @staticmethod
    def now() -> datetime:
        return datetime.now(tz=UTC)
