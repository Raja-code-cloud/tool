"""Queue status port for administrative queue summaries."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class AdminQueueName(StrEnum):
    AI = "ai"
    MEDIA = "media"
    NOTIFICATION = "notification"
    MAINTENANCE = "maintenance"
    PUBLISHING = "publishing"


@dataclass(frozen=True, slots=True)
class QueueSummaryRecord:
    """Aggregate queue depth and age projection."""

    queue_name: AdminQueueName
    queued: int
    running: int
    retry_wait: int
    failed: int
    dead_lettered: int
    oldest_queued_at: datetime | None


@dataclass(frozen=True, slots=True)
class QueueStatusCriteria:
    """Structured queue status query criteria."""

    workspace_id: UUID | None
    queue_names: frozenset[AdminQueueName] = frozenset()


class IQueueStatusPort(Protocol):
    """Port for retrieving aggregate queue summaries."""

    async def list_queue_summaries(
        self,
        criteria: QueueStatusCriteria,
    ) -> tuple[QueueSummaryRecord, ...]:
        """Return queue depth and terminal state counts."""
