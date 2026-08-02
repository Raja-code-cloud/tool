"""Prompt construction for content generation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from cloud_content_hub.application.content.dto.requests import (
    GenerationInputDto,
    GenerationScopeDto,
)
from cloud_content_hub.application.content.interfaces.platforms import ContentPlatform
from cloud_content_hub.application.content.services.platform_mapping_service import (
    PlatformMappingService,
)
from cloud_content_hub.application.shared.interfaces.ai_generation import (
    ApplicationGenerationRequest,
)


@dataclass(frozen=True, slots=True)
class BuiltPrompt:
    """Prompt bundle ready for the AI generation port."""

    system_prompt: str
    user_prompt: str
    metadata: dict[str, str]
    system_prompt_hash: str
    user_prompt_hash: str


@dataclass(frozen=True, slots=True)
class ContentPromptService:
    """Builds normalized prompts from generation inputs and platform constraints."""

    platform_mapping: PlatformMappingService

    def build_generation_prompt(
        self,
        *,
        request: GenerationInputDto,
        scope: GenerationScopeDto,
        source_title: str | None,
        source_body: str | None,
        model: str,
    ) -> BuiltPrompt:
        """Construct system and user prompts for a generation request."""

        platforms = request.target_platforms or (ContentPlatform.LINKEDIN,)
        platform_codes = self.platform_mapping.platform_codes(platforms)
        max_length = self.platform_mapping.max_generation_length(platforms)

        system_prompt = (
            "You are a professional content strategist. "
            "Generate platform-specific marketing content that respects "
            "each platform's constraints. "
            f"Target platforms: {', '.join(platform_codes)}. "
            f"Maximum text length: {max_length} characters. "
            f"Language: {request.language}. "
            f"Scope: {scope.value}."
        )
        if request.tone:
            system_prompt += f" Tone: {request.tone}."
        if request.audience:
            system_prompt += f" Audience: {request.audience}."
        if request.length:
            system_prompt += f" Length preference: {request.length.value}."

        user_sections: list[str] = []
        if source_title:
            user_sections.append(f"Source title:\n{source_title}")
        if source_body:
            user_sections.append(f"Source body:\n{source_body}")
        if request.user_prompt:
            user_sections.append(f"User instructions:\n{request.user_prompt}")
        if request.selection_text:
            user_sections.append(f"Selected text:\n{request.selection_text}")
        if request.call_to_action:
            user_sections.append(f"Call to action:\n{request.call_to_action}")
        if request.hashtags:
            user_sections.append(f"Requested hashtags: {', '.join(request.hashtags)}")

        asset_refs = _format_asset_refs(request)
        if asset_refs:
            user_sections.append(f"Referenced assets:\n{asset_refs}")

        user_prompt = "\n\n".join(user_sections) or "Generate content from the provided context."
        metadata = {
            "model": model,
            "scope": scope.value,
            "platforms": ",".join(platform_codes),
            "language": request.language,
        }
        return BuiltPrompt(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            metadata=metadata,
            system_prompt_hash=_hash_text(system_prompt),
            user_prompt_hash=_hash_text(user_prompt),
        )

    def to_application_request(
        self,
        *,
        built: BuiltPrompt,
        model: str,
        temperature: float | None,
        max_tokens: int | None,
        extra_metadata: dict[str, Any] | None = None,
    ) -> ApplicationGenerationRequest:
        """Map a built prompt to the shared AI generation port request."""

        metadata = dict(built.metadata)
        if extra_metadata:
            metadata.update({key: str(value) for key, value in extra_metadata.items()})
        return ApplicationGenerationRequest(
            model=model,
            system_prompt=built.system_prompt,
            user_prompt=built.user_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            metadata=metadata,
        )


def _format_asset_refs(request: GenerationInputDto) -> str:
    refs: list[str] = []
    if request.poster_asset_id:
        refs.append(f"poster={request.poster_asset_id}")
    if request.article_asset_id:
        refs.append(f"article={request.article_asset_id}")
    if request.video_asset_id:
        refs.append(f"video={request.video_asset_id}")
    if request.thumbnail_asset_id:
        refs.append(f"thumbnail={request.thumbnail_asset_id}")
    return ", ".join(refs)


def _hash_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def serialize_parameters(parameters: dict[str, Any]) -> str:
    """Serialize generation parameters for prompt metadata."""

    return json.dumps(parameters, sort_keys=True, separators=(",", ":"))
