"""Scheduler response DTOs."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from cloud_content_hub.application.shared.dto.base import ResourceBaseDto


class ScheduleStateDto(StrEnum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PAUSED = "paused"
    DISPATCHED = "dispatched"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class SchedulePriorityDto(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class AmbiguityPolicyDto(StrEnum):
    REJECT = "reject"
    EARLIER = "earlier"
    LATER = "later"


class ScheduleDto(ResourceBaseDto):
    """Schedule projection returned by handlers."""

    publication_target_id: UUID
    requested_local_at: datetime
    time_zone: str
    fold: int | None
    ambiguity_policy: AmbiguityPolicyDto
    scheduled_for: datetime
    state: ScheduleStateDto
    priority: SchedulePriorityDto


class ScheduleCalendarDto(ScheduleDto):
    """Schedule projection enriched with publication metadata for calendar views."""

    publication_id: UUID
    publication_title: str
    publication_status: str
    platform_code: str
    approval_state: str
    queue_order: int
