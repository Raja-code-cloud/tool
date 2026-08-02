"""Notification module repository and publisher ports."""

from .event_publisher import INotificationEventPublisher
from .notification_preference_repository import (
    INotificationPreferenceRepository,
    NotificationChannel,
    NotificationPreferenceRecord,
    PreferenceUpdate,
)
from .notification_repository import (
    INotificationRepository,
    NewNotification,
    NotificationCategory,
    NotificationPriority,
    NotificationRecord,
    NotificationSearchCriteria,
    NotificationSearchPage,
    NotificationSeverity,
    NotificationSummaryRecord,
    NotificationTypeRecord,
    RetentionPolicy,
)

__all__ = [
    "INotificationEventPublisher",
    "INotificationPreferenceRepository",
    "INotificationRepository",
    "NewNotification",
    "NotificationCategory",
    "NotificationChannel",
    "NotificationPreferenceRecord",
    "NotificationPriority",
    "NotificationRecord",
    "NotificationSearchCriteria",
    "NotificationSearchPage",
    "NotificationSeverity",
    "NotificationSummaryRecord",
    "NotificationTypeRecord",
    "PreferenceUpdate",
    "RetentionPolicy",
]
