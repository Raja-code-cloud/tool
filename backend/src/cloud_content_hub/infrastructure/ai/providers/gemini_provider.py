"""Google Gemini adapter using the current google-genai client."""

from collections.abc import AsyncIterator

from google import genai
from google.genai import types

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


class GeminiProvider:
    def __init__(
        self, config: ProviderConfig, *, pricing_catalog: PricingCatalog | None = None
    ) -> None:
        self.config = config
        self._support = ProviderSupport(
            config,
            provider_name="gemini",
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
        self._client = genai.Client(
            api_key=config.api_key.get_secret_value() if config.api_key else None
        )

    @property
    def name(self) -> str:
        return "gemini"

    def _contents(self, request: GenerationRequest) -> str:
        return "\n".join(message.content for message in request.messages)

    async def generate(self, request: GenerationRequest) -> GenerationResponse:
        model = resolve_model(request, self.config)
        try:
            response, latency_ms = await measure_latency_ms(
                lambda: self._client.aio.models.generate_content(
                    model=model,
                    contents=self._contents(request),
                    config=types.GenerateContentConfig(
                        temperature=request.temperature or self.config.default_temperature,
                        max_output_tokens=request.max_tokens or self.config.default_max_tokens,
                    ),
                )
            )
            metadata = response.usage_metadata
            usage = TokenUsage(
                input_tokens=metadata.prompt_token_count or 0 if metadata else 0,
                output_tokens=metadata.candidates_token_count or 0 if metadata else 0,
            )
            result = GenerationResponse(
                content=response.text or "", model=model, provider=self.name, usage=usage
            )
            return self._support.attach_cost(
                result, model=model, usage=usage, latency_ms=latency_ms
            )
        except Exception as exc:
            raise translate_error(exc) from exc

    async def stream(self, request: GenerationRequest) -> AsyncIterator[StreamChunk]:
        model = resolve_model(request, self.config)
        try:
            stream = await self._client.aio.models.generate_content_stream(
                model=model, contents=self._contents(request)
            )
            async for chunk in stream:
                yield StreamChunk(content=chunk.text or "", model=model, provider=self.name)
        except Exception as exc:
            raise translate_error(exc) from exc

    async def health_check(self) -> HealthStatus:
        model = self.config.model
        return await timed_health_check(
            lambda: self._client.aio.models.get(model=model),
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
        await self._client.aio.aclose()
