"""Search notifications query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.notifications.dto.responses import NotificationResponseDto
from cloud_content_hub.application.notifications.interfaces.notification_repository import (
    INotificationRepository,
    NotificationSearchCriteria,
)
from cloud_content_hub.application.notifications.mappers.notification_mapper import (
    NotificationMapper,
)
from cloud_content_hub.application.notifications.queries import SearchNotificationsQuery
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.dto.base import PagedResultDto, PageInfoDto
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.core.errors import ValidationError


class SearchNotificationsHandler:
    """Full-text searches the current user's notification inbox."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        notification_repository_factory: Callable[[IUnitOfWork], INotificationRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._notification_repository_factory = notification_repository_factory

    async def handle(
        self,
        actor: ActorContext,
        query: SearchNotificationsQuery,
    ) -> PagedResultDto[NotificationResponseDto]:
        require_permission(actor, "notifications:read")

        if not query.query.strip():
            raise ValidationError(detail="Search query must not be empty.")

        async with self._unit_of_work_factory() as unit_of_work:
            notification_repository = self._notification_repository_factory(unit_of_work)
            page = await notification_repository.search(
                NotificationSearchCriteria(
                    workspace_id=actor.workspace_id,
                    recipient_user_id=actor.user_id,
                    query=query.query.strip(),
                    severities=query.severities,
                    type_codes=query.type_codes,
                    read=query.read,
                    include_archived=query.include_archived,
                    created_after=query.created_after,
                    created_before=query.created_before,
                    cursor=query.cursor,
                    limit=query.limit,
                    sort=query.sort,
                )
            )

        items = tuple(NotificationMapper.to_dto(record) for record in page.items)
        return PagedResultDto(
            items=items,
            page=PageInfoDto(
                next_cursor=page.next_cursor,
                has_more=page.has_more,
                limit=query.limit,
            ),
        )
