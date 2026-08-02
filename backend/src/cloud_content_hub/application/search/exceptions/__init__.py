"""Search application exceptions."""

from cloud_content_hub.application.search.exceptions.search_errors import (
    SavedSearchNotFoundError,
    SavedSearchOwnershipError,
    SearchAccessDeniedError,
    UnsupportedSearchFilterError,
    UnsupportedSearchSortError,
)

__all__ = [
    "SavedSearchNotFoundError",
    "SavedSearchOwnershipError",
    "SearchAccessDeniedError",
    "UnsupportedSearchFilterError",
    "UnsupportedSearchSortError",
]
