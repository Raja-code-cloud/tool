"""Provider-independent token pricing."""

from dataclasses import dataclass
from decimal import Decimal

from cloud_content_hub.infrastructure.ai.exceptions import AIConfigurationError
from cloud_content_hub.infrastructure.ai.models import TokenUsage


@dataclass(frozen=True, slots=True)
class ModelPricing:
    input_per_million: Decimal
    output_per_million: Decimal


class PricingCatalog:
    def __init__(self) -> None:
        self._prices: dict[tuple[str, str], ModelPricing] = {}

    def register(self, provider: str, model: str, pricing: ModelPricing) -> None:
        self._prices[(provider, model)] = pricing

    def estimate(self, provider: str, model: str, usage: TokenUsage) -> Decimal:
        try:
            price = self._prices[(provider, model)]
        except KeyError as exc:
            raise AIConfigurationError(f"No pricing configured for {provider}/{model}") from exc
        million = Decimal(1_000_000)
        return (
            Decimal(usage.input_tokens) * price.input_per_million
            + Decimal(usage.output_tokens) * price.output_per_million
        ) / million
