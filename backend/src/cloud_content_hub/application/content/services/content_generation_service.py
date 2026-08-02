"""AI orchestration for content generation."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from cloud_content_hub.application.content.dto.requests import (
    GenerationInputDto,
    GenerationScopeDto,
)
from cloud_content_hub.application.content.dto.responses import (
    AiUsageMetadataDto,
    ContentPreviewResponse,
    PlatformContentDto,
    PromptMetadataDto,
    SeoMetadataDto,
)
from cloud_content_hub.application.content.exceptions.content_errors import (
    GenerationValidationError,
)
from cloud_content_hub.application.content.interfaces.platforms import ContentPlatform
from cloud_content_hub.application.content.services.content_prompt_service import (
    ContentPromptService,
)
from cloud_content_hub.application.content.services.platform_mapping_service import (
    PlatformMappingService,
)
from cloud_content_hub.application.shared.interfaces.ai_generation import (
    AIGenerationPort,
    ApplicationGenerationRequest,
    ApplicationGenerationResponse,
)


@dataclass(frozen=True, slots=True)
class ContentGenerationService:
    """Orchestrates AI generation through the application port."""

    ai_port: AIGenerationPort
    prompt_service: ContentPromptService
    platform_mapping: PlatformMappingService

    async def preview(
        self,
        *,
        request: GenerationInputDto,
        scope: GenerationScopeDto,
        model: str,
        source_title: str | None,
        source_body: str | None,
        parameters: dict[str, Any],
    ) -> ContentPreviewResponse:
        """Generate a non-persisted preview using the AI port."""

        model_valid = await self.ai_port.validate_model(model)
        if not model_valid:
            raise GenerationValidationError(detail="The requested AI model is not enabled.")

        built = self.prompt_service.build_generation_prompt(
            request=request,
            scope=scope,
            source_title=source_title,
            source_body=source_body,
            model=model,
        )
        temperature = _optional_float(parameters.get("temperature"))
        max_tokens = _optional_int(parameters.get("maxTokens") or parameters.get("max_tokens"))
        app_request = self.prompt_service.to_application_request(
            built=built,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        response = await self.ai_port.generate(app_request)
        platforms = _split_platform_outputs(request.target_platforms, response)
        seo = _extract_seo_metadata(response)
        usage = _map_usage(response)
        prompt_metadata = PromptMetadataDto(
            system_prompt_hash=built.system_prompt_hash,
            user_prompt_hash=built.user_prompt_hash,
            variables=dict(built.metadata),
        )
        return ContentPreviewResponse(
            platforms=platforms,
            seo_metadata=seo,
            prompt_metadata=prompt_metadata,
            ai_usage=usage,
        )

    async def estimate_cost(self, request: ApplicationGenerationRequest) -> Decimal:
        """Estimate provider cost for a normalized generation request."""

        return await self.ai_port.estimate_cost(request)


def _split_platform_outputs(
    platforms: tuple[ContentPlatform, ...],
    response: ApplicationGenerationResponse,
) -> tuple[PlatformContentDto, ...]:
    selected = platforms or (ContentPlatform.LINKEDIN,)
    sections = [section.strip() for section in response.content.split("\n---\n") if section.strip()]
    if len(sections) == len(selected):
        return tuple(
            PlatformContentDto(platform=platform, text=text)
            for platform, text in zip(selected, sections, strict=True)
        )
    return tuple(
        PlatformContentDto(platform=platform, text=response.content) for platform in selected
    )


def _extract_seo_metadata(response: ApplicationGenerationResponse) -> SeoMetadataDto | None:
    lines = [line.strip() for line in response.content.splitlines() if line.strip()]
    if not lines:
        return None
    title = lines[0][:100] if lines else None
    description = lines[1][:300] if len(lines) > 1 else None
    return SeoMetadataDto(title=title, description=description)


def _map_usage(response: ApplicationGenerationResponse) -> AiUsageMetadataDto:
    return AiUsageMetadataDto(
        model=response.model,
        provider=response.provider,
        input_tokens=response.input_tokens,
        output_tokens=response.output_tokens,
        estimated_cost=str(response.estimated_cost)
        if response.estimated_cost is not None
        else None,
        latency_ms=response.latency_ms,
        finish_reason=response.finish_reason,
    )


def _optional_float(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _optional_int(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return None
