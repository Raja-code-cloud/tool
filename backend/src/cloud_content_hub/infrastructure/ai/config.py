"""Immutable AI provider configuration."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator

from cloud_content_hub.infrastructure.ai.exceptions import AIConfigurationError


class ProviderKind(StrEnum):
    OPENAI = "openai"
    AZURE_OPENAI = "azure_openai"
    CLAUDE = "claude"
    GEMINI = "gemini"
    MOCK = "mock"
    FUTURE = "future"


class RateLimitConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    requests_per_minute: int | None = Field(default=None, gt=0)
    tokens_per_minute: int | None = Field(default=None, gt=0)


class SafetyConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    enabled: bool = True
    policy: str | None = None
    max_prompt_tokens: int | None = Field(default=None, gt=0)
    max_prompt_characters: int | None = Field(default=None, gt=0)


class ProviderConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    kind: ProviderKind
    model: str
    api_key: SecretStr | None = Field(default=None, repr=False)
    endpoint: str | None = None
    azure_deployment: str | None = None
    api_version: str | None = None
    timeout_seconds: float = Field(default=30, gt=0)
    retries: int = Field(default=3, ge=0)
    default_temperature: float = Field(default=0.7, ge=0, le=2)
    default_max_tokens: int = Field(default=1024, gt=0)
    streaming: bool = True
    rate_limit: RateLimitConfig = RateLimitConfig()
    safety: SafetyConfig = SafetyConfig()

    @model_validator(mode="after")
    def validate_provider(self) -> "ProviderConfig":
        if self.kind is ProviderKind.AZURE_OPENAI and (
            not self.endpoint or not self.azure_deployment or not self.api_version
        ):
            raise AIConfigurationError("Azure endpoint, deployment, and API version are required")
        if self.kind is ProviderKind.FUTURE:
            return self
        if self.kind is not ProviderKind.MOCK and self.api_key is None:
            raise AIConfigurationError("API key is required")
        return self


class AIConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    providers: tuple[ProviderConfig, ...]
    primary_kind: ProviderKind | None = None
    fallback_kind: ProviderKind | None = None
    fallback_enabled: bool = True
