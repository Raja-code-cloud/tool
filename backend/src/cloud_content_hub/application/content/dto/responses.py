"""Content response DTOs."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field

from cloud_content_hub.application.content.interfaces.platforms import ContentPlatform
from cloud_content_hub.application.shared.dto.base import ApplicationDto, ResourceBaseDto


class ContentLifecycleStatusDto(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ContentOriginDto(StrEnum):
    USER = "user"
    AI = "ai"
    IMPORT = "import"
    REGENERATION = "regeneration"


class GenerationOutputStatusDto(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ContentDto(ResourceBaseDto):
    """Content projection returned by query handlers."""

    asset_id: UUID
    title: str
    body_text: str | None
    body_rich: dict[str, Any] | None = None
    metadata: dict[str, Any]
    lifecycle_status: ContentLifecycleStatusDto
    origin: ContentOriginDto
    content_version_id: UUID | None


class ContentVersionResponse(ResourceBaseDto):
    """Immutable content version projection."""

    asset_id: UUID
    version_number: int = Field(ge=1)
    title: str
    body_text: str | None
    body_rich: dict[str, Any] | None = None
    metadata: dict[str, Any]
    origin: ContentOriginDto
    source_version_id: UUID | None
    change_summary: str | None
    created_by: UUID


class SeoMetadataDto(ApplicationDto):
    """SEO metadata extracted from generated content."""

    title: str | None = None
    description: str | None = None
    keywords: tuple[str, ...] = Field(default_factory=tuple)
    canonical_url: str | None = None


class PromptMetadataDto(ApplicationDto):
    """Prompt metadata attached to generation outputs."""

    template_id: UUID | None = None
    template_version: str | None = None
    system_prompt_hash: str | None = None
    user_prompt_hash: str | None = None
    variables: dict[str, str] = Field(default_factory=dict)


class AiUsageMetadataDto(ApplicationDto):
    """Token and cost metadata from AI generation."""

    model: str
    provider: str
    input_tokens: int = Field(ge=0)
    output_tokens: int = Field(ge=0)
    estimated_cost: str | None = None
    latency_ms: int = Field(ge=0, default=0)
    finish_reason: str | None = None


class PlatformContentDto(ApplicationDto):
    """Platform-specific generated text projection."""

    platform: ContentPlatform
    text: str
    suggested_title: str | None = None
    suggested_hashtags: tuple[str, ...] = Field(default_factory=tuple)
    summary: str | None = None
    estimated_reading_time_minutes: int | None = Field(default=None, ge=1)


class GenerateContentResponse(ApplicationDto):
    """Response returned when generation is accepted."""

    operation_id: UUID
    status: str
    resource_type: str | None = None
    resource_id: UUID | None = None
    created_at: datetime


class ContentPreviewResponse(ApplicationDto):
    """Non-persisted preview of generated platform content."""

    platforms: tuple[PlatformContentDto, ...]
    seo_metadata: SeoMetadataDto | None = None
    prompt_metadata: PromptMetadataDto | None = None
    ai_usage: AiUsageMetadataDto | None = None


class VersionComparisonResponse(ApplicationDto):
    """Comparison between two content versions."""

    source_version_id: UUID
    target_version_id: UUID
    title_changed: bool
    body_changed: bool
    metadata_changed: bool
    source_title: str
    target_title: str
    source_body_text: str | None
    target_body_text: str | None


class GenerationOutputDto(ResourceBaseDto):
    """Generation output candidate projection."""

    generation_request_id: UUID
    sequence_no: int = Field(ge=1)
    platform_id: UUID | None
    output_text: str
    output_metadata: dict[str, Any]
    safety_status: str
    materialized_version_id: UUID | None
    status: GenerationOutputStatusDto


SearchContentResponse = tuple[ContentDto, ...]
