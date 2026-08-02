"""Administration-specific application exceptions."""

from cloud_content_hub.core.errors import AuthorizationError, ClientError, ValidationError


class AdministrationAccessDeniedError(AuthorizationError):
    default_code = "permission_denied"
    default_detail = "Administrative access is required."


class GlobalAdminRequiredError(AuthorizationError):
    default_code = "permission_denied"
    default_detail = "Global administrator access is required."


class WorkspaceAdminScopeError(AuthorizationError):
    default_code = "permission_denied"
    default_detail = "Workspace administrators cannot modify global settings."


class UserNotFoundError(ClientError):
    default_code = "resource_not_found"
    default_detail = "The requested user was not found."


class WorkspaceNotFoundError(ClientError):
    default_code = "resource_not_found"
    default_detail = "The requested workspace was not found."


class RoleNotFoundError(ClientError):
    default_code = "resource_not_found"
    default_detail = "The requested role was not found."


class MembershipNotFoundError(ClientError):
    default_code = "resource_not_found"
    default_detail = "The requested workspace membership was not found."


class FeatureFlagNotFoundError(ClientError):
    default_code = "resource_not_found"
    default_detail = "The requested feature flag was not found."


class RoleHierarchyViolationError(ValidationError):
    default_code = "validation_failed"
    default_detail = "The role assignment violates role hierarchy rules."


class MaintenanceModeStateError(ClientError):
    default_code = "invalid_state_transition"
    default_detail = "Maintenance mode is already in the requested state."
