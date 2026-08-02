"""Background job repository port for asynchronous work orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class JobQueueName(StrEnum):
    AI = "ai"
    MEDIA = "media"
    NOTIFICATION = "notification"
    MAINTENANCE = "maintenance"


class JobState(StrEnum):
    QUEUED = "queued"
    LEASED = "leased"
    RUNNING = "running"
    RETRY_WAIT = "retry_wait"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    DEAD_LETTERED = "dead_lettered"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class BackgroundJobRecord:
    """Persisted background job read model."""

    id: UUID
    workspace_id: UUID | None
    version: int
    created_at: datetime
    updated_at: datetime
    job_type: str
    queue_name: JobQueueName
    state: JobState
    resource_type: str | None
    resource_id: UUID | None
    attempt_count: int
    max_attempts: int
    available_at: datetime
    completed_at: datetime | None
    error_code: str | None
    idempotency_key: str | None


@dataclass(frozen=True, slots=True)
class NewBackgroundJob:
    """Input for creating a background job."""

    workspace_id: UUID | None
    job_type: str
    queue_name: JobQueueName
    resource_type: str | None
    resource_id: UUID | None
    idempotency_key: str | None
    created_by: UUID


class IBackgroundJobRepository(Protocol):
    """Repository port for durable background jobs."""

    async def create(self, job: NewBackgroundJob) -> BackgroundJobRecord:
        """Persist a new queued background job."""

    async def get_by_idempotency_key(
        self,
        *,
        workspace_id: UUID | None,
        job_type: str,
        idempotency_key: str,
    ) -> BackgroundJobRecord | None:
        """Return an existing job for an idempotency key, if any."""

    async def get_by_id(self, job_id: UUID) -> BackgroundJobRecord | None:
        """Return one job by identifier."""
