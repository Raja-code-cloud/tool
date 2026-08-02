"""Search request DTOs."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from cloud_content_hub.application.shared.dto.base import ApplicationDto


class SearchEntityTypeDto(StrEnum):
    ASSET = "asset"
    CONTENT = "content"
    PUBLICATION = "publication"


class SearchFiltersDto(ApplicationDto):
    """Advanced search filter projection."""

    entity_types: frozenset[SearchEntityTypeDto] = frozenset()
    asset_types: frozenset[str] = frozenset()
    lifecycle_statuses: frozenset[str] = frozenset()
    content_origins: frozenset[str] = frozenset()
    publication_statuses: frozenset[str] = frozenset()
    owner_id: UUID | None = None
    project_id: UUID | None = None
    folder_id: UUID | None = None
    updated_after: datetime | None = None
    updated_before: datetime | None = None


class SearchRequestDto(ApplicationDto):
    """Shared search request shape."""

    query: str = Field(min_length=2, max_length=200)
    filters: SearchFiltersDto = Field(default_factory=SearchFiltersDto)
    cursor: str | None = None
    limit: int = Field(default=25, ge=1, le=100)
    sort: str = "relevance"


class SaveSearchRequestDto(ApplicationDto):
    """Request body for persisting a saved search."""

    name: str = Field(min_length=1, max_length=120)
    query: str = Field(min_length=2, max_length=200)
    filters: SearchFiltersDto = Field(default_factory=SearchFiltersDto)
    sort: str = Field(default="relevance", min_length=1, max_length=64)
    is_shared: bool = False


class SearchSuggestionsRequestDto(ApplicationDto):
    """Request body for autocomplete suggestions."""

    prefix: str = Field(min_length=1, max_length=200)
    entity_types: frozenset[SearchEntityTypeDto] = frozenset()
    limit: int = Field(default=10, ge=1, le=25)
