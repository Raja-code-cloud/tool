"""Search suggestion repository port and read models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class SuggestionKind(StrEnum):
    QUERY = "query"
    ENTITY = "entity"


class SearchEntityType(StrEnum):
    ASSET = "asset"
    CONTENT = "content"
    PUBLICATION = "publication"


@dataclass(frozen=True, slots=True)
class SearchSuggestionRecord:
    """Autocomplete suggestion read model."""

    text: str
    kind: SuggestionKind
    entity_type: SearchEntityType | None = None
    entity_id: UUID | None = None
    score: float | None = None


@dataclass(frozen=True, slots=True)
class SearchSuggestionCriteria:
    """Structured suggestion lookup criteria."""

    workspace_id: UUID
    user_id: UUID
    prefix: str
    entity_types: frozenset[SearchEntityType] = frozenset()
    limit: int = 10


class ISearchSuggestionRepository(Protocol):
    """Repository port for search autocomplete suggestions."""

    async def suggest(
        self, criteria: SearchSuggestionCriteria
    ) -> tuple[SearchSuggestionRecord, ...]:
        """Return ranked suggestions for the given prefix."""
