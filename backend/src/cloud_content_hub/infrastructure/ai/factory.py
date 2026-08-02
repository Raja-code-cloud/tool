"""Single provider construction composition root with lazy adapter imports."""

from cloud_content_hub.infrastructure.ai.client import AIClient
from cloud_content_hub.infrastructure.ai.config import ProviderConfig, ProviderKind
from cloud_content_hub.infrastructure.ai.cost import PricingCatalog
from cloud_content_hub.infrastructure.ai.interfaces.provider import AIProvider
from cloud_content_hub.infrastructure.ai.registry import ProviderRegistry


def default_registry() -> ProviderRegistry:
    from cloud_content_hub.infrastructure.ai.providers.azure_openai_provider import (
        AzureOpenAIProvider,
    )
    from cloud_content_hub.infrastructure.ai.providers.claude_provider import ClaudeProvider
    from cloud_content_hub.infrastructure.ai.providers.future_provider import (
        FutureProviderPlaceholder,
    )
    from cloud_content_hub.infrastructure.ai.providers.gemini_provider import GeminiProvider
    from cloud_content_hub.infrastructure.ai.providers.mock_provider import MockProvider
    from cloud_content_hub.infrastructure.ai.providers.openai_provider import OpenAIProvider

    registry = ProviderRegistry()
    registry.register(ProviderKind.OPENAI, OpenAIProvider)
    registry.register(ProviderKind.AZURE_OPENAI, AzureOpenAIProvider)
    registry.register(ProviderKind.CLAUDE, ClaudeProvider)
    registry.register(ProviderKind.GEMINI, GeminiProvider)
    registry.register(ProviderKind.MOCK, MockProvider)
    registry.register(ProviderKind.FUTURE, FutureProviderPlaceholder)
    return registry


def create_provider(
    config: ProviderConfig,
    registry: ProviderRegistry | None = None,
    *,
    pricing_catalog: PricingCatalog | None = None,
) -> AIProvider:
    builder = (registry or default_registry()).get_builder(config.kind)
    try:
        return builder(config, pricing_catalog=pricing_catalog)
    except TypeError:
        return builder(config)


def create_client_from_config(
    config: ProviderConfig,
    *,
    fallback: ProviderConfig | None = None,
    pricing_catalog: PricingCatalog | None = None,
) -> AIClient:
    providers = [create_provider(config, pricing_catalog=pricing_catalog)]
    if fallback is not None:
        providers.append(create_provider(fallback, pricing_catalog=pricing_catalog))
    return AIClient(providers)
