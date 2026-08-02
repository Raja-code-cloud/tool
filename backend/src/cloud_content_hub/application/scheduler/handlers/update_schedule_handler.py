"""Update schedule command handler."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

from cloud_content_hub.application.scheduler.dto.responses import ScheduleDto
from cloud_content_hub.application.scheduler.exceptions.schedule_errors import ScheduleNotFoundError
from cloud_content_hub.application.scheduler.interfaces.schedule_repository import (
    AmbiguityPolicy,
    IScheduleRepository,
    SchedulePriority,
    ScheduleState,
    ScheduleUpdate,
)
from cloud_content_hub.application.scheduler.interfaces.schedule_time_resolver import (
    IScheduleTimeResolver,
    LocalScheduleInput,
)
from cloud_content_hub.application.scheduler.mappers.schedule_mapper import ScheduleMapper
from cloud_content_hub.application.scheduler.validators.schedule_validator import validate_update
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.core.errors import VersionConflictError


class UpdateScheduleHandler:
    """Orchestrates schedule updates before dispatch."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        schedule_repository_factory: Callable[[IUnitOfWork], IScheduleRepository],
        schedule_time_resolver: IScheduleTimeResolver,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._schedule_repository_factory = schedule_repository_factory
        self._schedule_time_resolver = schedule_time_resolver

    async def handle(self, actor: ActorContext, command: dict[str, Any]) -> ScheduleDto:
        require_permission(actor, "schedule:write")

        request = command["request"]
        schedule_id = command["schedule_id"]
        expected_version = command["expected_version"]

        async with self._unit_of_work_factory() as unit_of_work:
            schedule_repository = self._schedule_repository_factory(unit_of_work)
            schedule = await schedule_repository.get_by_id(
                workspace_id=actor.workspace_id,
                schedule_id=schedule_id,
            )
            if schedule is None:
                raise ScheduleNotFoundError(parameters={"scheduleId": str(schedule_id)})
            if schedule.version != expected_version:
                raise VersionConflictError(
                    parameters={
                        "scheduleId": str(schedule_id),
                        "expectedVersion": expected_version,
                    },
                )

            validate_update(schedule)

            requested_local_at = request.requested_local_at or schedule.requested_local_at
            time_zone = request.time_zone or schedule.time_zone
            fold = request.fold.value if request.fold is not None else schedule.fold
            ambiguity_policy = (
                AmbiguityPolicy(request.ambiguity_policy.value)
                if request.ambiguity_policy is not None
                else schedule.ambiguity_policy
            )
            priority = (
                SchedulePriority(request.priority.value)
                if request.priority is not None
                else schedule.priority
            )
            state = ScheduleState(request.state) if request.state is not None else None

            scheduled_for: datetime | None = None
            resolved_fold = request.fold.value if request.fold is not None else None
            if request.requested_local_at is not None or request.time_zone is not None:
                resolved = self._schedule_time_resolver.resolve(
                    LocalScheduleInput(
                        requested_local_at=requested_local_at,
                        time_zone=time_zone,
                        fold=resolved_fold if resolved_fold is not None else fold,
                        ambiguity_policy=ambiguity_policy,
                    )
                )
                scheduled_for = resolved.scheduled_for
                resolved_fold = resolved.fold

            updated = await schedule_repository.update(
                workspace_id=actor.workspace_id,
                schedule_id=schedule_id,
                expected_version=expected_version,
                update=ScheduleUpdate(
                    requested_local_at=request.requested_local_at,
                    time_zone=request.time_zone,
                    fold=resolved_fold,
                    ambiguity_policy=(
                        AmbiguityPolicy(request.ambiguity_policy.value)
                        if request.ambiguity_policy is not None
                        else None
                    ),
                    priority=(
                        SchedulePriority(request.priority.value)
                        if request.priority is not None
                        else None
                    ),
                    state=state,
                    scheduled_for=scheduled_for,
                ),
                updated_by=actor.user_id,
            )
            await unit_of_work.flush()

        return ScheduleMapper.to_dto(updated)
