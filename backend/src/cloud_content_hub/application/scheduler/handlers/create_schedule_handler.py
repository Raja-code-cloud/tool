"""Create schedule command handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.scheduler.commands import SchedulePublicationCommand
from cloud_content_hub.application.scheduler.dto.responses import ScheduleDto
from cloud_content_hub.application.scheduler.interfaces.schedule_repository import (
    AmbiguityPolicy,
    IScheduleRepository,
    NewSchedule,
)
from cloud_content_hub.application.scheduler.interfaces.schedule_time_resolver import (
    IScheduleTimeResolver,
)
from cloud_content_hub.application.scheduler.mappers.schedule_mapper import ScheduleMapper
from cloud_content_hub.application.scheduler.validators.schedule_validator import (
    resolve_schedule_time,
    validate_schedule_creation,
    validate_schedule_priority,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class CreateScheduleHandler:
    """Orchestrates publication schedule creation."""

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

    async def handle(self, actor: ActorContext, command: SchedulePublicationCommand) -> ScheduleDto:
        require_permission(actor, "schedule:write")
        resolved = resolve_schedule_time(self._schedule_time_resolver, command.request)
        priority = validate_schedule_priority(command.request)

        async with self._unit_of_work_factory() as unit_of_work:
            schedule_repository = self._schedule_repository_factory(unit_of_work)
            target_valid = await schedule_repository.validate_publication_target(
                workspace_id=actor.workspace_id,
                publication_target_id=command.request.publication_target_id,
            )
            has_active = await schedule_repository.has_active_schedule(
                workspace_id=actor.workspace_id,
                publication_target_id=command.request.publication_target_id,
            )
            validate_schedule_creation(
                target_valid=target_valid,
                has_active_schedule=has_active,
                resolved=resolved,
            )

            schedule = await schedule_repository.create(
                NewSchedule(
                    workspace_id=actor.workspace_id,
                    publication_target_id=command.request.publication_target_id,
                    requested_local_at=command.request.requested_local_at,
                    time_zone=command.request.time_zone,
                    fold=resolved.fold,
                    ambiguity_policy=AmbiguityPolicy(command.request.ambiguity_policy.value),
                    priority=priority,
                    scheduled_for=resolved.scheduled_for,
                    created_by=actor.user_id,
                )
            )
            await unit_of_work.flush()

        return ScheduleMapper.to_dto(schedule)
