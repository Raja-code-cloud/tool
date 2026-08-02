"""Administration request DTOs."""

from __future__ import annotations

from uuid import UUID

from pydantic import Field

from cloud_content_hub.application.administration.interfaces.provider_health_port import (
    ProviderType,
)
from cloud_content_hub.application.shared.dto.base import ApplicationDto


class EnableMaintenanceModeRequestDto(ApplicationDto):
    """Request payload for enabling global maintenance mode."""

    message: str | None = Field(default=None, max_length=500)


class DisableMaintenanceModeRequestDto(ApplicationDto):
    """Request payload for disabling global maintenance mode."""


class AssignRoleRequestDto(ApplicationDto):
    """Request payload for assigning a role to a workspace membership."""

    workspace_id: UUID
    membership_id: UUID
    role_id: UUID


class RemoveRoleRequestDto(ApplicationDto):
    """Request payload for removing a role from a workspace membership."""

    workspace_id: UUID
    membership_id: UUID
    role_id: UUID


class UpdateWorkspaceSettingsRequestDto(ApplicationDto):
    """Request payload for updating workspace settings."""

    name: str | None = Field(default=None, min_length=1, max_length=200)
    time_zone: str | None = Field(default=None, min_length=1, max_length=64)
    retention_policy_days: int | None = Field(default=None, ge=1)


class RefreshProviderHealthRequestDto(ApplicationDto):
    """Request payload for refreshing provider health checks."""

    provider_types: tuple[ProviderType, ...] = Field(default_factory=tuple)
