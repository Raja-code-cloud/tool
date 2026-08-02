"""Health-aware provider-agnostic client with fallback and circuit hooks."""

from collections.abc import AsyncIterator, Sequence
from typing import Protocol

from cloud_content_hub.infrastructure.ai.exceptions import (
    AICircuitOpenError,
    AIError,
    AIUnavailableError,
)
from cloud_content_hub.infrastructure.ai.interfaces.provider import AIProvider
from cloud_content_hub.infrastructure.ai.models import (
    GenerationRequest,
    GenerationResponse,
    StreamChunk,
    TokenUsage,
)
from cloud_content_hub.infrastructure.ai.providers.base import stream_with_timeout
from cloud_content_hub.infrastructure.ai.retry import RetryPolicy, retry_async
from cloud_content_hub.infrastructure.ai.safety import PassthroughSafetyHook, SafetyHook
from cloud_content_hub.infrastructure.ai.telemetry import log_completion, log_stream_event
from cloud_content_hub.infrastructure.ai.usage import UsageLedger


class CircuitBreaker(Protocol):
    async def allow(self, provider: str) -> bool: ...
    async def success(self, provider: str) -> None: ...
    async def failure(self, provider: str, error: Exception) -> None: ...


class NoopCircuitBreaker:
    async def allow(self, provider: str) -> bool:
        return True

    async def success(self, provider: str) -> None:
        return None

    async def failure(self, provider: str, error: Exception) -> None:
        return None


class AIClient:
    def __init__(
        self,
        providers: Sequence[AIProvider],
        *,
        retry_policy: RetryPolicy | None = None,
        circuit_breaker: CircuitBreaker | None = None,
        safety: SafetyHook | None = None,
        usage_ledger: UsageLedger | None = None,
        stream_timeout_seconds: float | None = None,
        correlation_id: str | None = None,
    ) -> None:
        if not providers:
            raise ValueError("At least one AI provider is required")
        self.providers = tuple(providers)
        self.retry_policy = retry_policy or RetryPolicy()
        self.circuit = circuit_breaker or NoopCircuitBreaker()
        self.safety = safety or PassthroughSafetyHook()
        self.usage_ledger = usage_ledger
        self.stream_timeout_seconds = stream_timeout_seconds
        self.correlation_id = correlation_id

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        safe_request = await self.safety.before_generate(request)
        last_error: Exception | None = None
        for provider in self.providers:
            if not await self.circuit.allow(provider.name):
                continue
            if not (await provider.health_check()).healthy:
                continue
            retries = 0
            try:
                response = await retry_async(
                    lambda: provider.generate(safe_request), self.retry_policy
                )
                await self.circuit.success(provider.name)
                response = await self.safety.after_generate(response)
                if self.usage_ledger is not None:
                    await self.usage_ledger.record(provider.name, response.usage)
                log_completion(
                    provider=provider.name,
                    model=response.model,
                    latency_ms=response.latency_ms,
                    usage=response.usage,
                    success=True,
                    retries=retries,
                    request_id=response.request_id,
                    correlation_id=self.correlation_id,
                    estimated_cost=str(response.estimated_cost)
                    if response.estimated_cost is not None
                    else None,
                )
                return response
            except AIError as exc:
                last_error = exc
                await self.circuit.failure(provider.name, exc)
                log_completion(
                    provider=provider.name,
                    model=safe_request.model or provider.supported_models()[0],
                    latency_ms=0,
                    usage=TokenUsage(input_tokens=0, output_tokens=0),
                    success=False,
                    correlation_id=self.correlation_id,
                )
        if last_error:
            raise AIUnavailableError("All AI providers failed") from last_error
        raise AICircuitOpenError("No healthy AI provider available")

    async def stream(self, request: GenerationRequest) -> AsyncIterator[StreamChunk]:
        safe_request = await self.safety.before_generate(request)
        for provider in self.providers:
            if not await self.circuit.allow(provider.name):
                continue
            if not (await provider.health_check()).healthy:
                continue
            try:
                stream = provider.stream(safe_request)
                if self.stream_timeout_seconds is not None:
                    stream = stream_with_timeout(stream, self.stream_timeout_seconds)
                model = safe_request.model or provider.supported_models()[0]
                async for chunk in stream:
                    model = chunk.model
                    yield chunk
                await self.circuit.success(provider.name)
                log_stream_event(
                    provider=provider.name,
                    model=model,
                    success=True,
                    correlation_id=self.correlation_id,
                )
                return
            except AIError as exc:
                await self.circuit.failure(provider.name, exc)
                log_stream_event(
                    provider=provider.name,
                    model=safe_request.model or provider.supported_models()[0],
                    success=False,
                    correlation_id=self.correlation_id,
                )
        raise AIUnavailableError("All AI provider streams failed")

    async def close(self) -> None:
        for provider in self.providers:
            await provider.close()
