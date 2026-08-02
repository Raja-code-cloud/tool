"""Update notification preferences command handler."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from cloud_content_hub.application.notifications.commands import UpdatePreferencesCommand
from cloud_content_hub.application.notifications.dto.responses import (
    NotificationPreferenceResponseDto,
)
from cloud_content_hub.application.notifications.events import PreferencesUpdated
from cloud_content_hub.application.notifications.interfaces import (
    INotificationEventPublisher,
    INotificationPreferenceRepository,
    INotificationRepository,
    NotificationChannel,
    PreferenceUpdate,
)
from cloud_content_hub.application.notifications.mappers.notification_mapper import (
    NotificationPreferenceMapper,
)
from cloud_content_hub.application.notifications.validators.notification_validator import (
    validate_notification_type,
    validate_preference_item,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class UpdatePreferencesHandler:
    """Orchestrates notification preference updates."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        preference_repository_factory: Callable[[IUnitOfWork], INotificationPreferenceRepository],
        notification_repository_factory: Callable[[IUnitOfWork], INotificationRepository],
        event_publisher: INotificationEventPublisher | None = None,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._preference_repository_factory = preference_repository_factory
        self._notification_repository_factory = notification_repository_factory
        self._event_publisher = event_publisher

    async def handle(
        self,
        actor: ActorContext,
        command: UpdatePreferencesCommand,
    ) -> tuple[NotificationPreferenceResponseDto, ...]:
        require_permission(actor, "notifications:write")

        for item in command.request.preferences:
            validate_preference_item(item)

        async with self._unit_of_work_factory() as unit_of_work:
            preference_repository = self._preference_repository_factory(unit_of_work)
            notification_repository = self._notification_repository_factory(unit_of_work)

            for item in command.request.preferences:
                notification_type = await notification_repository.get_type_by_code(item.type_code)
                validate_notification_type(notification_type, type_code=item.type_code)

            updates = tuple(
                PreferenceUpdate(
                    type_code=item.type_code,
                    channel=NotificationChannel(item.channel.value),
                    enabled=item.enabled,
                    quiet_hours_start=item.quiet_hours_start,
                    quiet_hours_end=item.quiet_hours_end,
                    time_zone=item.time_zone,
                )
                for item in command.request.preferences
            )

            updated = await preference_repository.upsert_many(
                workspace_id=actor.workspace_id,
                user_id=actor.user_id,
                preferences=updates,
                updated_by=actor.user_id,
            )

            if self._event_publisher is not None:
                await self._event_publisher.publish(
                    PreferencesUpdated(
                        workspace_id=actor.workspace_id,
                        user_id=actor.user_id,
                        type_codes=tuple(item.type_code for item in command.request.preferences),
                        actor_id=actor.user_id,
                        occurred_at=datetime.now(tz=UTC),
                    ),
                    unit_of_work=unit_of_work,
                )

            await unit_of_work.flush()

        return tuple(NotificationPreferenceMapper.to_dto(record) for record in updated)
