"""Social account record to DTO mappers."""

from __future__ import annotations

import hashlib

from cloud_content_hub.application.social_accounts.dto.responses import (
    ActivityEventDto,
    ActivityTypeDto,
    ConnectionStatusDto,
    DefaultSettingsDto,
    HealthStatusDto,
    OAuthTokenStatusDto,
    PlatformStatusDto,
    SocialAccountDto,
    SocialPlatformDto,
)
from cloud_content_hub.application.social_accounts.interfaces.social_account_repository import (
    ActivityEventRecord,
    DefaultSettingsRecord,
    SocialAccountRecord,
    SocialPlatformRecord,
)


class SocialAccountMapper:
    """Maps social account repository records to application DTOs."""

    @staticmethod
    def _avatar_fallback(display_name: str) -> str:
        parts = display_name.strip().split()
        if not parts:
            return "??"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return f"{parts[0][0]}{parts[-1][0]}".upper()

    @staticmethod
    def _avatar_hue(display_name: str) -> int:
        digest = hashlib.sha256(display_name.encode("utf-8")).hexdigest()
        return int(digest[:8], 16) % 360

    @staticmethod
    def _default_settings(record: DefaultSettingsRecord | None) -> DefaultSettingsDto:
        if record is None:
            return DefaultSettingsDto()
        return DefaultSettingsDto(
            visibility=record.visibility,
            hashtags=record.hashtag_strategy,
            auto_publish=record.auto_publish,
            ai_optimization=record.ai_optimization,
            auto_schedule=record.auto_schedule,
            url_tracking=record.url_tracking,
        )

    @classmethod
    def to_dto(cls, record: SocialAccountRecord) -> SocialAccountDto:
        token_status = (
            OAuthTokenStatusDto(record.token_status) if record.token_status is not None else None
        )
        return SocialAccountDto(
            id=record.id,
            version=record.version,
            created_at=record.created_at,
            updated_at=record.updated_at,
            platform_id=record.platform_code,
            platform_name=record.platform_name,
            connection_status=ConnectionStatusDto(record.connection_status),
            health_status=HealthStatusDto(record.health_status),
            token_status=token_status,
            account_name=record.account_name,
            display_name=record.display_name,
            username=record.username,
            account_type=record.account_type,
            avatar_fallback=cls._avatar_fallback(record.display_name),
            avatar_hue=cls._avatar_hue(record.display_name),
            last_sync=record.last_sync_at,
            connected_since=record.connected_at,
            publishing_enabled=record.publishing_enabled,
            followers=record.followers_count or 0,
            permissions=record.permissions,
            default_audience=record.default_audience,
            timezone=record.time_zone,
            default_settings=cls._default_settings(record.default_settings),
        )

    @staticmethod
    def to_platform_dto(record: SocialPlatformRecord) -> SocialPlatformDto:
        return SocialPlatformDto(
            id=record.id,
            code=record.code,
            name=record.name,
            status=PlatformStatusDto(record.status),
            api_version=record.api_version,
        )

    @staticmethod
    def to_activity_dto(record: ActivityEventRecord) -> ActivityEventDto:
        return ActivityEventDto(
            id=record.id,
            account_id=record.account_id,
            platform_name=record.platform_name,
            type=ActivityTypeDto(record.activity_type.value),
            message=record.message,
            timestamp=record.timestamp,
        )
