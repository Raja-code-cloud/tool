"""Content query definitions."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from cloud_content_hub.application.content.dto.requests import GenerationRequestDto
from cloud_content_hub.application.content.interfaces.content_repository import (
    ContentLifecycleStatus,
    ContentOrigin,
)


@dataclass(frozen=True, slots=True)
class GetContentQuery:
    """Query to retrieve one content aggregate."""

    content_id: UUID


@dataclass(frozen=True, slots=True)
class GetContentVersionQuery:
    """Query to retrieve one content version."""

    version_id: UUID


@dataclass(frozen=True, slots=True)
class SearchContentQuery:
    """Query to search content."""

    query: str | None = None
    lifecycle_statuses: frozenset[ContentLifecycleStatus] = frozenset()
    origins: frozenset[ContentOrigin] = frozenset()
    cursor: str | None = None
    limit: int = 25
    sort: str = "-updated_at"


@dataclass(frozen=True, slots=True)
class ListContentQuery:
    """Query to list content with structured filters."""

    lifecycle_statuses: frozenset[ContentLifecycleStatus] = frozenset()
    origins: frozenset[ContentOrigin] = frozenset()
    cursor: str | None = None
    limit: int = 25
    sort: str = "-updated_at"


@dataclass(frozen=True, slots=True)
class CompareVersionsQuery:
    """Query to compare two content versions."""

    source_version_id: UUID
    target_version_id: UUID


@dataclass(frozen=True, slots=True)
class PreviewContentQuery:
    """Query to preview generated content without persisting."""

    request: GenerationRequestDto
