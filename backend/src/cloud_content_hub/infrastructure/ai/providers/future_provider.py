"""Placeholder adapter for providers not yet implemented."""

from collections.abc import AsyncIterator

from cloud_content_hub.infrastructure.ai.config import ProviderConfig
from cloud_content_hub.infrastructure.ai.exceptions import AIConfigurationError
from cloud_content_hub.infrastructure.ai.models import (
    Capability,
    GenerationRequest,
    GenerationResponse,
    HealthStatus,
    StreamChunk,
    ValidationResult,
)


class FutureProviderPlaceholder:
    def __init__(self, config: ProviderConfig) -> None:
        self.config = config

    @property
    def name(self) -> str:
        return "future"

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        raise AIConfigurationError("Future provider is not implemented")

    async def stream(self, request: GenerationRequest) -> AsyncIterator[StreamChunk]:
        raise AIConfigurationError("Future provider is not implemented")
        yield StreamChunk(
            content="", model=self.config.model, provider=self.name
        )  # pragma: no cover

    async def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=False, latency_ms=0, detail="not implemented")

    async def count_tokens(self, request: GenerationRequest) -> int:
        raise AIConfigurationError("Future provider is not implemented")

    async def estimate_cost(self, request: GenerationRequest) -> float:
        raise AIConfigurationError("Future provider is not implemented")

    async def validate_prompt(self, request: GenerationRequest) -> ValidationResult:
        return ValidationResult(valid=False, errors=("Future provider is not implemented",))

    def supported_models(self) -> tuple[str, ...]:
        return ()

    def supported_capabilities(self) -> frozenset[Capability]:
        return frozenset()

    async def close(self) -> None:
        return None
