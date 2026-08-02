"""Schedule repository port and read models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum, StrEnum
from typing import Protocol
from uuid import UUID


class ScheduleState(StrEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PAUSED = "paused"
    DISPATCHED = "dispatched"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class SchedulePriority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class AmbiguityPolicy(StrEnum):
    REJECT = "reject"
    EARLIER = "earlier"
    LATER = "later"


class DstFold(IntEnum):
    FIRST = 0
    SECOND = 1


@dataclass(frozen=True, slots=True)
class ScheduleRecord:
    """Publication schedule read model."""

    id: UUID
    workspace_id: UUID
    version: int
    created_at: datetime
    updated_at: datetime
    publication_target_id: UUID
    requested_local_at: datetime
    time_zone: str
    fold: int | None
    ambiguity_policy: AmbiguityPolicy
    scheduled_for: datetime
    state: ScheduleState
    priority: SchedulePriority


@dataclass(frozen=True, slots=True)
class NewSchedule:
    """Input for creating a publication schedule."""

    workspace_id: UUID
    publication_target_id: UUID
    requested_local_at: datetime
    time_zone: str
    fold: int | None
    ambiguity_policy: AmbiguityPolicy
    priority: SchedulePriority
    scheduled_for: datetime
    created_by: UUID


@dataclass(frozen=True, slots=True)
class ResolvedScheduleTime:
    """Resolved UTC schedule instant."""

    scheduled_for: datetime
    fold: int | None


class IScheduleRepository(Protocol):
    """Repository port for publication schedules."""

    async def get_by_id(self, *, workspace_id: UUID, schedule_id: UUID) -> ScheduleRecord | None:
        """Return one active schedule."""

    async def create(self, schedule: NewSchedule) -> ScheduleRecord:
        """Persist a new schedule."""

    async def cancel(
        self,
        *,
        workspace_id: UUID,
        schedule_id: UUID,
        expected_version: int,
        updated_by: UUID,
    ) -> ScheduleRecord:
        """Cancel a schedule."""

    async def has_active_schedule(
        self,
        *,
        workspace_id: UUID,
        publication_target_id: UUID,
    ) -> bool:
        """Return whether an active schedule exists for the target."""

    async def validate_publication_target(
        self,
        *,
        workspace_id: UUID,
        publication_target_id: UUID,
    ) -> bool:
        """Return whether the publication target is approved and dispatchable."""
