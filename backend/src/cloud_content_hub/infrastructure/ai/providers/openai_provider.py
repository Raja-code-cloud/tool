"""OpenAI adapter using the asynchronous Responses API."""

from collections.abc import AsyncIterator
from typing import Any, cast

from openai import AsyncOpenAI
from openai.types.responses import ResponseStreamEvent

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
from cloud_content_hub.infrastructure.ai.providers.base import (
    ProviderSupport,
    measure_latency_ms,
    resolve_model,
    timed_health_check,
)
from cloud_content_hub.infrastructure.ai.utils import translate_error


class OpenAIProvider:
    def __init__(
        self,
        config: ProviderConfig,
        *,
        pricing_catalog: PricingCatalog | None = None,
    ) -> None:
        self.config = config
        self._support = ProviderSupport(
            config,
            provider_name="openai",
            capabilities=frozenset(
                {
                    Capability.TEXT,
                    Capability.STREAMING,
                    Capability.JSON,
                    Capability.TOOLS,
                    Capability.VISION,
                }
            ),
            pricing_catalog=pricing_catalog,
        )
        self._client = AsyncOpenAI(
            api_key=config.api_key.get_secret_value() if config.api_key else None,
            timeout=config.timeout_seconds,
            max_retries=0,
        )

    @property
    def name(self) -> str:
        return "openai"

    def _input(self, request: GenerationRequest) -> list[dict[str, str]]:
        return [
            {"role": message.role.value, "content": message.content} for message in request.messages
        ]

    def _sdk_input(self, request: GenerationRequest) -> Any:
        return cast(Any, self._input(request))

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        model = resolve_model(request, self.config)
        try:
            response, latency_ms = await measure_latency_ms(
                lambda: self._client.responses.create(
                    model=model,
                    input=self._sdk_input(request),
                    temperature=request.temperature or self.config.default_temperature,
                    max_output_tokens=request.max_tokens or self.config.default_max_tokens,
                )
            )
            usage = TokenUsage(
                input_tokens=response.usage.input_tokens if response.usage else 0,
                output_tokens=response.usage.output_tokens if response.usage else 0,
            )
            result = GenerationResponse(
                content=response.output_text,
                model=response.model,
                provider=self.name,
                usage=usage,
                request_id=response.id,
            )
            return self._support.attach_cost(
                result, model=model, usage=usage, latency_ms=latency_ms
            )
        except Exception as exc:
            raise translate_error(exc) from exc

    async def stream(self, request: GenerationRequest) -> AsyncIterator[StreamChunk]:
        model = resolve_model(request, self.config)
        try:
            stream = await self._client.responses.create(
                model=model,
                input=self._sdk_input(request),
                stream=True,
            )
            async for event in cast(AsyncIterator[ResponseStreamEvent], stream):
                if event.type == "response.output_text.delta":
                    yield StreamChunk(content=event.delta, model=model, provider=self.name)
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
