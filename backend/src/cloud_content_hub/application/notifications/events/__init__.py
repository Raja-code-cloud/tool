"""Notification domain events raised by command handlers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from cloud_content_hub.application.notifications.interfaces.notification_repository import (
        NotificationSeverity,
    )


@dataclass(frozen=True, slots=True)
class NotificationCreated:
    """Raised when a notification is created for a recipient."""

    workspace_id: UUID
    notification_id: UUID
    recipient_user_id: UUID
    type_code: str
    severity: NotificationSeverity
    actor_id: UUID
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class NotificationRead:
    """Raised when a notification read state changes."""

    workspace_id: UUID
    notification_id: UUID
    recipient_user_id: UUID
    read_at: datetime | None
    actor_id: UUID
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class NotificationArchived:
    """Raised when a notification is archived."""

    workspace_id: UUID
    notification_id: UUID
    recipient_user_id: UUID
    actor_id: UUID
    version: int
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class NotificationDeleted:
    """Raised when a notification is soft-deleted."""

    workspace_id: UUID
    notification_id: UUID
    recipient_user_id: UUID
    actor_id: UUID
    version: int
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class PreferencesUpdated:
    """Raised when notification preferences are updated."""

    workspace_id: UUID
    user_id: UUID
    type_codes: tuple[str, ...]
    actor_id: UUID
    occurred_at: datetime


NotificationDomainEvent = (
    NotificationCreated
    | NotificationRead
    | NotificationArchived
    | NotificationDeleted
    | PreferencesUpdated
)

__all__ = [
    "NotificationArchived",
    "NotificationCreated",
    "NotificationDeleted",
    "NotificationDomainEvent",
    "NotificationRead",
    "PreferencesUpdated",
]
