"""Search business validation."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from cloud_content_hub.application.search.exceptions.search_errors import (
    SavedSearchOwnershipError,
    SearchAccessDeniedError,
    UnsupportedSearchFilterError,
    UnsupportedSearchSortError,
)
from cloud_content_hub.application.search.interfaces.saved_search_repository import (
    SavedSearchRecord,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.core.errors import ValidationError

_ASSET_SORTS = frozenset({"relevance", "-updated_at", "updated_at", "-created_at", "created_at"})
_CONTENT_SORTS = frozenset(
    {"relevance", "-updated_at", "updated_at", "-created_at", "created_at", "title", "-title"}
)
_PUBLICATION_SORTS = frozenset({"relevance", "-updated_at", "updated_at"})
_GLOBAL_SORTS = frozenset({"relevance", "-updated_at", "updated_at"})

_SUPPORTED_ASSET_TYPES = frozenset({"article", "video", "poster", "thumbnail"})
_SUPPORTED_LIFECYCLE_STATUSES = frozenset({"draft", "active", "archived"})
_SUPPORTED_CONTENT_ORIGINS = frozenset({"user", "ai", "import", "regeneration"})
_SUPPORTED_PUBLICATION_STATUSES = frozenset(
    {"draft", "ready", "in_progress", "completed", "partially_failed", "cancelled"}
)

_SEARCH_READ_PERMISSIONS = ("assets:read", "content:read", "publishing:read")


def require_any_search_permission(actor: ActorContext) -> None:
    """Raise when the actor cannot read any searchable resource type."""

    if any(actor.has_permission(permission) for permission in _SEARCH_READ_PERMISSIONS):
        return
    raise SearchAccessDeniedError(
        detail="At least one search read permission is required.",
    )


def normalize_search_query(query: str) -> str:
    """Normalize and validate a full-text search query."""

    normalized = query.strip()
    if len(normalized) < 2 or len(normalized) > 200:
        raise ValidationError(detail="Search query must be between 2 and 200 characters.")
    return normalized


def normalize_suggestion_prefix(prefix: str) -> str:
    """Normalize and validate an autocomplete prefix."""

    normalized = prefix.strip()
    if len(normalized) < 1 or len(normalized) > 200:
        raise ValidationError(detail="Suggestion prefix must be between 1 and 200 characters.")
    return normalized


def validate_page_size(limit: int) -> None:
    """Validate cursor page size."""

    if limit < 1 or limit > 100:
        raise ValidationError(detail="Page size must be between 1 and 100.")


def validate_suggestion_limit(limit: int) -> None:
    """Validate suggestion result count."""

    if limit < 1 or limit > 25:
        raise ValidationError(detail="Suggestion limit must be between 1 and 25.")


def validate_recent_search_limit(limit: int) -> None:
    """Validate recent search history count."""

    if limit < 1 or limit > 50:
        raise ValidationError(detail="Recent search limit must be between 1 and 50.")


def validate_asset_sort(sort: str) -> None:
    """Validate asset search sort allowlist."""

    if sort not in _ASSET_SORTS:
        raise UnsupportedSearchSortError(
            detail=f"Asset sort '{sort}' is not supported.",
            parameters={"sort": sort},
        )


def validate_content_sort(sort: str) -> None:
    """Validate content search sort allowlist."""

    if sort not in _CONTENT_SORTS:
        raise UnsupportedSearchSortError(
            detail=f"Content sort '{sort}' is not supported.",
            parameters={"sort": sort},
        )


def validate_publication_sort(sort: str) -> None:
    """Validate publication search sort allowlist."""

    if sort not in _PUBLICATION_SORTS:
        raise UnsupportedSearchSortError(
            detail=f"Publication sort '{sort}' is not supported.",
            parameters={"sort": sort},
        )


def validate_global_sort(sort: str) -> None:
    """Validate global search sort allowlist."""

    if sort not in _GLOBAL_SORTS:
        raise UnsupportedSearchSortError(
            detail=f"Global sort '{sort}' is not supported.",
            parameters={"sort": sort},
        )


def validate_asset_types(asset_types: frozenset[str]) -> None:
    """Validate supported asset type filters."""

    unsupported = asset_types - _SUPPORTED_ASSET_TYPES
    if unsupported:
        raise UnsupportedSearchFilterError(
            detail="One or more asset type filters are not supported.",
            parameters={"assetTypes": sorted(unsupported)},
        )


def validate_lifecycle_statuses(lifecycle_statuses: frozenset[str]) -> None:
    """Validate supported lifecycle status filters."""

    unsupported = lifecycle_statuses - _SUPPORTED_LIFECYCLE_STATUSES
    if unsupported:
        raise UnsupportedSearchFilterError(
            detail="One or more lifecycle status filters are not supported.",
            parameters={"lifecycleStatuses": sorted(unsupported)},
        )


def validate_content_origins(origins: frozenset[str]) -> None:
    """Validate supported content origin filters."""

    unsupported = origins - _SUPPORTED_CONTENT_ORIGINS
    if unsupported:
        raise UnsupportedSearchFilterError(
            detail="One or more content origin filters are not supported.",
            parameters={"contentOrigins": sorted(unsupported)},
        )


def validate_publication_statuses(statuses: frozenset[str]) -> None:
    """Validate supported publication status filters."""

    unsupported = statuses - _SUPPORTED_PUBLICATION_STATUSES
    if unsupported:
        raise UnsupportedSearchFilterError(
            detail="One or more publication status filters are not supported.",
            parameters={"publicationStatuses": sorted(unsupported)},
        )


def validate_updated_range(
    *,
    updated_after: datetime | None,
    updated_before: datetime | None,
) -> None:
    """Validate updated-at filter range."""

    if updated_after is not None and updated_before is not None and updated_after >= updated_before:
        raise ValidationError(detail="updatedAfter must be earlier than updatedBefore.")


def validate_saved_search_name(name: str) -> str:
    """Validate and normalize a saved search name."""

    normalized = name.strip()
    if len(normalized) < 1 or len(normalized) > 120:
        raise ValidationError(detail="Saved search name must be between 1 and 120 characters.")
    return normalized


def validate_saved_search_owner(
    saved_search: SavedSearchRecord,
    *,
    actor: ActorContext,
) -> None:
    """Ensure the actor owns the saved search."""

    if saved_search.owner_id != actor.user_id:
        raise SavedSearchOwnershipError(
            parameters={"savedSearchId": str(saved_search.id)},
        )


def validate_saved_search_ownership(
    saved_search: SavedSearchRecord,
    *,
    actor: ActorContext,
) -> None:
    """Ensure the actor owns the saved search or it is shared."""

    if saved_search.owner_id != actor.user_id and not saved_search.is_shared:
        raise SavedSearchOwnershipError(
            parameters={"savedSearchId": str(saved_search.id)},
        )


def filters_to_spec(
    *,
    entity_types: frozenset[str] | None = None,
    asset_types: frozenset[str] | None = None,
    lifecycle_statuses: frozenset[str] | None = None,
    content_origins: frozenset[str] | None = None,
    publication_statuses: frozenset[str] | None = None,
    owner_id: str | None = None,
    project_id: str | None = None,
    folder_id: str | None = None,
    updated_after: datetime | None = None,
    updated_before: datetime | None = None,
) -> dict[str, Any]:
    """Serialize active filters to a JSON-safe specification."""

    spec: dict[str, Any] = {}
    if entity_types:
        spec["entityTypes"] = sorted(entity_types)
    if asset_types:
        spec["assetTypes"] = sorted(asset_types)
    if lifecycle_statuses:
        spec["lifecycleStatuses"] = sorted(lifecycle_statuses)
    if content_origins:
        spec["contentOrigins"] = sorted(content_origins)
    if publication_statuses:
        spec["publicationStatuses"] = sorted(publication_statuses)
    if owner_id is not None:
        spec["ownerId"] = owner_id
    if project_id is not None:
        spec["projectId"] = project_id
    if folder_id is not None:
        spec["folderId"] = folder_id
    if updated_after is not None:
        spec["updatedAfter"] = updated_after.isoformat()
    if updated_before is not None:
        spec["updatedBefore"] = updated_before.isoformat()
    return spec
