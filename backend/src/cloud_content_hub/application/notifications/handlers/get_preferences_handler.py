"""Get notification preferences query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.notifications.dto.responses import (
    NotificationPreferenceResponseDto,
)
from cloud_content_hub.application.notifications.interfaces import INotificationPreferenceRepository
from cloud_content_hub.application.notifications.mappers.notification_mapper import (
    NotificationPreferenceMapper,
)
from cloud_content_hub.application.notifications.queries import GetPreferencesQuery
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class GetPreferencesHandler:
    """Retrieves notification preferences for the current user."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        preference_repository_factory: Callable[[IUnitOfWork], INotificationPreferenceRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._preference_repository_factory = preference_repository_factory

    async def handle(
        self,
        actor: ActorContext,
        query: GetPreferencesQuery,
    ) -> tuple[NotificationPreferenceResponseDto, ...]:
        require_permission(actor, "notifications:read")

        async with self._unit_of_work_factory() as unit_of_work:
            preference_repository = self._preference_repository_factory(unit_of_work)
            preferences = await preference_repository.list_for_user(
                workspace_id=actor.workspace_id,
                user_id=actor.user_id,
            )

        return tuple(NotificationPreferenceMapper.to_dto(record) for record in preferences)
