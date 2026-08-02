"""Notification repository port and read models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class NotificationSeverity(StrEnum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationCategory(StrEnum):
    TRANSACTIONAL = "transactional"
    PRODUCT = "product"
    SECURITY = "security"


class NotificationPriority(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class RetentionPolicy(StrEnum):
    STANDARD = "standard"
    EXTENDED = "extended"
    PERMANENT = "permanent"


@dataclass(frozen=True, slots=True)
class NotificationRecord:
    """Notification inbox read model."""

    id: UUID
    workspace_id: UUID
    version: int
    created_at: datetime
    updated_at: datetime
    type_code: str
    title: str
    body: str
    severity: NotificationSeverity
    resource_type: str | None
    resource_id: UUID | None
    read_at: datetime | None
    archived_at: datetime | None
    expires_at: datetime | None
    recipient_user_id: UUID


@dataclass(frozen=True, slots=True)
class NewNotification:
    """Input for creating a notification."""

    workspace_id: UUID
    recipient_user_id: UUID
    type_code: str
    title: str
    body: str
    severity: NotificationSeverity
    resource_type: str | None
    resource_id: UUID | None
    dedupe_key: str
    expires_at: datetime | None
    created_by: UUID


@dataclass(frozen=True, slots=True)
class NotificationSearchCriteria:
    """Structured notification inbox search criteria."""

    workspace_id: UUID
    recipient_user_id: UUID
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
class NotificationSearchPage:
    """Cursor-paged notification search results."""

    items: tuple[NotificationRecord, ...]
    next_cursor: str | None
    has_more: bool


@dataclass(frozen=True, slots=True)
class NotificationSummaryRecord:
    """Aggregated notification inbox statistics."""

    total_count: int
    unread_count: int
    archived_count: int
    counts_by_severity: tuple[tuple[NotificationSeverity, int], ...]
    counts_by_type_code: tuple[tuple[str, int], ...]


@dataclass(frozen=True, slots=True)
class NotificationTypeRecord:
    """Notification type catalog entry."""

    code: str
    category: NotificationCategory
    default_channels: frozenset[str]


class INotificationRepository(Protocol):
    """Repository port for user notifications."""

    async def get_by_id(
        self,
        *,
        workspace_id: UUID,
        notification_id: UUID,
        recipient_user_id: UUID,
    ) -> NotificationRecord | None:
        """Return one notification for the recipient."""

    async def search(self, criteria: NotificationSearchCriteria) -> NotificationSearchPage:
        """Search the recipient notification inbox."""

    async def create(self, notification: NewNotification) -> NotificationRecord:
        """Persist a new notification for a recipient."""

    async def mark_read(
        self,
        *,
        workspace_id: UUID,
        notification_id: UUID,
        recipient_user_id: UUID,
        read: bool,
        expected_version: int,
        updated_by: UUID,
    ) -> NotificationRecord:
        """Set or clear read state for a notification."""

    async def mark_all_read(
        self,
        *,
        workspace_id: UUID,
        recipient_user_id: UUID,
        updated_by: UUID,
    ) -> int:
        """Mark all unread notifications as read; return count updated."""

    async def archive(
        self,
        *,
        workspace_id: UUID,
        notification_id: UUID,
        recipient_user_id: UUID,
        expected_version: int,
        updated_by: UUID,
    ) -> NotificationRecord:
        """Archive a notification while keeping it searchable."""

    async def soft_delete(
        self,
        *,
        workspace_id: UUID,
        notification_id: UUID,
        recipient_user_id: UUID,
        expected_version: int,
        updated_by: UUID,
    ) -> None:
        """Soft-delete a notification for the recipient."""

    async def count_unread(
        self,
        *,
        workspace_id: UUID,
        recipient_user_id: UUID,
    ) -> int:
        """Return the unread notification count for a recipient."""

    async def get_summary(
        self,
        *,
        workspace_id: UUID,
        recipient_user_id: UUID,
    ) -> NotificationSummaryRecord:
        """Return aggregated inbox statistics for a recipient."""

    async def validate_recipient_in_workspace(
        self,
        *,
        workspace_id: UUID,
        recipient_user_id: UUID,
    ) -> bool:
        """Return whether the recipient is an active workspace member."""

    async def get_type_by_code(self, type_code: str) -> NotificationTypeRecord | None:
        """Return catalog metadata for a notification type code."""
