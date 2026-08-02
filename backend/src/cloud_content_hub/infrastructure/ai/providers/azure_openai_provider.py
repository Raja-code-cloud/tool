"""Azure OpenAI adapter using AzureOpenAI Responses API."""

from openai import AsyncAzureOpenAI

from cloud_content_hub.infrastructure.ai.config import ProviderConfig
from cloud_content_hub.infrastructure.ai.cost import PricingCatalog
from cloud_content_hub.infrastructure.ai.models import Capability
from cloud_content_hub.infrastructure.ai.providers.base import ProviderSupport
from cloud_content_hub.infrastructure.ai.providers.openai_provider import OpenAIProvider


class AzureOpenAIProvider(OpenAIProvider):
    def __init__(
        self,
        config: ProviderConfig,
        *,
        pricing_catalog: PricingCatalog | None = None,
    ) -> None:
        endpoint = config.endpoint
        if endpoint is None:
            msg = "Azure endpoint is required"
            raise ValueError(msg)
        self.config = config
        self._support = ProviderSupport(
            config,
            provider_name="azure_openai",
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
        self._client = AsyncAzureOpenAI(
            api_key=config.api_key.get_secret_value() if config.api_key else None,
            azure_endpoint=endpoint,
            azure_deployment=config.azure_deployment,
            api_version=config.api_version,
            timeout=config.timeout_seconds,
            max_retries=0,
        )

    @property
    def name(self) -> str:
        return "azure_openai"
