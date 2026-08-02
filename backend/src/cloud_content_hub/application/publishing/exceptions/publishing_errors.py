"""Publishing-specific application exceptions."""

from cloud_content_hub.core.errors import ClientError, ConflictError


class PublicationNotFoundError(ClientError):
    default_code = "resource_not_found"
    default_detail = "The requested publication was not found."


class PublicationValidationError(ClientError):
    default_code = "validation_failed"
    default_detail = "The publication request failed validation."


class ApprovalRequiredError(ConflictError):
    default_code = "approval_required"
    default_detail = "Publication requires approval before dispatch."


class SocialAccountUnhealthyError(ConflictError):
    default_code = "social_account_unhealthy"
    default_detail = "One or more social accounts are unhealthy."
