"""Content-specific application exceptions."""

from cloud_content_hub.core.errors import ClientError, ConflictError, ValidationError


class ContentNotFoundError(ClientError):
    default_code = "resource_not_found"
    default_detail = "The requested content was not found."


class ContentVersionNotFoundError(ClientError):
    default_code = "resource_not_found"
    default_detail = "The requested content version was not found."


class GenerationOutputNotFoundError(ClientError):
    default_code = "resource_not_found"
    default_detail = "The requested generation output was not found."


class GenerationValidationError(ValidationError):
    default_code = "validation_failed"
    default_detail = "The generation request failed validation."


class ContentStateError(ConflictError):
    default_code = "invalid_state_transition"
    default_detail = "The content is not in a valid state for this operation."


class ContentVersionConflictError(ConflictError):
    default_code = "version_conflict"
    default_detail = "The content changed after it was loaded."


class GenerationOutputStateError(ConflictError):
    default_code = "invalid_state_transition"
    default_detail = "The generation output is not in a valid state for this operation."
