"""Search query definitions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from cloud_content_hub.application.assets.interfaces.asset_repository import (
    AssetLifecycleStatus,
    AssetType,
)
from cloud_content_hub.application.content.interfaces.content_repository import (
    ContentLifecycleStatus,
    ContentOrigin,
)
from cloud_content_hub.application.search.interfaces.publication_search_repository import (
    PublicationStatus,
)
from cloud_content_hub.application.search.interfaces.suggestion_repository import SearchEntityType


@dataclass(frozen=True, slots=True)
class SearchAllQuery:
    """Query to search across all accessible entity types."""

    query: str
    entity_types: frozenset[SearchEntityType] = frozenset()
    asset_types: frozenset[AssetType] = frozenset()
    lifecycle_statuses: frozenset[AssetLifecycleStatus] = frozenset()
    content_lifecycle_statuses: frozenset[ContentLifecycleStatus] = frozenset()
    content_origins: frozenset[ContentOrigin] = frozenset()
    publication_statuses: frozenset[PublicationStatus] = frozenset()
    owner_id: UUID | None = None
    project_id: UUID | None = None
    folder_id: UUID | None = None
    updated_after: datetime | None = None
    updated_before: datetime | None = None
    cursor: str | None = None
    limit: int = 25
    sort: str = "relevance"


@dataclass(frozen=True, slots=True)
class SearchAssetsQuery:
    """Query to search assets."""

    query: str
    asset_types: frozenset[AssetType] = frozenset()
    lifecycle_statuses: frozenset[AssetLifecycleStatus] = frozenset()
    owner_id: UUID | None = None
    project_id: UUID | None = None
    folder_id: UUID | None = None
    cursor: str | None = None
    limit: int = 25
    sort: str = "relevance"


@dataclass(frozen=True, slots=True)
class SearchContentQuery:
    """Query to search content."""

    query: str
    lifecycle_statuses: frozenset[ContentLifecycleStatus] = frozenset()
    origins: frozenset[ContentOrigin] = frozenset()
    cursor: str | None = None
    limit: int = 25
    sort: str = "-updated_at"


@dataclass(frozen=True, slots=True)
class SearchPublicationsQuery:
    """Query to search publications."""

    query: str
    statuses: frozenset[PublicationStatus] = frozenset()
    cursor: str | None = None
    limit: int = 25
    sort: str = "relevance"


@dataclass(frozen=True, slots=True)
class GetRecentSearchesQuery:
    """Query to retrieve recent searches for the current user."""

    limit: int = 10


@dataclass(frozen=True, slots=True)
class GetSavedSearchesQuery:
    """Query to retrieve saved searches visible to the current user."""

    include_shared: bool = True


@dataclass(frozen=True, slots=True)
class SearchSuggestionsQuery:
    """Query to retrieve autocomplete suggestions."""

    prefix: str
    entity_types: frozenset[SearchEntityType] = frozenset()
    limit: int = 10
