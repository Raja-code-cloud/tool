"""Notification query definitions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from cloud_content_hub.application.notifications.interfaces.notification_repository import (
    NotificationSeverity,
)


@dataclass(frozen=True, slots=True)
class GetNotificationsQuery:
    """Query to list the current user's notifications."""

    query: str | None = None
    severities: frozenset[NotificationSeverity] = frozenset()
    type_codes: frozenset[str] = frozenset()
    read: bool | None = None
    include_archived: bool = True
    created_after: datetime | None = None
    created_before: datetime | None = None
    cursor: str | None = None
    limit: int = 25
    sort: str = "-updated_at"


@dataclass(frozen=True, slots=True)
class GetUnreadNotificationsQuery:
    """Query to list unread notifications for the current user."""

    type_codes: frozenset[str] = frozenset()
    cursor: str | None = None
    limit: int = 25
    sort: str = "-updated_at"


@dataclass(frozen=True, slots=True)
class SearchNotificationsQuery:
    """Query to full-text search the current user's notifications."""

    query: str
    severities: frozenset[NotificationSeverity] = frozenset()
    type_codes: frozenset[str] = frozenset()
    read: bool | None = None
    include_archived: bool = True
    created_after: datetime | None = None
    created_before: datetime | None = None
    cursor: str | None = None
    limit: int = 25
    sort: str = "-updated_at"


@dataclass(frozen=True, slots=True)
class GetPreferencesQuery:
    """Query to retrieve notification preferences for the current user."""


@dataclass(frozen=True, slots=True)
class NotificationSummaryQuery:
    """Query to retrieve aggregated notification inbox statistics."""
