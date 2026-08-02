"""AI and social provider latency micro-benchmarks."""

from __future__ import annotations

from typing import Any

import pytest

from cloud_content_hub.application.content.interfaces.platforms import ContentPlatform
from cloud_content_hub.infrastructure.ai.config import ProviderConfig, ProviderKind
from cloud_content_hub.infrastructure.ai.models import GenerationRequest, Message, Role
from cloud_content_hub.infrastructure.ai.providers.mock_provider import MockProvider
from cloud_content_hub.infrastructure.ai.testing.fakes import RateLimitedMockProvider

pytestmark = pytest.mark.benchmark


@pytest.fixture
def mock_provider_config() -> ProviderConfig:
    return ProviderConfig(kind=ProviderKind.MOCK, model="mock-model")


@pytest.fixture
def generation_request() -> GenerationRequest:
    return GenerationRequest(
        messages=(Message(role=Role.USER, content="Benchmark prompt for content generation."),),
        model="mock-model",
        max_tokens=256,
        temperature=0.2,
    )


@pytest.mark.asyncio
async def test_benchmark_ai_provider_generate(
    benchmark: Any,
    mock_provider_config: ProviderConfig,
    generation_request: GenerationRequest,
) -> None:
    provider = MockProvider(mock_provider_config, latency_ms=1)

    async def run() -> None:
        response = await provider.generate(generation_request)
        assert response.content

    await benchmark.pedantic(run, rounds=10, iterations=1)


@pytest.mark.asyncio
async def test_benchmark_ai_provider_retry_latency(
    benchmark: Any,
    mock_provider_config: ProviderConfig,
    generation_request: GenerationRequest,
) -> None:
    provider = RateLimitedMockProvider(mock_provider_config, latency_ms=1)

    async def run() -> None:
        try:
            await provider.generate(generation_request)
        except Exception:
            await provider.generate(generation_request)

    await benchmark.pedantic(run, rounds=10, iterations=1)


def test_benchmark_platform_constraint_lookup(benchmark: Any) -> None:
    from cloud_content_hub.application.content.interfaces.platforms import PLATFORM_CONSTRAINTS

    platforms = (
        ContentPlatform.LINKEDIN,
        ContentPlatform.FACEBOOK,
        ContentPlatform.INSTAGRAM,
        ContentPlatform.X,
        ContentPlatform.MEDIUM,
        ContentPlatform.YOUTUBE,
    )

    def run() -> None:
        for platform in platforms:
            constraints = PLATFORM_CONSTRAINTS[platform]
            assert constraints.max_text_length > 0

    benchmark(run)


def test_benchmark_scheduler_route_resolution(benchmark: Any) -> None:
    from cloud_content_hub.workers.routing import resolve_task_route

    scheduler_tasks = (
        "cloud_content_hub.tasks.execute_scheduled_publish",
        "cloud_content_hub.tasks.execute_scheduled_analytics",
        "cloud_content_hub.tasks.execute_scheduled_cleanup",
    )

    def run() -> None:
        for task_name in scheduler_tasks:
            route = resolve_task_route(task_name)
            assert route.queue == "maintenance"

    benchmark(run)
