"""Notification-specific application exceptions."""

from cloud_content_hub.core.errors import ClientError, ValidationError


class NotificationNotFoundError(ClientError):
    default_code = "resource_not_found"
    default_detail = "The requested notification was not found."


class NotificationTypeNotFoundError(ValidationError):
    default_code = "validation_failed"
    default_detail = "The notification type code is not recognized."


class InvalidRecipientError(ValidationError):
    default_code = "validation_failed"
    default_detail = "The notification recipient is not valid for this workspace."


class ReadTimestampImmutableError(ClientError):
    default_code = "invalid_state_transition"
    default_detail = "The notification read timestamp cannot be cleared once set."


class NotificationAlreadyArchivedError(ClientError):
    default_code = "invalid_state_transition"
    default_detail = "The notification is already archived."
