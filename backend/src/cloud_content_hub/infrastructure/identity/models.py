"""Provider-neutral identity value objects."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from types import MappingProxyType


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    ID = "id"


class ProviderCode(StrEnum):
    ENTRA = "entra"
    GOOGLE = "google"
    MOCK = "mock"
    PLACEHOLDER = "placeholder"


@dataclass(frozen=True, slots=True)
class IdentityClaims:
    subject: str
    issuer: str
    audience: tuple[str, ...]
    expires_at: datetime
    issued_at: datetime | None = None
    not_before: datetime | None = None
    email: str | None = None
    name: str | None = None
    tenant_id: str | None = None
    roles: frozenset[str] = frozenset()
    groups: frozenset[str] = frozenset()
    permissions: frozenset[str] = frozenset()
    provider: str | None = None
    profile_picture: str | None = None
    token_id: str | None = None
    token_type: TokenType = TokenType.ACCESS


@dataclass(frozen=True, slots=True)
class UnifiedIdentity:
    """Application-facing identity mapped from provider-specific claims."""

    user_id: str
    subject: str
    provider: str
    email: str | None = None
    display_name: str | None = None
    tenant_id: str | None = None
    roles: frozenset[str] = frozenset()
    groups: frozenset[str] = frozenset()
    permissions: frozenset[str] = frozenset()
    profile_picture: str | None = None


@dataclass(frozen=True, slots=True)
class UserIdentity:
    subject: str
    provider: str
    email: str | None = None
    display_name: str | None = None
    tenant_id: str | None = None
    roles: frozenset[str] = frozenset()
    groups: frozenset[str] = frozenset()
    permissions: frozenset[str] = frozenset()
    profile_picture: str | None = None


@dataclass(frozen=True, slots=True)
class TokenSet:
    access_token: str
    token_type: str = "Bearer"
    expires_in: int | None = None
    refresh_token: str | None = None
    id_token: str | None = None
    scope: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DecodedToken:
    claims: IdentityClaims
    raw_header: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "raw_header", MappingProxyType(dict(self.raw_header)))


@dataclass(frozen=True, slots=True)
class ProviderHealth:
    healthy: bool
    provider: str
    detail: str = "ok"
    checked_at: datetime | None = None
    jwks_available: bool | None = None
    issuer_valid: bool | None = None


@dataclass(frozen=True, slots=True)
class AuthenticationResult:
    user: UserIdentity
    claims: IdentityClaims
    tokens: TokenSet | None = None
    unified: UnifiedIdentity | None = None


@dataclass(frozen=True, slots=True)
class AuthorizationRequest:
    url: str
    state: str
    nonce: str
    code_verifier: str
    code_challenge: str
    provider: str


@dataclass(frozen=True, slots=True)
class AuthContext:
    correlation_id: str
    attributes: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "attributes", MappingProxyType(dict(self.attributes)))


@dataclass(frozen=True, slots=True)
class ProviderDescriptor:
    code: str
    name: str
    authorization_url: str | None
    pkce_required: bool
    enabled: bool = True
