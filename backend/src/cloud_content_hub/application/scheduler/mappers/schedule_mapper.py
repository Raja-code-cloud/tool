"""Schedule record to DTO mappers."""

from __future__ import annotations

from cloud_content_hub.application.scheduler.dto.responses import (
    AmbiguityPolicyDto,
    ScheduleCalendarDto,
    ScheduleDto,
    SchedulePriorityDto,
    ScheduleStateDto,
)
from cloud_content_hub.application.scheduler.interfaces.schedule_repository import (
    ScheduleListRecord,
    ScheduleRecord,
)


class ScheduleMapper:
    """Maps schedule read models to response DTOs."""

    @staticmethod
    def to_dto(record: ScheduleRecord) -> ScheduleDto:
        return ScheduleDto(
            id=record.id,
            version=record.version,
            created_at=record.created_at,
            updated_at=record.updated_at,
            publication_target_id=record.publication_target_id,
            requested_local_at=record.requested_local_at,
            time_zone=record.time_zone,
            fold=record.fold,
            ambiguity_policy=AmbiguityPolicyDto(record.ambiguity_policy.value),
            scheduled_for=record.scheduled_for,
            state=ScheduleStateDto(record.state.value),
            priority=SchedulePriorityDto(record.priority.value),
        )

    @staticmethod
    def to_calendar_dto(record: ScheduleListRecord) -> ScheduleCalendarDto:
        schedule = ScheduleMapper.to_dto(record.schedule)
        return ScheduleCalendarDto(
            **schedule.model_dump(),
            publication_id=record.publication_id,
            publication_title=record.publication_title,
            publication_status=record.publication_status,
            platform_code=record.platform_code,
            approval_state=record.approval_state,
            queue_order=record.queue_order,
        )
