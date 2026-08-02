"""Administration command definitions."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from cloud_content_hub.application.administration.dto.requests import (
    AssignRoleRequestDto,
    DisableMaintenanceModeRequestDto,
    EnableMaintenanceModeRequestDto,
    RefreshProviderHealthRequestDto,
    RemoveRoleRequestDto,
    UpdateWorkspaceSettingsRequestDto,
)


@dataclass(frozen=True, slots=True)
class EnableMaintenanceModeCommand:
    """Command to enable global maintenance mode."""

    request: EnableMaintenanceModeRequestDto
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class DisableMaintenanceModeCommand:
    """Command to disable global maintenance mode."""

    request: DisableMaintenanceModeRequestDto
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class AssignRoleCommand:
    """Command to assign a role to a workspace membership."""

    request: AssignRoleRequestDto
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RemoveRoleCommand:
    """Command to remove a role from a workspace membership."""

    request: RemoveRoleRequestDto
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class UpdateWorkspaceSettingsCommand:
    """Command to update workspace settings."""

    workspace_id: UUID
    expected_version: int
    request: UpdateWorkspaceSettingsRequestDto
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RefreshProviderHealthCommand:
    """Command to refresh provider health checks."""

    request: RefreshProviderHealthRequestDto
    workspace_id: UUID | None
    idempotency_key: str
