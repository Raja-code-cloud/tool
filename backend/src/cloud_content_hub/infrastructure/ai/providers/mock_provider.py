"""Deterministic no-network provider for tests and development."""

from collections.abc import AsyncIterator

from cloud_content_hub.infrastructure.ai.config import ProviderConfig
from cloud_content_hub.infrastructure.ai.exceptions import AIUnavailableError
from cloud_content_hub.infrastructure.ai.models import (
    Capability,
    GenerationRequest,
    GenerationResponse,
    HealthStatus,
    StreamChunk,
    TokenUsage,
    ValidationResult,
)
from cloud_content_hub.infrastructure.ai.providers.base import ProviderSupport, resolve_model


class MockProvider:
    def __init__(
        self, config: ProviderConfig, response: str = "mock response", *, latency_ms: int = 1
    ) -> None:
        self.config, self.response, self.latency_ms = config, response, latency_ms
        self.fail = False
        self._support = ProviderSupport(
            config,
            provider_name="mock",
            capabilities=frozenset({Capability.TEXT, Capability.STREAMING}),
        )

    @property
    def name(self) -> str:
        return "mock"

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        if self.fail:
            raise AIUnavailableError("mock provider unavailable")
        model = resolve_model(request, self.config)
        usage = TokenUsage(
            input_tokens=await self.count_tokens(request),
            output_tokens=max(1, len(self.response) // 4),
        )
        result = GenerationResponse(
            content=self.response,
            model=model,
            provider=self.name,
            usage=usage,
            finish_reason="stop",
        )
        return self._support.attach_cost(
            result, model=model, usage=usage, latency_ms=self.latency_ms
        )

    async def stream(self, request: GenerationRequest) -> AsyncIterator[StreamChunk]:
        response = await self.generate(request)
        for word in response.content.split():
            yield StreamChunk(content=word + " ", model=response.model, provider=self.name)
        yield StreamChunk(
            model=response.model,
            provider=self.name,
            finish_reason="stop",
            usage=response.usage,
            estimated_cost=response.estimated_cost,
        )

    async def health_check(self) -> HealthStatus:
        return HealthStatus(
            healthy=not self.fail,
            latency_ms=self.latency_ms,
            detail="mock",
            available_models=self.supported_models(),
        )

    async def count_tokens(self, request: GenerationRequest) -> int:
        return await self._support.count_tokens(request)

    async def estimate_cost(self, request: GenerationRequest) -> float:
        return await self._support.estimate_cost(request)

    async def validate_prompt(self, request: GenerationRequest) -> ValidationResult:
        return await self._support.validate_prompt(request)

    def supported_models(self) -> tuple[str, ...]:
        return self._support.supported_models()

    def supported_capabilities(self) -> frozenset[Capability]:
        return self._support.supported_capabilities()

    async def close(self) -> None:
        return None
