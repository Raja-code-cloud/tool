"""Search response DTOs."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field

from cloud_content_hub.application.search.dto.requests import SearchEntityTypeDto, SearchFiltersDto
from cloud_content_hub.application.shared.dto.base import ApplicationDto, ResourceBaseDto


class SearchSuggestionKindDto(StrEnum):
    QUERY = "query"
    ENTITY = "entity"


class SearchResult(ApplicationDto):
    """Unified search hit returned by query handlers."""

    entity_type: SearchEntityTypeDto
    entity_id: UUID
    title: str
    summary: str | None = None
    score: float | None = None
    highlight: str | None = None
    updated_at: datetime
    metadata: dict[str, Any] = Field(default_factory=dict)


class SearchResponse(ApplicationDto):
    """Paged search results envelope."""

    items: tuple[SearchResult, ...]
    query: str
    filters: SearchFiltersDto
    page_next_cursor: str | None = None
    page_has_more: bool = False
    page_limit: int = Field(ge=1, le=100)


class SearchSuggestion(ApplicationDto):
    """Autocomplete suggestion returned by the suggestions query."""

    text: str
    kind: SearchSuggestionKindDto
    entity_type: SearchEntityTypeDto | None = None
    entity_id: UUID | None = None
    score: float | None = None


class SavedSearchResponse(ResourceBaseDto):
    """Persisted saved search projection."""

    owner_id: UUID
    name: str
    query: str
    filters: SearchFiltersDto
    sort: str
    is_shared: bool


class RecentSearchResponse(ApplicationDto):
    """Recent search history entry projection."""

    id: UUID
    query: str
    filters: SearchFiltersDto
    executed_at: datetime
