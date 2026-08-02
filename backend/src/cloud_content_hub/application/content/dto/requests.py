"""Content request DTOs."""

from __future__ import annotations

from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import Field

from cloud_content_hub.application.content.interfaces.platforms import ContentPlatform
from cloud_content_hub.application.shared.dto.base import ApplicationDto


class GenerationScopeDto(StrEnum):
    WHOLE = "whole"
    SELECTION = "selection"
    HEADLINE = "headline"
    CTA = "cta"
    HASHTAGS = "hashtags"
    TONE = "tone"
    PLATFORM_VARIANT = "platform_variant"


class ContentLengthDto(StrEnum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class GenerationInputDto(ApplicationDto):
    """Shared generation input fields for platform-specific content creation."""

    poster_asset_id: UUID | None = None
    article_asset_id: UUID | None = None
    video_asset_id: UUID | None = None
    thumbnail_asset_id: UUID | None = None
    user_prompt: str | None = None
    target_platforms: tuple[ContentPlatform, ...] = Field(default_factory=tuple)
    tone: str | None = None
    audience: str | None = None
    length: ContentLengthDto | None = None
    language: str = "en"
    hashtags: tuple[str, ...] = Field(default_factory=tuple)
    call_to_action: str | None = None
    selection_text: str | None = None


class GenerationRequestDto(GenerationInputDto):
    """Request payload for content generation."""

    asset_id: UUID | None = None
    source_version_id: UUID
    model_id: UUID
    prompt_template_id: UUID | None = None
    brand_profile_id: UUID | None = None
    scope: GenerationScopeDto
    parameters: dict[str, Any] = Field(default_factory=dict)


class RegenerationRequestDto(GenerationRequestDto):
    """Request payload for content regeneration."""

    content_id: UUID
    asset_id: UUID | None = None


GenerateContentRequest = GenerationRequestDto


class DuplicateContentRequestDto(ApplicationDto):
    """Request payload for duplicating content."""

    title: str | None = Field(default=None, min_length=1, max_length=300)
    project_id: UUID | None = None
    folder_id: UUID | None = None


class CreateContentVersionRequestDto(ApplicationDto):
    """Request payload for creating a user-origin content version."""

    title: str = Field(min_length=1, max_length=300)
    body_text: str | None = None
    body_rich: dict[str, Any] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    source_version_id: UUID | None = None
    change_summary: str | None = Field(default=None, max_length=500)


class ApproveContentRequestDto(ApplicationDto):
    """Request payload for approving a generation output."""

    output_id: UUID
    change_summary: str | None = Field(default=None, max_length=500)


class RejectContentRequestDto(ApplicationDto):
    """Request payload for rejecting a generation output."""

    output_id: UUID
    reason: str | None = Field(default=None, max_length=500)
