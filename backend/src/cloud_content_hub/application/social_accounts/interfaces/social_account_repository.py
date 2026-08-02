"""Social account repository port and read models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Protocol
from uuid import UUID


class ActivityType(StrEnum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PUBLISH_SUCCESS = "publish_success"
    PUBLISH_FAILED = "publish_failed"
    PERMISSION_CHANGED = "permission_changed"


@dataclass(frozen=True, slots=True)
class DefaultSettingsRecord:
    """Publishing defaults for a connected social account."""

    visibility: str | None
    hashtag_strategy: str | None
    auto_publish: bool
    ai_optimization: bool
    auto_schedule: bool
    url_tracking: bool


@dataclass(frozen=True, slots=True)
class SocialAccountRecord:
    """Connected social account read model."""

    id: UUID
    workspace_id: UUID
    version: int
    created_at: datetime
    updated_at: datetime
    platform_id: UUID
    platform_code: str
    platform_name: str
    external_account_id: str
    account_name: str
    display_name: str
    username: str | None
    account_type: str | None
    connection_status: str
    health_status: str
    token_status: str | None
    publishing_enabled: bool
    default_audience: str | None
    time_zone: str
    followers_count: int | None
    connected_at: datetime | None
    last_sync_at: datetime | None
    permissions: tuple[str, ...]
    default_settings: DefaultSettingsRecord | None


@dataclass(frozen=True, slots=True)
class SocialPlatformRecord:
    """Enabled social platform catalog entry."""

    id: UUID
    code: str
    name: str
    status: str
    api_version: str | None
    capability_metadata: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ActivityEventRecord:
    """Social account activity timeline entry."""

    id: UUID
    account_id: UUID
    platform_name: str
    activity_type: ActivityType
    message: str
    timestamp: datetime


@dataclass(frozen=True, slots=True)
class SocialAccountListCriteria:
    """Filters for listing workspace social accounts."""

    workspace_id: UUID
    cursor: str | None
    limit: int
    sort: str


@dataclass(frozen=True, slots=True)
class SocialAccountListPage:
    """Paged social account list result."""

    items: tuple[SocialAccountRecord, ...]
    next_cursor: str | None
    has_more: bool


@dataclass(frozen=True, slots=True)
class ActivityListCriteria:
    """Filters for listing social account activity."""

    workspace_id: UUID
    cursor: str | None
    limit: int
    sort: str


@dataclass(frozen=True, slots=True)
class ActivityListPage:
    """Paged activity list result."""

    items: tuple[ActivityEventRecord, ...]
    next_cursor: str | None
    has_more: bool


@dataclass(frozen=True, slots=True)
class ConnectSocialAccountInput:
    """Input for completing a mock OAuth connection."""

    workspace_id: UUID
    platform_code: str
    authorization_code: str
    code_verifier: str
    redirect_uri: str
    state: str
    connected_by: UUID


@dataclass(frozen=True, slots=True)
class DefaultSettingsUpdate:
    """Partial update for account publishing defaults."""

    visibility: str | None = None
    hashtag_strategy: str | None = None
    auto_publish: bool | None = None
    ai_optimization: bool | None = None
    auto_schedule: bool | None = None
    url_tracking: bool | None = None


@dataclass(frozen=True, slots=True)
class SocialAccountUpdate:
    """Partial update for a connected social account."""

    publishing_enabled: bool | None = None
    default_settings: DefaultSettingsUpdate | None = None


class ISocialAccountRepository(Protocol):
    """Repository port for social account operations."""

    async def list_accounts(
        self, criteria: SocialAccountListCriteria
    ) -> SocialAccountListPage:
        """List active social accounts for a workspace."""

    async def get_by_id(
        self, *, workspace_id: UUID, account_id: UUID
    ) -> SocialAccountRecord | None:
        """Return one active social account."""

    async def list_enabled_platforms(self) -> tuple[SocialPlatformRecord, ...]:
        """Return globally enabled social platforms."""

    async def get_platform_by_code(self, platform_code: str) -> SocialPlatformRecord | None:
        """Return one platform by code."""

    async def connect_account(self, connection: ConnectSocialAccountInput) -> SocialAccountRecord:
        """Complete OAuth and create or refresh a connected account."""

    async def disconnect_account(
        self,
        *,
        workspace_id: UUID,
        account_id: UUID,
        updated_by: UUID,
    ) -> SocialAccountRecord:
        """Disconnect a social account."""

    async def refresh_account(
        self,
        *,
        workspace_id: UUID,
        account_id: UUID,
        updated_by: UUID,
    ) -> SocialAccountRecord:
        """Refresh account health and sync metadata."""

    async def update_account(
        self,
        *,
        workspace_id: UUID,
        account_id: UUID,
        expected_version: int,
        update: SocialAccountUpdate,
        updated_by: UUID,
    ) -> SocialAccountRecord:
        """Update account settings with optimistic concurrency."""

    async def list_activity(self, criteria: ActivityListCriteria) -> ActivityListPage:
        """List social account activity events for a workspace."""
