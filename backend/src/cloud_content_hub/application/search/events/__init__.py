"""Search domain events raised by command and query handlers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from cloud_content_hub.application.search.interfaces.suggestion_repository import SearchEntityType


@dataclass(frozen=True, slots=True)
class SearchExecuted:
    """Raised when a search query completes successfully."""

    workspace_id: UUID
    user_id: UUID
    query: str
    entity_types: tuple[SearchEntityType, ...]
    result_count: int
    filter_spec: dict[str, Any]
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class SavedSearchCreated:
    """Raised when a saved search is created."""

    workspace_id: UUID
    saved_search_id: UUID
    owner_id: UUID
    actor_id: UUID
    name: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class SavedSearchDeleted:
    """Raised when a saved search is deleted."""

    workspace_id: UUID
    saved_search_id: UUID
    owner_id: UUID
    actor_id: UUID
    version: int
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class RecentSearchCleared:
    """Raised when a user clears recent search history."""

    workspace_id: UUID
    user_id: UUID
    actor_id: UUID
    cleared_count: int
    occurred_at: datetime


SearchDomainEvent = SearchExecuted | SavedSearchCreated | SavedSearchDeleted | RecentSearchCleared

__all__ = [
    "RecentSearchCleared",
    "SavedSearchCreated",
    "SavedSearchDeleted",
    "SearchDomainEvent",
    "SearchExecuted",
]
