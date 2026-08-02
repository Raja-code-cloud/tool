"""Scheduler request DTOs."""

from __future__ import annotations

from datetime import datetime
from enum import IntEnum, StrEnum
from uuid import UUID

from pydantic import Field

from cloud_content_hub.application.shared.dto.base import ApplicationDto


class AmbiguityPolicyDto(StrEnum):
    REJECT = "reject"
    EARLIER = "earlier"
    LATER = "later"


class SchedulePriorityDto(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class DstFoldDto(IntEnum):
    FIRST = 0
    SECOND = 1


class ScheduleRequestDto(ApplicationDto):
    """Request payload for creating a schedule."""

    publication_target_id: UUID
    requested_local_at: datetime
    time_zone: str = Field(min_length=1)
    fold: DstFoldDto | None = None
    ambiguity_policy: AmbiguityPolicyDto = AmbiguityPolicyDto.REJECT
    priority: SchedulePriorityDto = SchedulePriorityDto.NORMAL
