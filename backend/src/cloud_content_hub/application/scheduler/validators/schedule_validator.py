"""Schedule business validation."""

from __future__ import annotations

from datetime import UTC, datetime

from cloud_content_hub.application.scheduler.dto.requests import ScheduleRequestDto
from cloud_content_hub.application.scheduler.exceptions.schedule_errors import (
    ScheduleTimeAmbiguousError,
    ScheduleTimeNonexistentError,
)
from cloud_content_hub.application.scheduler.interfaces.schedule_repository import (
    AmbiguityPolicy,
    SchedulePriority,
    ScheduleRecord,
    ScheduleState,
)
from cloud_content_hub.application.scheduler.interfaces.schedule_time_resolver import (
    IScheduleTimeResolver,
    LocalScheduleInput,
    ResolvedLocalTime,
)
from cloud_content_hub.core.errors import StateTransitionError, ValidationError


def resolve_schedule_time(
    resolver: IScheduleTimeResolver,
    request: ScheduleRequestDto,
) -> ResolvedLocalTime:
    """Resolve local schedule time using the schedule time resolver port."""

    try:
        return resolver.resolve(
            LocalScheduleInput(
                requested_local_at=request.requested_local_at,
                time_zone=request.time_zone,
                fold=int(request.fold.value) if request.fold is not None else None,
                ambiguity_policy=AmbiguityPolicy(request.ambiguity_policy.value),
            )
        )
    except ScheduleTimeNonexistentError:
        raise
    except ScheduleTimeAmbiguousError:
        raise
    except ValueError as exc:
        message = str(exc)
        if "nonexistent" in message:
            raise ScheduleTimeNonexistentError(detail=message) from exc
        if "ambiguous" in message:
            raise ScheduleTimeAmbiguousError(detail=message) from exc
        raise ValidationError(detail=message) from exc


def validate_schedule_creation(
    *,
    target_valid: bool,
    has_active_schedule: bool,
    resolved: ResolvedLocalTime,
) -> None:
    """Validate schedule creation business rules."""

    if not target_valid:
        raise ValidationError(detail="Publication target must be approved and dispatchable.")
    if has_active_schedule:
        raise ValidationError(detail="An active schedule already exists for this target.")
    if resolved.scheduled_for <= datetime.now(tz=UTC):
        raise ValidationError(detail="Scheduled time must be in the future.")


def validate_schedule_priority(request: ScheduleRequestDto) -> SchedulePriority:
    return SchedulePriority(request.priority.value)


def validate_cancellation(schedule: ScheduleRecord) -> None:
    """Validate that a schedule can be cancelled."""

    if schedule.state in {
        ScheduleState.DISPATCHED,
        ScheduleState.COMPLETED,
        ScheduleState.CANCELLED,
    }:
        raise StateTransitionError(
            detail="Schedule cannot be cancelled from its current state.",
            parameters={"state": schedule.state.value},
        )
