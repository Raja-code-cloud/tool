"""Notification request DTOs."""

from __future__ import annotations

from datetime import time
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from cloud_content_hub.application.shared.dto.base import ApplicationDto


class NotificationSeverityRequestDto(StrEnum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationPriorityRequestDto(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class RetentionPolicyRequestDto(StrEnum):
    STANDARD = "standard"
    EXTENDED = "extended"
    PERMANENT = "permanent"


class NotificationChannelRequestDto(StrEnum):
    IN_APP = "in_app"
    EMAIL = "email"
    WEBHOOK = "webhook"


class NotificationRequestDto(ApplicationDto):
    """Request payload for creating a notification."""

    recipient_user_id: UUID = Field(description="User who receives the notification.")
    type_code: str = Field(min_length=1, max_length=128, description="Notification type code.")
    title: str = Field(min_length=1, max_length=512, description="Notification title.")
    body: str = Field(min_length=1, description="Notification body text.")
    severity: NotificationSeverityRequestDto = Field(
        default=NotificationSeverityRequestDto.INFO,
        description="User-visible severity.",
    )
    priority: NotificationPriorityRequestDto = Field(
        default=NotificationPriorityRequestDto.NORMAL,
        description="Delivery priority for channel orchestration.",
    )
    retention_policy: RetentionPolicyRequestDto = Field(
        default=RetentionPolicyRequestDto.STANDARD,
        description="Retention policy governing notification expiry.",
    )
    resource_type: str | None = Field(default=None, max_length=128)
    resource_id: UUID | None = None
    dedupe_key: str | None = Field(
        default=None,
        max_length=256,
        description="Optional deduplication key within workspace and recipient.",
    )


class MarkNotificationReadRequestDto(ApplicationDto):
    """Request payload for updating notification read state."""

    read: bool = Field(description="Whether the notification should be marked read.")


class NotificationPreferenceItemRequestDto(ApplicationDto):
    """Single preference update within a batch request."""

    type_code: str = Field(min_length=1, max_length=128)
    channel: NotificationChannelRequestDto
    enabled: bool = True
    quiet_hours_start: time | None = None
    quiet_hours_end: time | None = None
    time_zone: str = Field(default="UTC", min_length=1, max_length=64)


class UpdatePreferencesRequestDto(ApplicationDto):
    """Request payload for updating notification preferences."""

    preferences: tuple[NotificationPreferenceItemRequestDto, ...] = Field(
        min_length=1,
        description="Preference rows to upsert.",
    )
