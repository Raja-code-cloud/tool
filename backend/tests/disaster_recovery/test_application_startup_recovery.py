"""Validate application startup behavior after simulated recovery."""

from __future__ import annotations

import pytest

from cloud_content_hub.bootstrap.configuration import load_bootstrap_configuration
from cloud_content_hub.bootstrap.container import Container
from cloud_content_hub.core.config import Environment, Settings
from cloud_content_hub.infrastructure.observability.health import HealthStatus
from tests.disaster_recovery.helpers.simulation import (
    DependencyState,
    build_recovery_health_checker,
)


class TestApplicationStartupRecovery:
    @pytest.mark.asyncio
    async def test_container_starts_in_test_environment(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        async def noop_startup(_container: Container) -> None:
            return None

        monkeypatch.setattr(
            "cloud_content_hub.bootstrap.startup.startup_application",
            noop_startup,
        )

        container = Container.create(Settings(environment=Environment.TEST))
        await container.startup()

        assert container.started_at is not None
        assert len(container.health_checker._checks) == 5

    def test_bootstrap_configuration_loads_for_test(self) -> None:
        settings = Settings(environment=Environment.TEST)
        config = load_bootstrap_configuration(settings)

        assert config.settings.environment is Environment.TEST
        assert config.identity.environment == "test"

    @pytest.mark.asyncio
    async def test_health_checker_reports_healthy_after_all_dependencies_recover(self) -> None:
        checker = build_recovery_health_checker(DependencyState())
        aggregate = await checker.check()

        assert aggregate.status is HealthStatus.HEALTHY
        assert all(result.status is HealthStatus.HEALTHY for result in aggregate.checks)

    def test_production_settings_validate_asyncpg_driver(self) -> None:
        settings = Settings(
            environment=Environment.PRODUCTION,
            database_url="postgresql+asyncpg://user:pass@localhost:5432/cch",
            http_allowed_origins=["https://app.example.com"],
        )
        assert settings.environment is Environment.PRODUCTION

    def test_production_settings_reject_invalid_database_url(self) -> None:
        with pytest.raises(ValueError):
            Settings(
                environment=Environment.PRODUCTION,
                database_url="postgresql://user:pass@localhost:5432/cch",
                http_allowed_origins=["https://app.example.com"],
            )
