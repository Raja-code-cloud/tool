"""Transactional outbox persistence and dispatch state transitions."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_content_hub.infrastructure.database.enums import (
    DeadLetterReplayState,
    DeadLetterSourceType,
)
from cloud_content_hub.infrastructure.database.models.dead_letter import DeadLetter
from cloud_content_hub.infrastructure.database.models.outbox_event import OutboxEvent
from cloud_content_hub.infrastructure.events.exceptions import OutboxWriteError
from cloud_content_hub.infrastructure.events.models import OutboxAppendRequest, OutboxDispatchRecord

logger = structlog.get_logger(__name__)


class OutboxRepository:
    """Append and transition outbox rows within the caller's transaction."""

    async def append(self, session: AsyncSession, request: OutboxAppendRequest) -> UUID:
        """Insert one immutable outbox row."""

        row = OutboxEvent(
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
            created_by=request.created_by,
            updated_by=request.created_by,
        )
        session.add(row)
        try:
            await session.flush()
        except Exception as error:
            msg = "Failed to append outbox event."
            raise OutboxWriteError(msg) from error
        return row.id

    async def fetch_due(
        self,
        session: AsyncSession,
        *,
        limit: int,
        now: datetime,
    ) -> list[OutboxDispatchRecord]:
        """Claim unpublished due events using ``FOR UPDATE SKIP LOCKED``."""

        statement = (
            select(OutboxEvent)
            .where(
                OutboxEvent.published_at.is_(None),
                OutboxEvent.available_at <= now,
            )
            .order_by(OutboxEvent.available_at, OutboxEvent.id)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        result = await session.execute(statement)
        rows = result.scalars().all()
        return [_to_dispatch_record(row) for row in rows]

    async def mark_published(
        self,
        session: AsyncSession,
        event_id: UUID,
        *,
        published_at: datetime,
    ) -> None:
        """Mark an outbox row as successfully published."""

        await session.execute(
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id, OutboxEvent.published_at.is_(None))
            .values(published_at=published_at)
        )

    async def mark_terminal_failure(
        self,
        session: AsyncSession,
        event_id: UUID,
        *,
        failed_at: datetime,
        last_error: str,
    ) -> None:
        """Stop dispatch attempts for an event that cannot be dead-lettered."""

        await session.execute(
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id, OutboxEvent.published_at.is_(None))
            .values(
                published_at=failed_at,
                last_error=last_error[:2048],
            )
        )

    async def schedule_retry(
        self,
        session: AsyncSession,
        event_id: UUID,
        *,
        attempt_count: int,
        available_at: datetime,
        last_error: str,
    ) -> None:
        """Defer a failed dispatch attempt without mutating audit columns."""

        await session.execute(
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id, OutboxEvent.published_at.is_(None))
            .values(
                attempt_count=attempt_count,
                available_at=available_at,
                last_error=last_error[:2048],
            )
        )

    async def move_to_dead_letter(
        self,
        session: AsyncSession,
        record: OutboxDispatchRecord,
        *,
        reason_code: str,
        reason_message: str,
        failed_at: datetime,
        created_by: UUID | None = None,
    ) -> UUID:
        """Persist a terminal failed outbox event to the dead-letter queue."""

        if record.workspace_id is None:
            msg = "Dead-letter creation requires a workspace-scoped outbox event."
            raise OutboxWriteError(msg)

        row = DeadLetter(
            workspace_id=record.workspace_id,
            source_type=DeadLetterSourceType.OUTBOX,
            source_id=record.id,
            reason_code=reason_code,
            reason_message=reason_message[:2048],
            payload={
                "event_type": record.event_type,
                "event_version": record.event_version,
                "aggregate_type": record.aggregate_type,
                "aggregate_id": str(record.aggregate_id),
                "payload": record.payload,
                "headers": record.headers,
                "attempt_count": record.attempt_count,
                "last_error": record.last_error,
            },
            failed_at=failed_at,
            replay_state=DeadLetterReplayState.PENDING,
            created_by=created_by,
            updated_by=created_by,
        )
        session.add(row)
        await session.execute(
            update(OutboxEvent)
            .where(OutboxEvent.id == record.id, OutboxEvent.published_at.is_(None))
            .values(
                published_at=failed_at,
                last_error=reason_message[:2048],
            )
        )
        await session.flush()
        logger.warning(
            "outbox_event_dead_lettered",
            event_id=str(record.id),
            event_type=record.event_type,
            reason_code=reason_code,
        )
        return row.id


class OutboxLagProbe(Protocol):
    """Optional dependency used by health checks."""

    async def oldest_unpublished_age_seconds(self, session: AsyncSession) -> float | None:
        """Return age in seconds of the oldest unpublished event, if any."""


class SqlAlchemyOutboxLagProbe:
    """Measure dispatch lag for unpublished outbox rows."""

    async def oldest_unpublished_age_seconds(self, session: AsyncSession) -> float | None:
        statement = (
            select(OutboxEvent.available_at)
            .where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.available_at)
            .limit(1)
        )
        result = await session.execute(statement)
        oldest = result.scalar_one_or_none()
        if oldest is None:
            return None
        now = datetime.now(tz=UTC)
        return max(0.0, (now - oldest).total_seconds())


def _to_dispatch_record(row: OutboxEvent) -> OutboxDispatchRecord:
    return OutboxDispatchRecord(
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
        last_error=row.last_error,
    )
