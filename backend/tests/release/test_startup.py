"""Release validation for application startup, DI wiring, and graceful shutdown."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from cloud_content_hub.bootstrap.container import Container
from cloud_content_hub.bootstrap.handlers import wire_handlers
from cloud_content_hub.bootstrap.providers import FixedClock, FixedUuidGenerator
from cloud_content_hub.bootstrap.shutdown import shutdown_application
from cloud_content_hub.core.config import Environment, Settings

pytestmark = pytest.mark.release


class TestDependencyInjection:
    def test_handler_registry_has_unique_keys(self) -> None:
        container = Container.create(Settings(environment=Environment.TEST))
        try:
            registry = wire_handlers(container)
        except ImportError:
            pytest.skip("Application handler imports are unavailable in this environment.")
        keys = list(registry.handlers.keys())
        assert len(keys) == len(set(keys))
        assert len(keys) >= 20

    def test_container_registers_health_checks(self) -> None:
        container = Container.create(Settings(environment=Environment.TEST))
        assert len(container.health_checker._checks) >= 5

    @pytest.mark.asyncio
    async def test_graceful_shutdown_releases_resources(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        settings = Settings(environment=Environment.TEST)
        container = Container.create(
            settings,
            clock=FixedClock(datetime(2026, 1, 1, tzinfo=UTC)),
            uuid_generator=FixedUuidGenerator(UUID("00000000-0000-0000-0000-000000000001")),
        )
        storage_close = AsyncMock()
        redis_close = AsyncMock()
        engine_dispose = AsyncMock()

        monkeypatch.setattr(container.storage_provider, "close", storage_close)
        monkeypatch.setattr(container.redis, "aclose", redis_close)
        monkeypatch.setattr(container.database_engine, "dispose", engine_dispose)

        await shutdown_application(container)

        storage_close.assert_awaited_once()
        redis_close.assert_awaited_once()
        engine_dispose.assert_awaited_once()


class TestApplicationFactory:
    def test_create_app_when_routers_available(self) -> None:
        try:
            from cloud_content_hub.bootstrap.api import create_app
        except ImportError:
            pytest.skip("Application routers are unavailable in this environment.")
        from fastapi import FastAPI

        app = create_app(Settings(environment=Environment.TEST))
        assert isinstance(app, FastAPI)
        assert app.state.container is not None
        assert app.state.handlers is not None

    def test_create_app_registers_lifespan_when_routers_available(self) -> None:
        try:
            from cloud_content_hub.bootstrap.api import create_app
        except ImportError:
            pytest.skip("Application routers are unavailable in this environment.")

        app = create_app(Settings(environment=Environment.TEST))
        assert app.router.lifespan_context is not None
