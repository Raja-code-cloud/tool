"""Search command definitions."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from cloud_content_hub.application.search.dto.requests import SaveSearchRequestDto


@dataclass(frozen=True, slots=True)
class SaveSearchCommand:
    """Command to persist a saved search."""

    request: SaveSearchRequestDto


@dataclass(frozen=True, slots=True)
class DeleteSavedSearchCommand:
    """Command to delete a saved search."""

    saved_search_id: UUID
    expected_version: int


@dataclass(frozen=True, slots=True)
class ClearRecentSearchesCommand:
    """Command to clear recent search history for the current user."""
