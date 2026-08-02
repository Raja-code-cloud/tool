"""Administration-specific application exceptions."""

from cloud_content_hub.application.administration.exceptions.administration_errors import (
    AdministrationAccessDeniedError,
    FeatureFlagNotFoundError,
    GlobalAdminRequiredError,
    MaintenanceModeStateError,
    MembershipNotFoundError,
    RoleHierarchyViolationError,
    RoleNotFoundError,
    UserNotFoundError,
    WorkspaceAdminScopeError,
    WorkspaceNotFoundError,
)

__all__ = [
    "AdministrationAccessDeniedError",
    "FeatureFlagNotFoundError",
    "GlobalAdminRequiredError",
    "MaintenanceModeStateError",
    "MembershipNotFoundError",
    "RoleHierarchyViolationError",
    "RoleNotFoundError",
    "UserNotFoundError",
    "WorkspaceAdminScopeError",
    "WorkspaceNotFoundError",
]
