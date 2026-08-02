"""SDK-free asynchronous AI provider contract."""

from collections.abc import AsyncIterator
from typing import Protocol

from cloud_content_hub.infrastructure.ai.models import (
    Capability,
    GenerationRequest,
    GenerationResponse,
    HealthStatus,
    StreamChunk,
    ValidationResult,
)


class AIProvider(Protocol):
    @property
    def name(self) -> str: ...

    async def generate(self, request: GenerationRequest) -> GenerationResponse: ...

    def stream(self, request: GenerationRequest) -> AsyncIterator[StreamChunk]: ...

    async def health_check(self) -> HealthStatus: ...

    async def count_tokens(self, request: GenerationRequest) -> int: ...

    async def estimate_cost(self, request: GenerationRequest) -> float: ...

    async def validate_prompt(self, request: GenerationRequest) -> ValidationResult: ...

    def supported_models(self) -> tuple[str, ...]: ...

    def supported_capabilities(self) -> frozenset[Capability]: ...

    async def close(self) -> None: ...
