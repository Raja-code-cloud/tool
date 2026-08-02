"""Administration domain events raised by command handlers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from cloud_content_hub.application.administration.interfaces.provider_health_port import (
    ProviderType,
)


@dataclass(frozen=True, slots=True)
class MaintenanceModeEnabled:
    """Raised when global maintenance mode is enabled."""

    actor_id: UUID
    message: str | None
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class MaintenanceModeDisabled:
    """Raised when global maintenance mode is disabled."""

    actor_id: UUID
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class RoleAssigned:
    """Raised when a role is assigned to a workspace membership."""

    workspace_id: UUID
    membership_id: UUID
    role_id: UUID
    actor_id: UUID
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class RoleRemoved:
    """Raised when a role is removed from a workspace membership."""

    workspace_id: UUID
    membership_id: UUID
    role_id: UUID
    actor_id: UUID
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class WorkspaceUpdated:
    """Raised when workspace settings are updated."""

    workspace_id: UUID
    actor_id: UUID
    version: int
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class ProviderHealthChecked:
    """Raised when provider health is refreshed."""

    provider_type: ProviderType
    provider_code: str
    actor_id: UUID
    occurred_at: datetime


AdministrationDomainEvent = (
    MaintenanceModeEnabled
    | MaintenanceModeDisabled
    | RoleAssigned
    | RoleRemoved
    | WorkspaceUpdated
    | ProviderHealthChecked
)

__all__ = [
    "AdministrationDomainEvent",
    "MaintenanceModeDisabled",
    "MaintenanceModeEnabled",
    "ProviderHealthChecked",
    "RoleAssigned",
    "RoleRemoved",
    "WorkspaceUpdated",
]
