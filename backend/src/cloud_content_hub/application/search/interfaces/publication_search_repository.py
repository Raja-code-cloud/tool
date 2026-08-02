"""Publication search repository port and read models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class PublicationStatus(StrEnum):
    DRAFT = "draft"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PARTIALLY_FAILED = "partially_failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class PublicationSearchRecord:
    """Publication aggregate projection for search results."""

    id: UUID
    workspace_id: UUID
    version: int
    created_at: datetime
    updated_at: datetime
    asset_id: UUID
    content_version_id: UUID
    title: str
    status: PublicationStatus


@dataclass(frozen=True, slots=True)
class PublicationSearchCriteria:
    """Structured publication search criteria."""

    workspace_id: UUID
    query: str | None = None
    statuses: frozenset[PublicationStatus] = frozenset()
    cursor: str | None = None
    limit: int = 25
    sort: str = "relevance"


@dataclass(frozen=True, slots=True)
class PublicationSearchPage:
    """Cursor-paged publication search results."""

    items: tuple[PublicationSearchRecord, ...]
    next_cursor: str | None
    has_more: bool


class IPublicationSearchRepository(Protocol):
    """Repository port for publication full-text search."""

    async def search(self, criteria: PublicationSearchCriteria) -> PublicationSearchPage:
        """Search publications using structured filters and optional full-text query."""
