"""Notification response DTOs."""

from __future__ import annotations

from datetime import datetime, time
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from cloud_content_hub.application.shared.dto.base import ApplicationDto, ResourceBaseDto


class NotificationSeverityDto(StrEnum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationChannelDto(StrEnum):
    IN_APP = "in_app"
    EMAIL = "email"
    WEBHOOK = "webhook"


class NotificationResponseDto(ResourceBaseDto):
    """Notification projection returned by handlers."""

    type_code: str
    title: str
    body: str
    severity: NotificationSeverityDto
    resource_type: str | None = None
    resource_id: UUID | None = None
    read_at: datetime | None
    archived_at: datetime | None = None
    expires_at: datetime | None = None


# Backward-compatible alias used by existing handlers and docs.
NotificationDto = NotificationResponseDto


class NotificationPreferenceResponseDto(ResourceBaseDto):
    """Notification preference projection returned by handlers."""

    type_code: str
    channel: NotificationChannelDto
    enabled: bool
    quiet_hours_start: time | None = None
    quiet_hours_end: time | None = None
    time_zone: str


class SeverityCountDto(ApplicationDto):
    """Unread or total count grouped by severity."""

    severity: NotificationSeverityDto
    count: int = Field(ge=0)


class TypeCodeCountDto(ApplicationDto):
    """Count grouped by notification type code."""

    type_code: str
    count: int = Field(ge=0)


class NotificationSummaryResponseDto(ApplicationDto):
    """Aggregated notification inbox statistics."""

    total_count: int = Field(ge=0)
    unread_count: int = Field(ge=0)
    archived_count: int = Field(ge=0)
    counts_by_severity: tuple[SeverityCountDto, ...]
    counts_by_type_code: tuple[TypeCodeCountDto, ...]


class UnreadCountResponseDto(ApplicationDto):
    """Unread notification count for the current user."""

    unread_count: int = Field(ge=0)
