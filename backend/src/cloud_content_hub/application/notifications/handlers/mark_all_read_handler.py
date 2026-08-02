"""Mark all notifications read command handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.notifications.commands import MarkAllReadCommand
from cloud_content_hub.application.notifications.dto.responses import UnreadCountResponseDto
from cloud_content_hub.application.notifications.interfaces.notification_repository import (
    INotificationRepository,
)
from cloud_content_hub.application.notifications.mappers.notification_mapper import (
    NotificationSummaryMapper,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class MarkAllReadHandler:
    """Marks all unread notifications as read for the current user."""

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
        command: MarkAllReadCommand,
    ) -> UnreadCountResponseDto:
        require_permission(actor, "notifications:write")

        async with self._unit_of_work_factory() as unit_of_work:
            notification_repository = self._notification_repository_factory(unit_of_work)
            await notification_repository.mark_all_read(
                workspace_id=actor.workspace_id,
                recipient_user_id=actor.user_id,
                updated_by=actor.user_id,
            )
            await unit_of_work.flush()

            unread_count = await notification_repository.count_unread(
                workspace_id=actor.workspace_id,
                recipient_user_id=actor.user_id,
            )

        return NotificationSummaryMapper.to_unread_count_dto(unread_count)
