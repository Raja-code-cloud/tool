"""Bootstrap configuration loading and validation."""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from cloud_content_hub.core.config import Environment, Settings
from cloud_content_hub.infrastructure.ai.config import AIConfig, ProviderConfig, ProviderKind
from cloud_content_hub.infrastructure.identity.config import IdentitySettings
from cloud_content_hub.infrastructure.observability.config import ObservabilityConfig
from cloud_content_hub.infrastructure.storage.config import AzureCredentialMode, AzureStorageConfig


class AzureStorageSettings(BaseSettings):
    """Azure Blob settings loaded from ``CCH_AZURE_STORAGE_*`` variables."""

    model_config = SettingsConfigDict(env_prefix="CCH_AZURE_STORAGE_", extra="ignore")

    account_url: str = "https://example.blob.core.windows.net"
    credential_mode: AzureCredentialMode = AzureCredentialMode.MANAGED_IDENTITY
    connection_string: str | None = Field(default=None, repr=False)
    tenant_id: str | None = None
    client_id: str | None = None
    client_secret: str | None = Field(default=None, repr=False)
    managed_identity_client_id: str | None = None
    public_base_url: str | None = None
    auto_create_containers: bool = False
    max_size_bytes: int = Field(default=100 * 1024 * 1024, gt=0)
    upload_chunk_size_bytes: int = Field(default=4 * 1024 * 1024, gt=0)
    download_chunk_size_bytes: int = Field(default=4 * 1024 * 1024, gt=0)
    timeout_seconds: float = Field(default=30.0, gt=0)
    retry_total: int = Field(default=3, ge=0)
    retry_backoff_seconds: float = Field(default=0.8, ge=0)


@dataclass(frozen=True, slots=True)
class BootstrapConfiguration:
    """Immutable aggregate of typed settings consumed by the composition root."""

    settings: Settings
    identity: IdentitySettings
    observability: ObservabilityConfig
    storage: AzureStorageConfig
    ai: AIConfig


def _build_identity_settings(settings: Settings) -> IdentitySettings:
    return IdentitySettings(environment=settings.environment.value)


def _build_observability_config(settings: Settings) -> ObservabilityConfig:
    return ObservabilityConfig(
        service_name=settings.service_name,
        service_version=settings.service_version,
        environment=settings.environment.value,
    )


def _build_storage_config(
    settings: Settings,
    azure_settings: AzureStorageSettings,
) -> AzureStorageConfig:
    if settings.environment in {Environment.LOCAL, Environment.TEST}:
        return AzureStorageConfig(
            account_url="https://storage.test",
            credential_mode=AzureCredentialMode.MANAGED_IDENTITY,
            auto_create_containers=True,
        )
    return AzureStorageConfig(
        account_url=azure_settings.account_url,
        credential_mode=azure_settings.credential_mode,
        connection_string=azure_settings.connection_string,
        tenant_id=azure_settings.tenant_id,
        client_id=azure_settings.client_id,
        client_secret=azure_settings.client_secret,
        managed_identity_client_id=azure_settings.managed_identity_client_id,
        public_base_url=azure_settings.public_base_url,
        auto_create_containers=azure_settings.auto_create_containers,
        max_size_bytes=azure_settings.max_size_bytes,
        upload_chunk_size_bytes=azure_settings.upload_chunk_size_bytes,
        download_chunk_size_bytes=azure_settings.download_chunk_size_bytes,
        timeout_seconds=azure_settings.timeout_seconds,
        retry_total=azure_settings.retry_total,
        retry_backoff_seconds=azure_settings.retry_backoff_seconds,
    )


def _build_ai_config(settings: Settings) -> AIConfig:
    if settings.environment in {Environment.LOCAL, Environment.TEST}:
        mock = ProviderConfig(
            kind=ProviderKind.MOCK,
            model="mock",
            api_key=SecretStr("local-mock"),
        )
        return AIConfig(providers=(mock,), primary_kind=ProviderKind.MOCK, fallback_enabled=False)
    mock = ProviderConfig(
        kind=ProviderKind.MOCK,
        model="mock",
        api_key=SecretStr("fallback-mock"),
    )
    return AIConfig(providers=(mock,), primary_kind=ProviderKind.MOCK, fallback_enabled=False)


def load_bootstrap_configuration(settings: Settings) -> BootstrapConfiguration:
    """Load and validate all infrastructure configuration for bootstrap wiring."""

    azure_settings = AzureStorageSettings()
    identity = _build_identity_settings(settings)
    observability = _build_observability_config(settings)
    storage = _build_storage_config(settings, azure_settings)
    ai = _build_ai_config(settings)
    return BootstrapConfiguration(
        settings=settings,
        identity=identity,
        observability=observability,
        storage=storage,
        ai=ai,
    )
