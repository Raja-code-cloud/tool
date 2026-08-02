"""Search-specific application exceptions."""

from cloud_content_hub.core.errors import ClientError, ValidationError


class SavedSearchNotFoundError(ClientError):
    default_code = "resource_not_found"
    default_detail = "The requested saved search was not found."


class SavedSearchOwnershipError(ValidationError):
    default_code = "validation_failed"
    default_detail = "The saved search does not belong to the current user."


class UnsupportedSearchFilterError(ValidationError):
    default_code = "validation_failed"
    default_detail = "One or more search filters are not supported."


class UnsupportedSearchSortError(ValidationError):
    default_code = "validation_failed"
    default_detail = "The requested sort field is not supported."


class SearchAccessDeniedError(ClientError):
    default_code = "permission_denied"
    default_detail = "The actor lacks permission to search the requested resources."
