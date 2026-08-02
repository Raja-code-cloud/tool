"""Extensible, business-neutral safety hooks."""

from typing import Protocol

from cloud_content_hub.infrastructure.ai.models import GenerationRequest, GenerationResponse


class ContentModerationHook(Protocol):
    async def moderate_prompt(self, request: GenerationRequest) -> None: ...

    async def moderate_response(self, response: GenerationResponse) -> None: ...


class PIIDetectionHook(Protocol):
    async def scan_prompt(self, request: GenerationRequest) -> None: ...

    async def scan_response(self, response: GenerationResponse) -> None: ...


class SafetyHook(Protocol):
    async def before_generate(self, request: GenerationRequest) -> GenerationRequest: ...

    async def after_generate(self, response: GenerationResponse) -> GenerationResponse: ...


class PassthroughSafetyHook:
    async def before_generate(self, request: GenerationRequest) -> GenerationRequest:
        return request

    async def after_generate(self, response: GenerationResponse) -> GenerationResponse:
        return response


class CompositeSafetyHook:
    """Combines optional moderation and PII hooks with request/response validation."""

    def __init__(
        self,
        *,
        moderation: ContentModerationHook | None = None,
        pii: PIIDetectionHook | None = None,
    ) -> None:
        self.moderation = moderation
        self.pii = pii

    async def before_generate(self, request: GenerationRequest) -> GenerationRequest:
        if self.pii is not None:
            await self.pii.scan_prompt(request)
        if self.moderation is not None:
            await self.moderation.moderate_prompt(request)
        return request

    async def after_generate(self, response: GenerationResponse) -> GenerationResponse:
        if self.pii is not None:
            await self.pii.scan_response(response)
        if self.moderation is not None:
            await self.moderation.moderate_response(response)
        return response
