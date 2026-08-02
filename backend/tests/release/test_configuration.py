"""Release validation for application configuration and production invariants."""

from __future__ import annotations

from pathlib import Path

import pytest

from cloud_content_hub.bootstrap.configuration import load_bootstrap_configuration
from cloud_content_hub.core.config import Environment, Settings, load_settings
from cloud_content_hub.infrastructure.identity.config import IdentitySettings

pytestmark = pytest.mark.release

BACKEND_ROOT = Path(__file__).resolve().parents[2]
ENV_EXAMPLE = BACKEND_ROOT / ".env.example"


class TestSettingsValidation:
    def test_test_environment_loads(self) -> None:
        settings = Settings(environment=Environment.TEST)
        assert settings.environment is Environment.TEST

    def test_production_rejects_wildcard_cors(self) -> None:
        with pytest.raises(ValueError, match="cannot contain '\\*'"):
            Settings(
                environment=Environment.PRODUCTION,
                http_allowed_origins=["*"],
            )

    def test_production_requires_asyncpg_database_url(self) -> None:
        with pytest.raises(ValueError, match="postgresql\\+asyncpg"):
            Settings(
                environment=Environment.PRODUCTION,
                database_url="postgresql://user:pass@host/db",
            )

    def test_production_accepts_valid_configuration(self) -> None:
        settings = Settings(
            environment=Environment.PRODUCTION,
            database_url="postgresql+asyncpg://user:pass@host:5432/db",
            http_allowed_origins=["https://app.example.com"],
            openapi_enabled=False,
        )
        assert settings.environment is Environment.PRODUCTION

    def test_load_settings_respects_overrides(self) -> None:
        settings = load_settings({"environment": Environment.TEST, "log_level": "DEBUG"})
        assert settings.environment is Environment.TEST
        assert settings.log_level == "DEBUG"


class TestBootstrapConfiguration:
    def test_loads_for_test_environment(self) -> None:
        settings = Settings(environment=Environment.TEST)
        config = load_bootstrap_configuration(settings)
        assert config.settings.environment is Environment.TEST
        assert config.identity.environment == "test"
        assert config.ai.primary_kind is not None

    def test_storage_uses_test_defaults(self) -> None:
        settings = Settings(environment=Environment.TEST)
        config = load_bootstrap_configuration(settings)
        assert config.storage.auto_create_containers is True


class TestIdentityProductionInvariants:
    def test_mock_provider_rejected_in_production(self) -> None:
        with pytest.raises(ValueError, match="mock identity provider must be disabled"):
            IdentitySettings(environment="production", mock_enabled=True)

    def test_mock_default_provider_rejected_in_production(self) -> None:
        with pytest.raises(ValueError, match="mock cannot be the production"):
            IdentitySettings(
                environment="production",
                mock_enabled=False,
                default_provider="mock",
            )


class TestEnvironmentTemplate:
    def test_env_example_exists(self) -> None:
        assert ENV_EXAMPLE.is_file()

    def test_env_example_keys_use_cch_prefix(self) -> None:
        keys = {
            line.split("=", 1)[0]
            for line in ENV_EXAMPLE.read_text(encoding="utf-8").splitlines()
            if line and not line.startswith("#")
        }
        invalid = sorted(key for key in keys if not key.startswith("CCH_"))
        assert invalid == [], f"Non-prefixed keys in .env.example: {invalid}"
        assert len(keys) >= 10
