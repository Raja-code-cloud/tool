"""Typed identity configuration and production safety checks."""

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class CookieSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    name: str = "cch_refresh"
    path: str = "/api/v1/auth"
    domain: str | None = None
    secure: bool = True
    httponly: bool = True
    samesite: str = "lax"


class IdentitySettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CCH_IDENTITY_", extra="ignore")

    environment: str = "local"
    default_provider: str = "mock"
    issuer: str = "cloud-content-hub"
    audience: str = "cloud-content-hub-api"
    allowed_algorithms: tuple[str, ...] = ("RS256", "ES256")
    allowed_issuers: tuple[str, ...] = ()
    clock_skew_seconds: int = Field(default=30, ge=0, le=300)
    jwks_cache_seconds: int = Field(default=300, ge=1)
    access_token_minutes: int = Field(default=15, ge=1)
    refresh_token_days: int = Field(default=30, ge=1)
    correlation_header: str = "X-Correlation-ID"
    csrf_header: str = "X-CSRF-Token"
    https_only: bool = True

    entra_enabled: bool = False
    entra_client_id: str | None = None
    entra_client_secret: str | None = None
    entra_tenant_id: str | None = None
    entra_authority: str | None = None
    entra_scopes: tuple[str, ...] = ("openid", "profile", "email", "offline_access")
    entra_redirect_uris: tuple[str, ...] = ()
    entra_jwks_url: str | None = None

    google_enabled: bool = False
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_scopes: tuple[str, ...] = ("openid", "email", "profile")
    google_redirect_uris: tuple[str, ...] = ()
    google_jwks_url: str = "https://www.googleapis.com/oauth2/v3/certs"
    google_authority: str = "https://accounts.google.com"

    mock_enabled: bool = True
    mock_redirect_uris: tuple[str, ...] = ("http://localhost:3000/callback",)

    placeholder_enabled: bool = False

    cookie: CookieSettings = Field(default_factory=CookieSettings)
    cors_origins: tuple[str, ...] = ()

    signing_key_pem: str | None = Field(default=None, repr=False)
    signing_key_id: str = "default"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> tuple[str, ...]:
        if value is None or value == "":
            return ()
        if isinstance(value, str):
            return tuple(part.strip() for part in value.split(",") if part.strip())
        if isinstance(value, (list, tuple)):
            return tuple(str(item) for item in value)
        raise ValueError("cors_origins must be a comma-separated string or sequence")

    @model_validator(mode="after")
    def secure_production(self) -> "IdentitySettings":
        env = self.environment.lower()
        if env in {"production", "prod"}:
            if self.mock_enabled:
                raise ValueError("mock identity provider must be disabled in production")
            if self.default_provider == "mock":
                raise ValueError("mock cannot be the production identity provider")
            if not self.issuer.startswith("https://"):
                raise ValueError("production issuer must use HTTPS")
            if not self.cookie.secure:
                raise ValueError("secure cookies are required in production")
            if "*" in self.cors_origins:
                raise ValueError("wildcard CORS origins are prohibited in production")
        if any(
            algorithm.startswith("HS") or algorithm == "none"
            for algorithm in self.allowed_algorithms
        ):
            raise ValueError("only approved asymmetric JWT algorithms are allowed")
        if self.entra_enabled and not all(
            (self.entra_client_id, self.entra_tenant_id, self.entra_redirect_uris)
        ):
            raise ValueError("entra provider requires client_id, tenant_id, and redirect_uris")
        if self.google_enabled and not all(
            (self.google_client_id, self.google_client_secret, self.google_redirect_uris)
        ):
            raise ValueError("google provider requires client_id, client_secret, and redirect_uris")
        return self

    @property
    def effective_allowed_issuers(self) -> tuple[str, ...]:
        issuers = list(self.allowed_issuers)
        if self.issuer not in issuers:
            issuers.append(self.issuer)
        if self.entra_enabled and self.entra_tenant_id:
            issuers.append(f"https://login.microsoftonline.com/{self.entra_tenant_id}/v2.0")
        if self.google_enabled:
            issuers.append(self.google_authority)
        return tuple(dict.fromkeys(issuers))

    def entra_authority_url(self) -> str:
        if self.entra_authority:
            return self.entra_authority.rstrip("/")
        if not self.entra_tenant_id:
            raise ValueError("entra tenant_id is required")
        return f"https://login.microsoftonline.com/{self.entra_tenant_id}"

    def entra_jwks_uri(self) -> str:
        if self.entra_jwks_url:
            return self.entra_jwks_url
        return f"{self.entra_authority_url()}/discovery/v2.0/keys"

    def validate_redirect_uri(self, provider: str, redirect_uri: str) -> None:
        allowed: tuple[str, ...]
        match provider:
            case "entra":
                allowed = self.entra_redirect_uris
            case "google":
                allowed = self.google_redirect_uris
            case "mock":
                allowed = self.mock_redirect_uris
            case _:
                raise ValueError(f"unknown provider for redirect validation: {provider}")
        if redirect_uri not in allowed:
            raise ValueError("redirect_uri is not registered for provider")
