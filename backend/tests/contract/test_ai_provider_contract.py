import pytest

from cloud_content_hub.infrastructure.ai.config import ProviderConfig, ProviderKind
from cloud_content_hub.infrastructure.ai.interfaces.provider import AIProvider
from cloud_content_hub.infrastructure.ai.models import Capability, GenerationRequest, Message, Role
from cloud_content_hub.infrastructure.ai.providers.mock_provider import MockProvider

pytestmark = pytest.mark.contract


async def test_mock_satisfies_provider_contract() -> None:
    provider: AIProvider = MockProvider(ProviderConfig(kind=ProviderKind.MOCK, model="mock"))
    request = GenerationRequest(messages=(Message(role=Role.USER, content="test"),))
    assert (await provider.validate_prompt(request)).valid
    assert await provider.count_tokens(request) > 0
    assert Capability.TEXT in provider.supported_capabilities()
    health = await provider.health_check()
    assert health.healthy
    assert health.available_models
    response = await provider.generate(request)
    assert response.provider == "mock"
    assert response.latency_ms >= 0
    await provider.close()
