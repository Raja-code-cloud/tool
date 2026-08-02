"""Create notification command handler."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from cloud_content_hub.application.notifications.commands import CreateNotificationCommand
from cloud_content_hub.application.notifications.dto.responses import NotificationResponseDto
from cloud_content_hub.application.notifications.events import NotificationCreated
from cloud_content_hub.application.notifications.interfaces import (
    INotificationEventPublisher,
    INotificationPreferenceRepository,
    INotificationRepository,
    NewNotification,
)
from cloud_content_hub.application.notifications.mappers.notification_mapper import (
    NotificationMapper,
)
from cloud_content_hub.application.notifications.services.notification_delivery_service import (
    NotificationDeliveryService,
)
from cloud_content_hub.application.notifications.services.retention_service import RetentionService
from cloud_content_hub.application.notifications.validators.notification_validator import (
    build_dedupe_key,
    validate_create_request,
    validate_notification_category,
    validate_notification_type,
    validate_recipient_in_workspace,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class CreateNotificationHandler:
    """Orchestrates notification creation for a workspace recipient."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        notification_repository_factory: Callable[[IUnitOfWork], INotificationRepository],
        preference_repository_factory: Callable[[IUnitOfWork], INotificationPreferenceRepository],
        delivery_service: NotificationDeliveryService | None = None,
        retention_service: RetentionService | None = None,
        event_publisher: INotificationEventPublisher | None = None,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._notification_repository_factory = notification_repository_factory
        self._preference_repository_factory = preference_repository_factory
        self._delivery_service = delivery_service or NotificationDeliveryService()
        self._retention_service = retention_service or RetentionService()
        self._event_publisher = event_publisher

    async def handle(
        self,
        actor: ActorContext,
        command: CreateNotificationCommand,
    ) -> NotificationResponseDto:
        require_permission(actor, "notifications:write")

        severity, retention_policy = validate_create_request(command.request)
        expires_at = self._retention_service.resolve_expires_at(retention_policy=retention_policy)

        async with self._unit_of_work_factory() as unit_of_work:
            notification_repository = self._notification_repository_factory(unit_of_work)
            preference_repository = self._preference_repository_factory(unit_of_work)

            recipient_valid = await notification_repository.validate_recipient_in_workspace(
                workspace_id=actor.workspace_id,
                recipient_user_id=command.request.recipient_user_id,
            )
            validate_recipient_in_workspace(
                recipient_valid=recipient_valid,
                recipient_user_id=command.request.recipient_user_id,
            )

            notification_type = await notification_repository.get_type_by_code(
                command.request.type_code
            )
            category = validate_notification_type(
                notification_type,
                type_code=command.request.type_code,
            )
            validate_notification_category(type_code=command.request.type_code, category=category)

            await self._delivery_service.resolve_channels(
                workspace_id=actor.workspace_id,
                recipient_user_id=command.request.recipient_user_id,
                notification_type=notification_type,
                type_code=command.request.type_code,
                preference_repository=preference_repository,
            )

            created = await notification_repository.create(
                NewNotification(
                    workspace_id=actor.workspace_id,
                    recipient_user_id=command.request.recipient_user_id,
                    type_code=command.request.type_code,
                    title=command.request.title,
                    body=command.request.body,
                    severity=severity,
                    resource_type=command.request.resource_type,
                    resource_id=command.request.resource_id,
                    dedupe_key=build_dedupe_key(command.request),
                    expires_at=expires_at,
                    created_by=actor.user_id,
                )
            )

            if self._event_publisher is not None:
                await self._event_publisher.publish(
                    NotificationCreated(
                        workspace_id=actor.workspace_id,
                        notification_id=created.id,
                        recipient_user_id=created.recipient_user_id,
                        type_code=created.type_code,
                        severity=created.severity,
                        actor_id=actor.user_id,
                        occurred_at=datetime.now(tz=UTC),
                    ),
                    unit_of_work=unit_of_work,
                )

            await unit_of_work.flush()

        return NotificationMapper.to_dto(created)
