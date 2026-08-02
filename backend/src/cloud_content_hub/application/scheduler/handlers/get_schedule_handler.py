"""Get schedule query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.scheduler.dto.responses import ScheduleDto
from cloud_content_hub.application.scheduler.exceptions.schedule_errors import ScheduleNotFoundError
from cloud_content_hub.application.scheduler.interfaces.schedule_repository import (
    IScheduleRepository,
)
from cloud_content_hub.application.scheduler.mappers.schedule_mapper import ScheduleMapper
from cloud_content_hub.application.scheduler.queries import GetScheduleQuery
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class GetScheduleHandler:
    """Retrieves a single schedule projection."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        schedule_repository_factory: Callable[[IUnitOfWork], IScheduleRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._schedule_repository_factory = schedule_repository_factory

    async def handle(self, actor: ActorContext, query: GetScheduleQuery) -> ScheduleDto:
        require_permission(actor, "schedule:read")

        async with self._unit_of_work_factory() as unit_of_work:
            schedule_repository = self._schedule_repository_factory(unit_of_work)
            schedule = await schedule_repository.get_by_id(
                workspace_id=actor.workspace_id,
                schedule_id=query.schedule_id,
            )
            if schedule is None:
                raise ScheduleNotFoundError(parameters={"scheduleId": str(query.schedule_id)})

        return ScheduleMapper.to_dto(schedule)
