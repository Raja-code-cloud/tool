"""Notification orchestration services."""

from __future__ import annotations

from uuid import UUID

from cloud_content_hub.application.notifications.interfaces import (
    INotificationPreferenceRepository,
    NotificationChannel,
    NotificationTypeRecord,
)


class NotificationDeliveryService:
    """Determines delivery channels based on preferences and type defaults."""

    SUPPORTED_CHANNELS: frozenset[NotificationChannel] = frozenset({NotificationChannel.IN_APP})

    async def resolve_channels(
        self,
        *,
        workspace_id: UUID,
        recipient_user_id: UUID,
        notification_type: NotificationTypeRecord | None,
        type_code: str,
        preference_repository: INotificationPreferenceRepository,
    ) -> tuple[NotificationChannel, ...]:
        """Return enabled channels for a notification, respecting user preferences."""

        preferences = await preference_repository.list_for_user(
            workspace_id=workspace_id,
            user_id=recipient_user_id,
        )
        preference_map = {
            (preference.type_code, preference.channel): preference.enabled
            for preference in preferences
        }

        default_channels = (
            frozenset(notification_type.default_channels)
            if notification_type is not None
            else frozenset({"in_app"})
        )

        enabled: list[NotificationChannel] = []
        for channel_name in default_channels:
            channel = NotificationChannel(channel_name)
            if channel not in self.SUPPORTED_CHANNELS:
                continue
            preference_key = (type_code, channel)
            if preference_map.get(preference_key, True):
                enabled.append(channel)

        if not enabled:
            enabled.append(NotificationChannel.IN_APP)

        return tuple(enabled)
