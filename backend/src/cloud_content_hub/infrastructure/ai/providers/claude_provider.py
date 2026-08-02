"""Anthropic Claude adapter using AsyncAnthropic Messages."""

from collections.abc import AsyncIterator
from typing import cast

from anthropic import AsyncAnthropic
from anthropic.types import MessageParam

from cloud_content_hub.infrastructure.ai.config import ProviderConfig
from cloud_content_hub.infrastructure.ai.cost import PricingCatalog
from cloud_content_hub.infrastructure.ai.models import (
    Capability,
    GenerationRequest,
    GenerationResponse,
    HealthStatus,
    Role,
    StreamChunk,
    TokenUsage,
    ValidationResult,
)
from cloud_content_hub.infrastructure.ai.providers.base import (
    ProviderSupport,
    measure_latency_ms,
    resolve_model,
    timed_health_check,
)
from cloud_content_hub.infrastructure.ai.utils import translate_error


class ClaudeProvider:
    def __init__(
        self,
        config: ProviderConfig,
        *,
        pricing_catalog: PricingCatalog | None = None,
    ) -> None:
        self.config = config
        self._support = ProviderSupport(
            config,
            provider_name="claude",
            capabilities=frozenset(
                {Capability.TEXT, Capability.STREAMING, Capability.TOOLS, Capability.VISION}
            ),
            pricing_catalog=pricing_catalog,
        )
        self._client = AsyncAnthropic(
            api_key=config.api_key.get_secret_value() if config.api_key else "",
            timeout=config.timeout_seconds,
            max_retries=0,
        )

    @property
    def name(self) -> str:
        return "claude"

    def _messages(self, request: GenerationRequest) -> tuple[str, list[MessageParam]]:
        system = "\n".join(
            message.content for message in request.messages if message.role is Role.SYSTEM
        )
        messages = cast(
            list[MessageParam],
            [
                {"role": message.role.value, "content": message.content}
                for message in request.messages
                if message.role is not Role.SYSTEM
            ],
        )
        return system, messages

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        model = resolve_model(request, self.config)
        system, messages = self._messages(request)
        try:
            response, latency_ms = await measure_latency_ms(
                lambda: self._client.messages.create(
                    model=model,
                    system=system,
                    messages=messages,
                    max_tokens=request.max_tokens or self.config.default_max_tokens,
                    temperature=request.temperature or self.config.default_temperature,
                )
            )
            content = "".join(block.text for block in response.content if block.type == "text")
            usage = TokenUsage(
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
            )
            result = GenerationResponse(
                content=content,
                model=response.model,
                provider=self.name,
                usage=usage,
                finish_reason=response.stop_reason,
                request_id=response.id,
            )
            return self._support.attach_cost(
                result, model=model, usage=usage, latency_ms=latency_ms
            )
        except Exception as exc:
            raise translate_error(exc) from exc

    async def stream(self, request: GenerationRequest) -> AsyncIterator[StreamChunk]:
        model = resolve_model(request, self.config)
        system, messages = self._messages(request)
        try:
            async with self._client.messages.stream(
                model=model,
                system=system,
                messages=messages,
                max_tokens=request.max_tokens or self.config.default_max_tokens,
                temperature=request.temperature or self.config.default_temperature,
            ) as events:
                async for event in events.text_stream:
                    yield StreamChunk(content=event, model=model, provider=self.name)
        except Exception as exc:
            raise translate_error(exc) from exc

    async def health_check(self) -> HealthStatus:
        return await timed_health_check(
            lambda: self._client.models.list(),
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
        await self._client.close()
