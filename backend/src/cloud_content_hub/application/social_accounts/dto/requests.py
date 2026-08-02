"""Social account request DTOs."""

from __future__ import annotations

from pydantic import Field, model_validator

from cloud_content_hub.application.shared.dto.base import ApplicationDto


class DefaultSettingsUpdateDto(ApplicationDto):
    """Partial update for account publishing defaults."""

    visibility: str | None = None
    hashtags: str | None = None
    auto_publish: bool | None = None
    ai_optimization: bool | None = None
    auto_schedule: bool | None = None
    url_tracking: bool | None = None


class AuthorizeSocialAccountRequestDto(ApplicationDto):
    """Begin OAuth authorization for a social platform."""

    platform_code: str = Field(min_length=1)
    redirect_uri: str = Field(min_length=1)


class ConnectSocialAccountRequestDto(ApplicationDto):
    """Complete OAuth authorization for a social platform."""

    platform_code: str = Field(min_length=1)
    authorization_code: str = Field(min_length=1)
    code_verifier: str = Field(min_length=1)
    redirect_uri: str = Field(min_length=1)
    state: str = Field(min_length=1)


class UpdateSocialAccountRequestDto(ApplicationDto):
    """Update mutable social account settings."""

    publishing_enabled: bool | None = None
    default_settings: DefaultSettingsUpdateDto | None = None

    @model_validator(mode="after")
    def validate_nonempty_patch(self) -> UpdateSocialAccountRequestDto:
        if self.publishing_enabled is None and self.default_settings is None:
            msg = "At least one field must be provided."
            raise ValueError(msg)
        return self
