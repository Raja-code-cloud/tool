"""Shared provider adapter helpers."""

import time
from collections.abc import AsyncIterator, Awaitable, Callable
from decimal import Decimal
from typing import Any, TypeVar

from cloud_content_hub.infrastructure.ai.config import ProviderConfig
from cloud_content_hub.infrastructure.ai.cost import PricingCatalog
from cloud_content_hub.infrastructure.ai.models import (
    Capability,
    GenerationRequest,
    GenerationResponse,
    HealthStatus,
    StreamChunk,
    TokenUsage,
    ValidationResult,
)
from cloud_content_hub.infrastructure.ai.prompts.validators import validate_request
from cloud_content_hub.infrastructure.ai.tokenizer import approximate_token_count

T = TypeVar("T")


async def measure_latency_ms(operation: Callable[[], Awaitable[T]]) -> tuple[T, int]:
    started = time.perf_counter()
    result = await operation()
    latency_ms = int((time.perf_counter() - started) * 1000)
    return result, latency_ms


def resolve_model(request: GenerationRequest, config: ProviderConfig) -> str:
    return request.model or config.model


def estimate_response_cost(
    catalog: PricingCatalog | None,
    provider: str,
    model: str,
    usage: TokenUsage,
) -> Decimal | None:
    if catalog is None:
        return None
    try:
        return catalog.estimate(provider, model, usage)
    except Exception:
        return None


async def timed_health_check(
    check: Callable[[], Awaitable[Any]],
    *,
    available_models: tuple[str, ...] = (),
) -> HealthStatus:
    started = time.perf_counter()
    try:
        await check()
        latency_ms = int((time.perf_counter() - started) * 1000)
        return HealthStatus(
            healthy=True,
            latency_ms=latency_ms,
            detail="ok",
            available_models=available_models,
        )
    except Exception as exc:
        latency_ms = int((time.perf_counter() - started) * 1000)
        return HealthStatus(
            healthy=False,
            latency_ms=latency_ms,
            detail=type(exc).__name__,
            available_models=available_models,
        )


class ProviderSupport:
    """Reusable non-SDK provider behaviors."""

    def __init__(
        self,
        config: ProviderConfig,
        *,
        provider_name: str,
        capabilities: frozenset[Capability],
        pricing_catalog: PricingCatalog | None = None,
    ) -> None:
        self.config = config
        self.provider_name = provider_name
        self.capabilities = capabilities
        self.pricing_catalog = pricing_catalog

    async def count_tokens(self, request: GenerationRequest) -> int:
        return approximate_token_count(request)

    async def estimate_cost(self, request: GenerationRequest) -> float:
        usage = TokenUsage(
            input_tokens=await self.count_tokens(request),
            output_tokens=self.config.default_max_tokens,
        )
        cost = estimate_response_cost(
            self.pricing_catalog,
            self.provider_name,
            resolve_model(request, self.config),
            usage,
        )
        return float(cost) if cost is not None else 0.0

    async def validate_prompt(self, request: GenerationRequest) -> ValidationResult:
        return validate_request(request, self.config)

    def supported_models(self) -> tuple[str, ...]:
        return (self.config.model,)

    def supported_capabilities(self) -> frozenset[Capability]:
        return self.capabilities

    def attach_cost(
        self,
        response: GenerationResponse,
        *,
        model: str,
        usage: TokenUsage,
        latency_ms: int,
    ) -> GenerationResponse:
        estimated_cost = estimate_response_cost(
            self.pricing_catalog,
            self.provider_name,
            model,
            usage,
        )
        return response.model_copy(
            update={
                "estimated_cost": estimated_cost,
                "latency_ms": latency_ms,
            }
        )


async def stream_with_timeout(
    iterator: AsyncIterator[StreamChunk],
    timeout_seconds: float,
) -> AsyncIterator[StreamChunk]:
    import asyncio

    async def _next() -> StreamChunk | None:
        try:
            return await anext(iterator)
        except StopAsyncIteration:
            return None

    while True:
        chunk = await asyncio.wait_for(_next(), timeout=timeout_seconds)
        if chunk is None:
            break
        yield chunk
