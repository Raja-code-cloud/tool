"""Notification preference repository port and read models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class NotificationChannel(StrEnum):
    IN_APP = "in_app"
    EMAIL = "email"
    WEBHOOK = "webhook"


@dataclass(frozen=True, slots=True)
class NotificationPreferenceRecord:
    """User notification channel preference read model."""

    id: UUID
    workspace_id: UUID
    version: int
    created_at: datetime
    updated_at: datetime
    user_id: UUID
    type_code: str
    channel: NotificationChannel
    enabled: bool
    quiet_hours_start: time | None
    quiet_hours_end: time | None
    time_zone: str


@dataclass(frozen=True, slots=True)
class PreferenceUpdate:
    """Input for upserting a notification preference."""

    type_code: str
    channel: NotificationChannel
    enabled: bool
    quiet_hours_start: time | None
    quiet_hours_end: time | None
    time_zone: str


class INotificationPreferenceRepository(Protocol):
    """Repository port for notification preferences."""

    async def list_for_user(
        self,
        *,
        workspace_id: UUID,
        user_id: UUID,
    ) -> tuple[NotificationPreferenceRecord, ...]:
        """Return all preferences for a user in a workspace."""

    async def upsert(
        self,
        *,
        workspace_id: UUID,
        user_id: UUID,
        preference: PreferenceUpdate,
        updated_by: UUID,
    ) -> NotificationPreferenceRecord:
        """Create or update one preference row."""

    async def upsert_many(
        self,
        *,
        workspace_id: UUID,
        user_id: UUID,
        preferences: tuple[PreferenceUpdate, ...],
        updated_by: UUID,
    ) -> tuple[NotificationPreferenceRecord, ...]:
        """Create or update multiple preference rows."""
