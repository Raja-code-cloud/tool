"""Notification command definitions."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from cloud_content_hub.application.notifications.dto.requests import (
    MarkNotificationReadRequestDto,
    NotificationRequestDto,
    UpdatePreferencesRequestDto,
)


@dataclass(frozen=True, slots=True)
class CreateNotificationCommand:
    """Command to create a notification for a recipient."""

    request: NotificationRequestDto


@dataclass(frozen=True, slots=True)
class MarkNotificationReadCommand:
    """Command to update notification read state."""

    notification_id: UUID
    expected_version: int
    request: MarkNotificationReadRequestDto


@dataclass(frozen=True, slots=True)
class MarkAllReadCommand:
    """Command to mark all unread notifications as read."""


@dataclass(frozen=True, slots=True)
class ArchiveNotificationCommand:
    """Command to archive a notification."""

    notification_id: UUID
    expected_version: int


@dataclass(frozen=True, slots=True)
class DeleteNotificationCommand:
    """Command to soft-delete a notification."""

    notification_id: UUID
    expected_version: int


@dataclass(frozen=True, slots=True)
class UpdatePreferencesCommand:
    """Command to update notification preferences."""

    request: UpdatePreferencesRequestDto
