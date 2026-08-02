from decimal import Decimal

import pytest

from cloud_content_hub.infrastructure.ai.client import AIClient
from cloud_content_hub.infrastructure.ai.config import ProviderConfig, ProviderKind, SafetyConfig
from cloud_content_hub.infrastructure.ai.cost import ModelPricing, PricingCatalog
from cloud_content_hub.infrastructure.ai.exceptions import (
    AIConfigurationError,
    AIRateLimitError,
    AIValidationError,
    InvalidPrompt,
    PromptTooLarge,
)
from cloud_content_hub.infrastructure.ai.factory import create_provider, default_registry
from cloud_content_hub.infrastructure.ai.models import GenerationRequest, Message, Role, TokenUsage
from cloud_content_hub.infrastructure.ai.prompts.renderer import render_prompt
from cloud_content_hub.infrastructure.ai.prompts.template import PromptTemplate
from cloud_content_hub.infrastructure.ai.prompts.validators import validate_request
from cloud_content_hub.infrastructure.ai.providers.future_provider import FutureProviderPlaceholder
from cloud_content_hub.infrastructure.ai.providers.mock_provider import MockProvider
from cloud_content_hub.infrastructure.ai.retry import RetryPolicy, retry_async
from cloud_content_hub.infrastructure.ai.telemetry import safe_metadata
from cloud_content_hub.infrastructure.ai.tokenizer import approximate_token_count, build_messages
from cloud_content_hub.infrastructure.ai.usage import UsageLedger


def config() -> ProviderConfig:
    return ProviderConfig(kind=ProviderKind.MOCK, model="mock-1")


def request() -> GenerationRequest:
    return GenerationRequest(messages=(Message(role=Role.USER, content="hello"),))


def test_prompt_rendering_is_strict() -> None:
    assert render_prompt(PromptTemplate(template="Hi {name}"), {"name": "Ada"}) == "Hi Ada"
    with pytest.raises(AIValidationError):
        render_prompt(PromptTemplate(template="{name}"), {})


def test_build_messages() -> None:
    messages = build_messages(system="sys", user="usr")
    assert len(messages) == 2
    assert messages[0].role is Role.SYSTEM


def test_cost_catalog() -> None:
    catalog = PricingCatalog()
    catalog.register("p", "m", ModelPricing(Decimal("1"), Decimal("2")))
    assert catalog.estimate(
        "p", "m", TokenUsage(input_tokens=1_000_000, output_tokens=500_000)
    ) == Decimal("2")


def test_prompt_size_validation() -> None:
    cfg = ProviderConfig(
        kind=ProviderKind.MOCK, model="mock", safety=SafetyConfig(max_prompt_characters=3)
    )
    result = validate_request(request(), cfg)
    assert not result.valid
    with pytest.raises(PromptTooLarge):
        from cloud_content_hub.infrastructure.ai.prompts.validators import ensure_valid_request

        ensure_valid_request(request(), cfg)


def test_empty_prompt_invalid() -> None:
    empty = GenerationRequest(messages=(Message(role=Role.USER, content="   "),))
    with pytest.raises(InvalidPrompt):
        from cloud_content_hub.infrastructure.ai.prompts.validators import ensure_valid_request

        ensure_valid_request(empty)


async def test_mock_generate_and_stream() -> None:
    provider = create_provider(config())
    assert (await provider.generate(request())).content == "mock response"
    chunks = [chunk async for chunk in provider.stream(request())]
    assert "".join(chunk.content for chunk in chunks).strip() == "mock response"


async def test_retry_transient_error() -> None:
    calls = 0

    async def operation() -> str:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise AIRateLimitError()
        return "ok"

    assert await retry_async(operation, RetryPolicy(attempts=1, base_delay=0, jitter=0)) == "ok"


async def test_client_falls_back_from_unhealthy_provider() -> None:
    first = MockProvider(config())
    first.fail = True
    second = MockProvider(config(), "fallback")
    assert (await AIClient([first, second]).generate(request())).content == "fallback"


async def test_usage_ledger_records_tokens() -> None:
    ledger = UsageLedger()
    client = AIClient([MockProvider(config())], usage_ledger=ledger)
    await client.generate(request())
    usage = await ledger.get("mock")
    assert usage.input_tokens > 0


def test_registry_future_placeholder_registered() -> None:
    assert ProviderKind.FUTURE in default_registry().registered_kinds()


async def test_future_provider_fails_fast() -> None:
    provider = FutureProviderPlaceholder(ProviderConfig(kind=ProviderKind.FUTURE, model="future"))
    with pytest.raises(AIConfigurationError):
        await provider.generate(request())


def test_telemetry_redacts_sensitive_fields() -> None:
    assert safe_metadata({"prompt": "secret", "provider": "mock", "api_key": "key"}) == {
        "provider": "mock"
    }


def test_token_estimation() -> None:
    assert approximate_token_count(request()) >= 1
