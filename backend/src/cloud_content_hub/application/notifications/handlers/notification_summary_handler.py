"""Notification summary query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.notifications.dto.responses import NotificationSummaryResponseDto
from cloud_content_hub.application.notifications.interfaces.notification_repository import (
    INotificationRepository,
)
from cloud_content_hub.application.notifications.mappers.notification_mapper import (
    NotificationSummaryMapper,
)
from cloud_content_hub.application.notifications.queries import NotificationSummaryQuery
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class NotificationSummaryHandler:
    """Retrieves aggregated notification inbox statistics."""

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
        query: NotificationSummaryQuery,
    ) -> NotificationSummaryResponseDto:
        require_permission(actor, "notifications:read")

        async with self._unit_of_work_factory() as unit_of_work:
            notification_repository = self._notification_repository_factory(unit_of_work)
            summary = await notification_repository.get_summary(
                workspace_id=actor.workspace_id,
                recipient_user_id=actor.user_id,
            )

        return NotificationSummaryMapper.to_dto(summary)
