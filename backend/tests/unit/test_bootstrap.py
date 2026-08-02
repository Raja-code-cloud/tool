"""Bootstrap composition root tests."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID

import pytest

from cloud_content_hub.application.scheduler.interfaces.schedule_repository import AmbiguityPolicy
from cloud_content_hub.application.scheduler.interfaces.schedule_time_resolver import (
    LocalScheduleInput,
)
from cloud_content_hub.bootstrap.configuration import load_bootstrap_configuration
from cloud_content_hub.bootstrap.container import Container
from cloud_content_hub.bootstrap.handlers import wire_handlers
from cloud_content_hub.bootstrap.providers import (
    FixedClock,
    FixedUuidGenerator,
    SystemClock,
    ZoneInfoScheduleTimeResolver,
)
from cloud_content_hub.bootstrap.repositories import create_repository_factories
from cloud_content_hub.bootstrap.shutdown import shutdown_application
from cloud_content_hub.core.config import Environment, Settings


class TestConfiguration:
    def test_loads_test_configuration(self) -> None:
        settings = Settings(environment=Environment.TEST)
        config = load_bootstrap_configuration(settings)
        assert config.settings.environment is Environment.TEST
        assert config.identity.environment == "test"
        assert config.ai.primary_kind is not None


class TestProviders:
    def test_schedule_time_resolver_converts_utc(self) -> None:
        resolver = ZoneInfoScheduleTimeResolver()
        resolved = resolver.resolve(
            LocalScheduleInput(
                requested_local_at=datetime(2026, 6, 1, 12, 0, tzinfo=UTC),
                time_zone="UTC",
                fold=None,
                ambiguity_policy=AmbiguityPolicy.REJECT,
            )
        )
        assert resolved.scheduled_for.tzinfo is UTC


class TestContainer:
    @pytest.mark.asyncio
    async def test_create_startup_and_shutdown(self, monkeypatch: pytest.MonkeyPatch) -> None:
        settings = Settings(environment=Environment.TEST)
        fixed_time = datetime(2026, 1, 1, tzinfo=UTC)
        container = Container.create(
            settings,
            clock=FixedClock(fixed_time),
            uuid_generator=FixedUuidGenerator(UUID("00000000-0000-0000-0000-000000000001")),
        )

        async def noop_startup(_container: Container) -> None:
            return None

        monkeypatch.setattr(
            "cloud_content_hub.bootstrap.startup.startup_application",
            noop_startup,
        )

        await container.startup()

        try:
            registry = wire_handlers(container)
        except ImportError:
            pytest.skip("Notification handler imports are unavailable in this environment.")

        assert container.started_at == fixed_time
        assert len(registry.handlers) >= 20
        assert registry.resolve("list_assets") is not None
        assert len(container.health_checker._checks) == 5

        container.storage_provider.close = AsyncMock()  # type: ignore[method-assign]
        container.redis.aclose = AsyncMock()  # type: ignore[method-assign]
        container.database_engine.dispose = AsyncMock()  # type: ignore[method-assign]
        await shutdown_application(container)


class TestRepositoryFactories:
    def test_unit_of_work_factory_creates_sqlalchemy_uow(self) -> None:
        session_factory = MagicMock()
        factories = create_repository_factories(session_factory)
        uow = factories.unit_of_work_factory()
        assert uow is not None


class TestDependencyGraph:
    def test_handler_registry_keys_are_unique(self) -> None:
        container = Container.create(Settings(environment=Environment.TEST))
        try:
            registry = wire_handlers(container)
        except ImportError:
            pytest.skip("Application handler imports are unavailable in this environment.")
        keys = list(registry.handlers.keys())
        assert len(keys) == len(set(keys))

    def test_clock_and_uuid_are_injected(self) -> None:
        fixed_uuid = UUID("11111111-1111-1111-1111-111111111111")
        container = Container.create(
            Settings(environment=Environment.TEST),
            clock=SystemClock(),
            uuid_generator=FixedUuidGenerator(fixed_uuid),
        )
        assert container.uuid_generator.uuid4() == fixed_uuid
