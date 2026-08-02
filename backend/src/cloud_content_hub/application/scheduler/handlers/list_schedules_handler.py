"""List schedules query handler."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from cloud_content_hub.application.scheduler.dto.responses import ScheduleCalendarDto
from cloud_content_hub.application.scheduler.interfaces.schedule_repository import (
    IScheduleRepository,
    ScheduleListCriteria,
)
from cloud_content_hub.application.scheduler.mappers.schedule_mapper import ScheduleMapper
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.dto.base import PagedResultDto, PageInfoDto
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class ListSchedulesHandler:
    """Lists publication schedules for calendar and queue views."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        schedule_repository_factory: Callable[[IUnitOfWork], IScheduleRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._schedule_repository_factory = schedule_repository_factory

    async def handle(
        self, actor: ActorContext, query: dict[str, Any]
    ) -> PagedResultDto[ScheduleCalendarDto]:
        require_permission(actor, "schedule:read")

        async with self._unit_of_work_factory() as unit_of_work:
            schedule_repository = self._schedule_repository_factory(unit_of_work)
            page = await schedule_repository.list_schedules(
                ScheduleListCriteria(
                    workspace_id=actor.workspace_id,
                    cursor=query.get("cursor"),
                    limit=int(query.get("limit", 25)),
                    states=query.get("states", frozenset()),
                    priorities=query.get("priorities", frozenset()),
                    publication_target_id=query.get("publication_target_id"),
                    scheduled_after=query.get("scheduled_after"),
                    scheduled_before=query.get("scheduled_before"),
                    sort=str(query.get("sort", "-updated_at")),
                )
            )

        items = tuple(ScheduleMapper.to_calendar_dto(record) for record in page.items)
        return PagedResultDto(
            items=items,
            page=PageInfoDto(
                next_cursor=page.next_cursor,
                has_more=page.has_more,
                limit=int(query.get("limit", 25)),
            ),
        )
