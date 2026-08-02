"""Administration repository port and read models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Protocol
from uuid import UUID


class UserStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"
    ANONYMIZED = "anonymized"


class WorkspaceStatus(StrEnum):
    PROVISIONING = "provisioning"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSING = "closing"
    CLOSED = "closed"


class AuditOutcome(StrEnum):
    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"


class AuditActorType(StrEnum):
    USER = "user"
    SERVICE = "service"
    SYSTEM = "system"
    PROVIDER = "provider"


class SettingScopeType(StrEnum):
    ORGANIZATION = "organization"
    WORKSPACE = "workspace"
    USER = "user"
    PROJECT = "project"
    SOCIAL_ACCOUNT = "social_account"


@dataclass(frozen=True, slots=True)
class UserRecord:
    """User administration read model."""

    id: UUID
    version: int
    created_at: datetime
    updated_at: datetime
    email: str | None
    display_name: str
    locale: str
    time_zone: str
    status: UserStatus


@dataclass(frozen=True, slots=True)
class UserProfileUpdate:
    """User profile mutation input."""

    user_id: UUID
    expected_version: int
    display_name: str | None
    locale: str | None
    time_zone: str | None
    avatar_object_key: str | None
    updated_by: UUID


@dataclass(frozen=True, slots=True)
class WorkspaceRecord:
    """Workspace administration read model."""

    id: UUID
    organization_id: UUID
    version: int
    created_at: datetime
    updated_at: datetime
    name: str
    slug: str
    status: WorkspaceStatus
    time_zone: str
    retention_policy_days: int | None


@dataclass(frozen=True, slots=True)
class RoleRecord:
    """Role read model for administration."""

    id: UUID
    workspace_id: UUID | None
    code: str
    name: str
    description: str | None
    is_system: bool


@dataclass(frozen=True, slots=True)
class MembershipRecord:
    """Workspace membership read model."""

    id: UUID
    workspace_id: UUID
    user_id: UUID
    status: str


@dataclass(frozen=True, slots=True)
class MembershipRoleRecord:
    """Assigned membership role read model."""

    workspace_id: UUID
    membership_id: UUID
    role_id: UUID


@dataclass(frozen=True, slots=True)
class FeatureFlagRecord:
    """Feature flag read model backed by typed settings."""

    key: str
    enabled: bool
    description: str
    owner: str | None
    purpose: str | None
    expires_at: datetime | None
    scope_type: SettingScopeType
    workspace_id: UUID | None


@dataclass(frozen=True, slots=True)
class MaintenanceModeRecord:
    """Global maintenance mode state."""

    enabled: bool
    message: str | None
    updated_at: datetime
    updated_by: UUID | None


@dataclass(frozen=True, slots=True)
class ApplicationConfigRecord:
    """Non-secret resolved application configuration entry."""

    key: str
    value: Any
    value_type: str
    scope_type: SettingScopeType
    workspace_id: UUID | None
    description: str


@dataclass(frozen=True, slots=True)
class AuditLogRecord:
    """Audit log entry read model."""

    id: UUID
    workspace_id: UUID | None
    organization_id: UUID | None
    actor_user_id: UUID | None
    actor_type: AuditActorType
    action: str
    target_type: str
    target_id: UUID | None
    outcome: AuditOutcome
    source: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class AuditSummaryRecord:
    """Aggregated audit query result."""

    total_count: int
    success_count: int
    failure_count: int
    denied_count: int
    recent_entries: tuple[AuditLogRecord, ...]


@dataclass(frozen=True, slots=True)
class UserSearchCriteria:
    """Structured user listing criteria."""

    workspace_id: UUID | None
    query: str | None = None
    statuses: frozenset[UserStatus] = frozenset()
    cursor: str | None = None
    limit: int = 25
    sort: str = "-updated_at"


@dataclass(frozen=True, slots=True)
class WorkspaceSearchCriteria:
    """Structured workspace listing criteria."""

    organization_id: UUID | None = None
    workspace_id: UUID | None = None
    query: str | None = None
    statuses: frozenset[WorkspaceStatus] = frozenset()
    cursor: str | None = None
    limit: int = 25
    sort: str = "-updated_at"


@dataclass(frozen=True, slots=True)
class AuditSearchCriteria:
    """Structured audit summary query criteria."""

    workspace_id: UUID | None
    organization_id: UUID | None = None
    actions: frozenset[str] = frozenset()
    outcomes: frozenset[AuditOutcome] = frozenset()
    occurred_after: datetime | None = None
    occurred_before: datetime | None = None
    limit: int = 25


@dataclass(frozen=True, slots=True)
class UserSearchPage:
    """Cursor-paged user search results."""

    items: tuple[UserRecord, ...]
    next_cursor: str | None
    has_more: bool


@dataclass(frozen=True, slots=True)
class WorkspaceSearchPage:
    """Cursor-paged workspace search results."""

    items: tuple[WorkspaceRecord, ...]
    next_cursor: str | None
    has_more: bool


@dataclass(frozen=True, slots=True)
class NewAuditLog:
    """Input for append-only audit evidence."""

    workspace_id: UUID | None
    organization_id: UUID | None
    actor_user_id: UUID | None
    actor_type: AuditActorType
    action: str
    target_type: str
    target_id: UUID | None
    outcome: AuditOutcome
    source: str
    safe_diff: dict[str, Any] | None = None
    request_id: str | None = None


@dataclass(frozen=True, slots=True)
class WorkspaceSettingsUpdate:
    """Mutable workspace settings input."""

    workspace_id: UUID
    expected_version: int
    name: str | None
    time_zone: str | None
    retention_policy_days: int | None
    updated_by: UUID


@dataclass(frozen=True, slots=True)
class RoleAssignment:
    """Role assignment input."""

    workspace_id: UUID
    membership_id: UUID
    role_id: UUID
    assigned_by: UUID


@dataclass(frozen=True, slots=True)
class RoleRemoval:
    """Role removal input."""

    workspace_id: UUID
    membership_id: UUID
    role_id: UUID
    removed_by: UUID


@dataclass(frozen=True, slots=True)
class MaintenanceModeUpdate:
    """Maintenance mode mutation input."""

    enabled: bool
    message: str | None
    updated_by: UUID


class IAdministrationRepository(Protocol):
    """Repository port for administration persistence."""

    async def list_users(self, criteria: UserSearchCriteria) -> UserSearchPage:
        """List users visible to the administrative scope."""

    async def get_user(self, user_id: UUID) -> UserRecord | None:
        """Return one user by identifier."""

    async def update_user_profile(self, update: UserProfileUpdate) -> UserRecord:
        """Update mutable profile fields for a user."""

    async def list_workspaces(self, criteria: WorkspaceSearchCriteria) -> WorkspaceSearchPage:
        """List workspaces visible to the administrative scope."""

    async def get_workspace(self, workspace_id: UUID) -> WorkspaceRecord | None:
        """Return one workspace by identifier."""

    async def update_workspace_settings(self, update: WorkspaceSettingsUpdate) -> WorkspaceRecord:
        """Update mutable workspace settings."""

    async def get_membership(
        self,
        *,
        workspace_id: UUID,
        membership_id: UUID,
    ) -> MembershipRecord | None:
        """Return one workspace membership."""

    async def get_role(
        self,
        *,
        role_id: UUID,
        workspace_id: UUID | None,
    ) -> RoleRecord | None:
        """Return one role scoped to a workspace or global catalog."""

    async def list_membership_roles(
        self,
        *,
        workspace_id: UUID,
        membership_id: UUID,
    ) -> tuple[RoleRecord, ...]:
        """Return roles currently assigned to a membership."""

    async def list_actor_roles(
        self,
        *,
        workspace_id: UUID,
        user_id: UUID,
    ) -> tuple[RoleRecord, ...]:
        """Return roles assigned to an actor within a workspace."""

    async def assign_role(self, assignment: RoleAssignment) -> MembershipRoleRecord:
        """Assign a role to a workspace membership."""

    async def remove_role(self, removal: RoleRemoval) -> None:
        """Remove a role from a workspace membership."""

    async def append_audit(self, entry: NewAuditLog) -> AuditLogRecord:
        """Append an immutable audit log entry."""

    async def get_audit_summary(self, criteria: AuditSearchCriteria) -> AuditSummaryRecord:
        """Return aggregated audit evidence for a scope."""

    async def list_feature_flags(
        self, *, workspace_id: UUID | None
    ) -> tuple[FeatureFlagRecord, ...]:
        """Return resolved feature flags for a scope."""

    async def get_feature_flag(
        self, *, key: str, workspace_id: UUID | None
    ) -> FeatureFlagRecord | None:
        """Return one feature flag by key."""

    async def get_maintenance_mode(self) -> MaintenanceModeRecord:
        """Return the current global maintenance mode state."""

    async def set_maintenance_mode(self, update: MaintenanceModeUpdate) -> MaintenanceModeRecord:
        """Enable or disable global maintenance mode."""

    async def list_application_config(
        self,
        *,
        workspace_id: UUID | None,
    ) -> tuple[ApplicationConfigRecord, ...]:
        """Return non-secret resolved application configuration."""
