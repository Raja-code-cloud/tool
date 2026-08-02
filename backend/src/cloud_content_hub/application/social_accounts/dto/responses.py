"""Social account response DTOs."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from cloud_content_hub.application.shared.dto.base import ApplicationDto, ResourceBaseDto


class ConnectionStatusDto(StrEnum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class HealthStatusDto(StrEnum):
    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    NEEDS_REAUTH = "needs_reauth"


class OAuthTokenStatusDto(StrEnum):
    ACTIVE = "active"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    RENEW_REQUIRED = "renew_required"
    REVOKED = "revoked"


class PlatformStatusDto(StrEnum):
    ENABLED = "enabled"
    DISABLED = "disabled"
    COMING_SOON = "coming_soon"


class ActivityTypeDto(StrEnum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    PUBLISH_SUCCESS = "publish_success"
    PUBLISH_FAILED = "publish_failed"
    PERMISSION_CHANGED = "permission_changed"


class DefaultSettingsDto(ApplicationDto):
    """Publishing defaults returned with a social account."""

    visibility: str | None = None
    hashtags: str | None = None
    auto_publish: bool = False
    ai_optimization: bool = False
    auto_schedule: bool = False
    url_tracking: bool = False


class SocialAccountDto(ResourceBaseDto):
    """Connected social account projection."""

    platform_id: str
    platform_name: str
    connection_status: ConnectionStatusDto
    health_status: HealthStatusDto
    token_status: OAuthTokenStatusDto | None = None
    account_name: str
    display_name: str
    username: str | None = None
    account_type: str | None = None
    avatar_fallback: str
    avatar_hue: int = Field(ge=0, le=359)
    last_sync: datetime | None = None
    connected_since: datetime | None = None
    publishing_enabled: bool
    followers: int = Field(ge=0, default=0)
    permissions: tuple[str, ...] = ()
    default_audience: str | None = None
    timezone: str
    default_settings: DefaultSettingsDto


class SocialPlatformDto(ApplicationDto):
    """Enabled social platform catalog entry."""

    id: UUID
    code: str
    name: str
    status: PlatformStatusDto
    api_version: str | None = None


class AuthorizeSocialAccountResponseDto(ApplicationDto):
    """OAuth authorization bootstrap payload."""

    authorization_url: str
    state: str
    code_verifier: str
    platform_code: str


class ActivityEventDto(ApplicationDto):
    """Social account activity timeline entry."""

    id: UUID
    account_id: UUID
    platform_name: str
    type: ActivityTypeDto
    message: str
    timestamp: datetime
