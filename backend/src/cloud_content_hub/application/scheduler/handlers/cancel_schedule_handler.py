"""Cancel schedule command handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.scheduler.commands import CancelScheduleCommand
from cloud_content_hub.application.scheduler.dto.responses import ScheduleDto
from cloud_content_hub.application.scheduler.exceptions.schedule_errors import ScheduleNotFoundError
from cloud_content_hub.application.scheduler.interfaces.schedule_repository import (
    IScheduleRepository,
    ScheduleState,
)
from cloud_content_hub.application.scheduler.mappers.schedule_mapper import ScheduleMapper
from cloud_content_hub.application.scheduler.validators.schedule_validator import (
    validate_cancellation,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.core.errors import VersionConflictError


class CancelScheduleHandler:
    """Orchestrates schedule cancellation."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        schedule_repository_factory: Callable[[IUnitOfWork], IScheduleRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._schedule_repository_factory = schedule_repository_factory

    async def handle(self, actor: ActorContext, command: CancelScheduleCommand) -> ScheduleDto:
        require_permission(actor, "schedule:delete")

        async with self._unit_of_work_factory() as unit_of_work:
            schedule_repository = self._schedule_repository_factory(unit_of_work)
            schedule = await schedule_repository.get_by_id(
                workspace_id=actor.workspace_id,
                schedule_id=command.schedule_id,
            )
            if schedule is None:
                raise ScheduleNotFoundError(parameters={"scheduleId": str(command.schedule_id)})
            if schedule.state == ScheduleState.CANCELLED:
                return ScheduleMapper.to_dto(schedule)
            if schedule.version != command.expected_version:
                raise VersionConflictError(
                    parameters={
                        "scheduleId": str(command.schedule_id),
                        "expectedVersion": command.expected_version,
                    },
                )

            validate_cancellation(schedule)
            updated = await schedule_repository.cancel(
                workspace_id=actor.workspace_id,
                schedule_id=command.schedule_id,
                expected_version=command.expected_version,
                updated_by=actor.user_id,
            )
            await unit_of_work.flush()

        return ScheduleMapper.to_dto(updated)
