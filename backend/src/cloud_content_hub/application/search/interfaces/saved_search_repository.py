"""Saved search repository port and read models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SavedSearchRecord:
    """Persisted saved search read model."""

    id: UUID
    workspace_id: UUID
    version: int
    created_at: datetime
    updated_at: datetime
    owner_id: UUID
    name: str
    query: str
    filter_spec: dict[str, Any]
    sort: str
    is_shared: bool


@dataclass(frozen=True, slots=True)
class NewSavedSearch:
    """Input for creating a saved search."""

    workspace_id: UUID
    owner_id: UUID
    name: str
    query: str
    filter_spec: dict[str, Any]
    sort: str
    is_shared: bool
    created_by: UUID


class ISavedSearchRepository(Protocol):
    """Repository port for workspace saved searches."""

    async def get_by_id(
        self,
        *,
        workspace_id: UUID,
        saved_search_id: UUID,
    ) -> SavedSearchRecord | None:
        """Return one active saved search scoped to the workspace."""

    async def list_for_workspace(
        self,
        *,
        workspace_id: UUID,
        owner_id: UUID | None = None,
        include_shared: bool = True,
    ) -> tuple[SavedSearchRecord, ...]:
        """Return saved searches visible to the caller within the workspace."""

    async def create(self, saved_search: NewSavedSearch) -> SavedSearchRecord:
        """Persist a new saved search."""

    async def soft_delete(
        self,
        *,
        workspace_id: UUID,
        saved_search_id: UUID,
        expected_version: int,
        updated_by: UUID,
    ) -> None:
        """Soft-delete a saved search."""
