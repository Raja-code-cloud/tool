"""Administration business validation."""

from __future__ import annotations

from uuid import UUID

from cloud_content_hub.application.administration.dto.requests import (
    UpdateWorkspaceSettingsRequestDto,
)
from cloud_content_hub.application.administration.exceptions.administration_errors import (
    FeatureFlagNotFoundError,
    GlobalAdminRequiredError,
    MaintenanceModeStateError,
    RoleHierarchyViolationError,
    WorkspaceAdminScopeError,
    WorkspaceNotFoundError,
)
from cloud_content_hub.application.administration.interfaces.administration_repository import (
    FeatureFlagRecord,
    RoleRecord,
)
from cloud_content_hub.application.administration.interfaces.provider_health_port import (
    ProviderType,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.core.errors import ValidationError

ROLE_RANK: dict[str, int] = {
    "owner": 100,
    "admin": 90,
    "billing_admin": 85,
    "editor": 50,
    "reviewer": 40,
    "viewer": 10,
    "member": 5,
}

FEATURE_FLAG_KEY_PREFIX = "feature."


def is_global_admin(actor: ActorContext) -> bool:
    """Return whether the actor is a global administrator."""

    return actor.has_permission("admin:*") or actor.has_permission("*")


def require_admin_read(actor: ActorContext) -> None:
    """Require read access to administration queries."""

    require_permission(actor, "admin:read")


def require_admin_write(actor: ActorContext) -> None:
    """Require write access to administration commands."""

    require_permission(actor, "admin:write")


def require_global_admin(actor: ActorContext) -> None:
    """Require global administrator privileges."""

    require_admin_write(actor)
    if not is_global_admin(actor):
        raise GlobalAdminRequiredError()


def validate_workspace_admin_scope(actor: ActorContext, *, workspace_id: UUID) -> None:
    """Ensure workspace administrators remain within their workspace scope."""

    if is_global_admin(actor):
        return
    if actor.workspace_id != workspace_id:
        raise WorkspaceAdminScopeError(
            detail="Workspace administrators may only manage their assigned workspace.",
            parameters={"workspaceId": str(workspace_id)},
        )


def validate_global_only_operation(actor: ActorContext) -> None:
    """Ensure the operation is restricted to global administrators."""

    require_global_admin(actor)


def validate_workspace_settings_update(
    request: UpdateWorkspaceSettingsRequestDto,
) -> None:
    """Validate that at least one workspace setting is being updated."""

    if request.name is None and request.time_zone is None and request.retention_policy_days is None:
        raise ValidationError(detail="At least one workspace setting must be provided.")


def validate_workspace_exists(workspace: object | None, *, workspace_id: UUID) -> None:
    """Raise when the workspace does not exist."""

    if workspace is None:
        raise WorkspaceNotFoundError(parameters={"workspaceId": str(workspace_id)})


def validate_feature_flag_exists(flag: FeatureFlagRecord | None, *, key: str) -> FeatureFlagRecord:
    """Raise when the feature flag does not exist."""

    if flag is None:
        raise FeatureFlagNotFoundError(parameters={"key": key})
    return flag


def validate_feature_flag_key(key: str) -> None:
    """Validate that a key follows the feature flag naming convention."""

    if not key.startswith(FEATURE_FLAG_KEY_PREFIX):
        raise ValidationError(
            detail="Feature flag keys must use the 'feature.' prefix.",
            parameters={"key": key},
        )


def validate_maintenance_transition(*, current_enabled: bool, requested_enabled: bool) -> None:
    """Raise when maintenance mode is already in the requested state."""

    if current_enabled == requested_enabled:
        state = "enabled" if requested_enabled else "disabled"
        raise MaintenanceModeStateError(
            detail=f"Maintenance mode is already {state}.",
            parameters={"enabled": requested_enabled},
        )


def role_rank(role: RoleRecord) -> int:
    """Return the hierarchy rank for a role."""

    return ROLE_RANK.get(role.code.lower(), 0)


def validate_role_hierarchy(
    *,
    actor_roles: tuple[RoleRecord, ...],
    target_role: RoleRecord,
    bypass: bool = False,
) -> None:
    """Ensure the actor may assign or remove the target role."""

    if bypass:
        return
    if not actor_roles:
        raise RoleHierarchyViolationError(detail="Actor has no assignable administrative roles.")
    actor_rank = max(role_rank(role) for role in actor_roles)
    target_rank = role_rank(target_role)
    if actor_rank < target_rank:
        raise RoleHierarchyViolationError(
            detail="Actors may not assign or remove roles above their hierarchy rank.",
            parameters={"roleCode": target_role.code},
        )
    if target_role.is_system and actor_rank < ROLE_RANK["admin"]:
        raise RoleHierarchyViolationError(
            detail="Only administrators may manage system roles.",
            parameters={"roleCode": target_role.code},
        )


def validate_role_workspace_scope(*, role: RoleRecord, workspace_id: UUID) -> None:
    """Ensure a role belongs to the requested workspace or is a system role."""

    if role.is_system:
        return
    if role.workspace_id != workspace_id:
        raise RoleHierarchyViolationError(
            detail="Custom roles must belong to the target workspace.",
            parameters={"roleId": str(role.id), "workspaceId": str(workspace_id)},
        )


def validate_provider_types(provider_types: tuple[ProviderType, ...]) -> frozenset[ProviderType]:
    """Validate and normalize provider type filters."""

    if not provider_types:
        return frozenset(ProviderType)
    return frozenset(provider_types)
