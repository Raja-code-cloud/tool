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


@dataclass(frozen=True, slots=True)
class ScheduleListRecord:
    """Schedule read model enriched with publication metadata for calendar views."""

    schedule: ScheduleRecord
    publication_id: UUID
    publication_title: str
    publication_status: str
    platform_code: str
    approval_state: str
    queue_order: int


@dataclass(frozen=True, slots=True)
class ScheduleListCriteria:
    """Filters for listing schedules."""

    workspace_id: UUID
    cursor: str | None
    limit: int
    states: frozenset[str]
    priorities: frozenset[str]
    publication_target_id: UUID | None
    scheduled_after: datetime | None
    scheduled_before: datetime | None
    sort: str


@dataclass(frozen=True, slots=True)
class ScheduleListPage:
    """Cursor-paged schedule list."""

    items: tuple[ScheduleListRecord, ...]
    next_cursor: str | None
    has_more: bool


@dataclass(frozen=True, slots=True)
class ScheduleUpdate:
    """Input for updating a publication schedule."""

    requested_local_at: datetime | None = None
    time_zone: str | None = None
    fold: int | None = None
    ambiguity_policy: AmbiguityPolicy | None = None
    priority: SchedulePriority | None = None
    state: ScheduleState | None = None
    scheduled_for: datetime | None = None


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

    async def list_schedules(self, criteria: ScheduleListCriteria) -> ScheduleListPage:
        """List schedules with optional calendar filters."""

    async def update(
        self,
        *,
        workspace_id: UUID,
        schedule_id: UUID,
        expected_version: int,
        update: ScheduleUpdate,
        updated_by: UUID,
    ) -> ScheduleRecord:
        """Update a schedule before dispatch."""
