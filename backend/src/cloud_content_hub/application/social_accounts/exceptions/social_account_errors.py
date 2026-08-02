"""Social account application exceptions."""

from cloud_content_hub.core.errors import ClientError, ConflictError


class SocialAccountNotFoundError(ClientError):
    default_code = "resource_not_found"
    default_detail = "The requested social account was not found."


class SocialPlatformNotFoundError(ClientError):
    default_code = "resource_not_found"
    default_detail = "The requested social platform was not found."


class SocialPlatformUnavailableError(ConflictError):
    default_code = "platform_unavailable"
    default_detail = "The requested social platform is not available for connection."


class SocialOAuthValidationError(ClientError):
    default_code = "oauth_validation_failed"
    default_detail = "The OAuth authorization request could not be validated."
