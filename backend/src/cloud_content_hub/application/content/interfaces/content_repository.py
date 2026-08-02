"""Content repository port and read models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Protocol
from uuid import UUID


class ContentLifecycleStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ContentOrigin(StrEnum):
    USER = "user"
    AI = "ai"
    IMPORT = "import"
    REGENERATION = "regeneration"


class GenerationScope(StrEnum):
    WHOLE = "whole"
    SELECTION = "selection"
    HEADLINE = "headline"
    CTA = "cta"
    HASHTAGS = "hashtags"
    TONE = "tone"
    PLATFORM_VARIANT = "platform_variant"


class GenerationOutputStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class ContentRecord:
    """Content aggregate read model."""

    id: UUID
    workspace_id: UUID
    version: int
    created_at: datetime
    updated_at: datetime
    asset_id: UUID
    title: str
    body_text: str | None
    body_rich: dict[str, Any] | None
    metadata: dict[str, Any]
    lifecycle_status: ContentLifecycleStatus
    origin: ContentOrigin
    content_version_id: UUID | None
    is_deleted: bool = False


@dataclass(frozen=True, slots=True)
class ContentVersionRecord:
    """Immutable content version read model."""

    id: UUID
    workspace_id: UUID
    asset_id: UUID
    version_number: int
    is_immutable: bool
    origin: ContentOrigin


@dataclass(frozen=True, slots=True)
class ContentVersionDetailRecord:
    """Extended immutable content version read model."""

    id: UUID
    workspace_id: UUID
    asset_id: UUID
    version_number: int
    title: str
    body_text: str | None
    body_rich: dict[str, Any] | None
    metadata: dict[str, Any]
    origin: ContentOrigin
    source_version_id: UUID | None
    change_summary: str | None
    created_at: datetime
    created_by: UUID


@dataclass(frozen=True, slots=True)
class GenerationOutputRecord:
    """AI generation output candidate read model."""

    id: UUID
    workspace_id: UUID
    generation_request_id: UUID
    sequence_no: int
    platform_id: UUID | None
    output_text: str
    output_metadata: dict[str, Any]
    safety_status: str
    materialized_version_id: UUID | None
    status: GenerationOutputStatus
    created_at: datetime


@dataclass(frozen=True, slots=True)
class VersionComparisonRecord:
    """Diff summary between two content versions."""

    source_version_id: UUID
    target_version_id: UUID
    title_changed: bool
    body_changed: bool
    metadata_changed: bool
    source_title: str
    target_title: str
    source_body_text: str | None
    target_body_text: str | None


@dataclass(frozen=True, slots=True)
class NewGenerationRequest:
    """Input for recording an AI generation request."""

    workspace_id: UUID
    asset_id: UUID
    source_version_id: UUID
    model_id: UUID
    prompt_template_id: UUID | None
    brand_profile_id: UUID | None
    scope: GenerationScope
    parameters: dict[str, Any]
    selection_text: str | None
    created_by: UUID
    idempotency_key: str | None = None


@dataclass(frozen=True, slots=True)
class NewContentVersion:
    """Input for creating a user-origin content version."""

    workspace_id: UUID
    asset_id: UUID
    source_version_id: UUID | None
    title: str
    body_text: str | None
    body_rich: dict[str, Any] | None
    metadata: dict[str, Any]
    origin: ContentOrigin
    change_summary: str | None
    created_by: UUID


@dataclass(frozen=True, slots=True)
class DuplicateContentInput:
    """Input for duplicating content from an existing aggregate."""

    workspace_id: UUID
    source_content_id: UUID
    title: str | None
    project_id: UUID | None
    folder_id: UUID | None
    created_by: UUID


@dataclass(frozen=True, slots=True)
class ContentSearchCriteria:
    """Structured content search criteria."""

    workspace_id: UUID
    query: str | None = None
    lifecycle_statuses: frozenset[ContentLifecycleStatus] = frozenset()
    origins: frozenset[ContentOrigin] = frozenset()
    cursor: str | None = None
    limit: int = 25
    sort: str = "-updated_at"


@dataclass(frozen=True, slots=True)
class ContentSearchPage:
    """Cursor-paged content search results."""

    items: tuple[ContentRecord, ...]
    next_cursor: str | None
    has_more: bool


class IContentRepository(Protocol):
    """Repository port for content aggregates."""

    async def get_by_id(self, *, workspace_id: UUID, content_id: UUID) -> ContentRecord | None:
        """Return one active content aggregate."""

    async def get_deleted_by_id(
        self, *, workspace_id: UUID, content_id: UUID
    ) -> ContentRecord | None:
        """Return one soft-deleted content aggregate."""

    async def get_version_by_id(
        self,
        *,
        workspace_id: UUID,
        version_id: UUID,
    ) -> ContentVersionRecord | None:
        """Return one content version."""

    async def get_version_detail_by_id(
        self,
        *,
        workspace_id: UUID,
        version_id: UUID,
    ) -> ContentVersionDetailRecord | None:
        """Return one content version with full snapshot fields."""

    async def list_versions(
        self,
        *,
        workspace_id: UUID,
        content_id: UUID,
    ) -> tuple[ContentVersionDetailRecord, ...]:
        """Return all versions for a content aggregate ordered by version number."""

    async def compare_versions(
        self,
        *,
        workspace_id: UUID,
        source_version_id: UUID,
        target_version_id: UUID,
    ) -> VersionComparisonRecord | None:
        """Return a comparison summary between two versions."""

    async def search(self, criteria: ContentSearchCriteria) -> ContentSearchPage:
        """Search content with optional full-text query."""

    async def list_content(
        self,
        *,
        workspace_id: UUID,
        lifecycle_statuses: frozenset[ContentLifecycleStatus],
        origins: frozenset[ContentOrigin],
        cursor: str | None,
        limit: int,
        sort: str,
    ) -> ContentSearchPage:
        """List content with structured filters."""

    async def soft_delete(
        self,
        *,
        workspace_id: UUID,
        content_id: UUID,
        expected_version: int,
        updated_by: UUID,
    ) -> None:
        """Soft-delete a content aggregate."""

    async def restore(
        self,
        *,
        workspace_id: UUID,
        content_id: UUID,
        expected_version: int,
        updated_by: UUID,
    ) -> ContentRecord:
        """Restore a soft-deleted content aggregate."""

    async def update_lifecycle_status(
        self,
        *,
        workspace_id: UUID,
        content_id: UUID,
        lifecycle_status: ContentLifecycleStatus,
        expected_version: int,
        updated_by: UUID,
    ) -> ContentRecord:
        """Transition a content aggregate lifecycle status."""

    async def duplicate(self, request: DuplicateContentInput) -> ContentRecord:
        """Create a new draft content aggregate derived from an existing one."""

    async def create_version(self, request: NewContentVersion) -> ContentVersionDetailRecord:
        """Persist a new immutable content version."""

    async def set_current_version(
        self,
        *,
        workspace_id: UUID,
        content_id: UUID,
        version_id: UUID,
        expected_version: int,
        updated_by: UUID,
    ) -> ContentRecord:
        """Point the content aggregate at an immutable version."""


class IGenerationRequestRepository(Protocol):
    """Repository port for AI generation requests."""

    async def create(self, request: NewGenerationRequest) -> UUID:
        """Persist a generation request and return its identifier."""

    async def validate_model_enabled(self, *, workspace_id: UUID, model_id: UUID) -> bool:
        """Return whether the model is enabled for the workspace."""


class IGenerationOutputRepository(Protocol):
    """Repository port for AI generation output candidates."""

    async def get_by_id(
        self,
        *,
        workspace_id: UUID,
        output_id: UUID,
    ) -> GenerationOutputRecord | None:
        """Return one generation output candidate."""

    async def approve(
        self,
        *,
        workspace_id: UUID,
        output_id: UUID,
        updated_by: UUID,
    ) -> GenerationOutputRecord:
        """Mark a generation output as approved."""

    async def reject(
        self,
        *,
        workspace_id: UUID,
        output_id: UUID,
        updated_by: UUID,
        reason: str | None,
    ) -> GenerationOutputRecord:
        """Mark a generation output as rejected."""
