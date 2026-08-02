import os
from enum import StrEnum
from pathlib import Path
from typing import Any, Self, cast

from pydantic import AnyUrl, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CCH_",
        case_sensitive=True,
        extra="ignore",
        frozen=True,
    )

    environment: Environment = Environment.LOCAL
    service_name: str = "cloud-content-hub"
    service_version: str = "0.1.0"
    log_level: str = "INFO"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost/cloud_content_hub"
    database_pool_size: int = Field(default=5, ge=1, le=50)
    database_timeout_seconds: float = Field(default=5, gt=0, le=60)
    redis_url: AnyUrl = AnyUrl("redis://localhost:6379/0")
    redis_timeout_seconds: float = Field(default=2, gt=0, le=30)
    http_allowed_origins: list[str] = Field(default_factory=list)
    http_compression_minimum_size: int = Field(default=1000, ge=500)
    openapi_enabled: bool = True

    @model_validator(mode="after")
    def validate_production(self) -> Self:
        if self.environment is Environment.PRODUCTION:
            if not self.database_url.startswith("postgresql+asyncpg://"):
                raise ValueError("CCH_DATABASE_URL must use PostgreSQL asyncpg in production")
            if "*" in self.http_allowed_origins:
                raise ValueError("CCH_HTTP_ALLOWED_ORIGINS cannot contain '*' in production")
        return self


def load_settings(overrides: dict[str, object] | None = None) -> Settings:
    environment = Environment(
        str(
            (overrides or {}).get("environment")
            or os.environ.get("CCH_ENVIRONMENT")
            or Environment.LOCAL
        )
    )
    env_file = Path(".env") if environment in {Environment.LOCAL, Environment.TEST} else None
    values = cast(dict[str, Any], overrides or {})
    return Settings(_env_file=env_file, **values)
