"""Notifications application module."""

from cloud_content_hub.application.notifications.commands import (
    ArchiveNotificationCommand,
    CreateNotificationCommand,
    DeleteNotificationCommand,
    MarkAllReadCommand,
    MarkNotificationReadCommand,
    UpdatePreferencesCommand,
)
from cloud_content_hub.application.notifications.dto.responses import (
    NotificationDto,
    NotificationPreferenceResponseDto,
    NotificationResponseDto,
    NotificationSummaryResponseDto,
    UnreadCountResponseDto,
)
from cloud_content_hub.application.notifications.events import (
    NotificationArchived,
    NotificationCreated,
    NotificationDeleted,
    NotificationDomainEvent,
    NotificationRead,
    PreferencesUpdated,
)
from cloud_content_hub.application.notifications.handlers.archive_notification_handler import (
    ArchiveNotificationHandler,
)
from cloud_content_hub.application.notifications.handlers.create_notification_handler import (
    CreateNotificationHandler,
)
from cloud_content_hub.application.notifications.handlers.delete_notification_handler import (
    DeleteNotificationHandler,
)
from cloud_content_hub.application.notifications.handlers.get_notifications_handler import (
    GetNotificationsHandler,
)
from cloud_content_hub.application.notifications.handlers.get_preferences_handler import (
    GetPreferencesHandler,
)
from cloud_content_hub.application.notifications.handlers.get_unread_notifications_handler import (
    GetUnreadNotificationsHandler,
)
from cloud_content_hub.application.notifications.handlers.mark_all_read_handler import (
    MarkAllReadHandler,
)
from cloud_content_hub.application.notifications.handlers.mark_notification_read_handler import (
    MarkNotificationReadHandler,
)
from cloud_content_hub.application.notifications.handlers.notification_summary_handler import (
    NotificationSummaryHandler,
)
from cloud_content_hub.application.notifications.handlers.search_notifications_handler import (
    SearchNotificationsHandler,
)
from cloud_content_hub.application.notifications.handlers.update_preferences_handler import (
    UpdatePreferencesHandler,
)
from cloud_content_hub.application.notifications.queries import (
    GetNotificationsQuery,
    GetPreferencesQuery,
    GetUnreadNotificationsQuery,
    NotificationSummaryQuery,
    SearchNotificationsQuery,
)

__all__ = [
    "ArchiveNotificationCommand",
    "ArchiveNotificationHandler",
    "CreateNotificationCommand",
    "CreateNotificationHandler",
    "DeleteNotificationCommand",
    "DeleteNotificationHandler",
    "GetNotificationsHandler",
    "GetNotificationsQuery",
    "GetPreferencesHandler",
    "GetPreferencesQuery",
    "GetUnreadNotificationsHandler",
    "GetUnreadNotificationsQuery",
    "MarkAllReadCommand",
    "MarkAllReadHandler",
    "MarkNotificationReadCommand",
    "MarkNotificationReadHandler",
    "NotificationArchived",
    "NotificationCreated",
    "NotificationDeleted",
    "NotificationDomainEvent",
    "NotificationDto",
    "NotificationPreferenceResponseDto",
    "NotificationRead",
    "NotificationResponseDto",
    "NotificationSummaryHandler",
    "NotificationSummaryQuery",
    "NotificationSummaryResponseDto",
    "PreferencesUpdated",
    "SearchNotificationsHandler",
    "SearchNotificationsQuery",
    "UnreadCountResponseDto",
    "UpdatePreferencesCommand",
    "UpdatePreferencesHandler",
]
