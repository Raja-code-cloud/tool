"""Delete notification command handler."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from cloud_content_hub.application.notifications.commands import DeleteNotificationCommand
from cloud_content_hub.application.notifications.events import NotificationDeleted
from cloud_content_hub.application.notifications.exceptions.notification_errors import (
    NotificationNotFoundError,
)
from cloud_content_hub.application.notifications.interfaces.event_publisher import (
    INotificationEventPublisher,
)
from cloud_content_hub.application.notifications.interfaces.notification_repository import (
    INotificationRepository,
)
from cloud_content_hub.application.notifications.validators.notification_validator import (
    validate_recipient_ownership,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.core.errors import VersionConflictError


class DeleteNotificationHandler:
    """Orchestrates notification soft-deletion."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        notification_repository_factory: Callable[[IUnitOfWork], INotificationRepository],
        event_publisher: INotificationEventPublisher | None = None,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._notification_repository_factory = notification_repository_factory
        self._event_publisher = event_publisher

    async def handle(self, actor: ActorContext, command: DeleteNotificationCommand) -> None:
        require_permission(actor, "notifications:delete")

        async with self._unit_of_work_factory() as unit_of_work:
            notification_repository = self._notification_repository_factory(unit_of_work)
            notification = await notification_repository.get_by_id(
                workspace_id=actor.workspace_id,
                notification_id=command.notification_id,
                recipient_user_id=actor.user_id,
            )
            if notification is None:
                raise NotificationNotFoundError(
                    parameters={"notificationId": str(command.notification_id)},
                )
            validate_recipient_ownership(notification, recipient_user_id=actor.user_id)

            if notification.version != command.expected_version:
                raise VersionConflictError(
                    parameters={
                        "notificationId": str(command.notification_id),
                        "expectedVersion": command.expected_version,
                    },
                )

            await notification_repository.soft_delete(
                workspace_id=actor.workspace_id,
                notification_id=command.notification_id,
                recipient_user_id=actor.user_id,
                expected_version=command.expected_version,
                updated_by=actor.user_id,
            )

            if self._event_publisher is not None:
                await self._event_publisher.publish(
                    NotificationDeleted(
                        workspace_id=actor.workspace_id,
                        notification_id=command.notification_id,
                        recipient_user_id=actor.user_id,
                        actor_id=actor.user_id,
                        version=command.expected_version,
                        occurred_at=datetime.now(tz=UTC),
                    ),
                    unit_of_work=unit_of_work,
                )

            await unit_of_work.flush()
