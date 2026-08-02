"""Immutable application-facing principal."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from .models import IdentityClaims, UnifiedIdentity


@dataclass(frozen=True, slots=True)
class Principal:
    subject: str
    provider: str
    email: str | None = None
    display_name: str | None = None
    roles: frozenset[str] = frozenset()
    permissions: frozenset[str] = frozenset()
    tenant_id: str | None = None
    groups: frozenset[str] = frozenset()
    authenticated: bool = True
    claims: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "claims", MappingProxyType(dict(self.claims)))

    @classmethod
    def anonymous(cls) -> "Principal":
        return cls(subject="anonymous", provider="none", authenticated=False)

    @classmethod
    def from_unified(
        cls, identity: UnifiedIdentity, *, claims: IdentityClaims | None = None
    ) -> "Principal":
        claim_map: dict[str, object] = {}
        if claims is not None:
            claim_map = {
                "issuer": claims.issuer,
                "audience": claims.audience,
                "expires_at": claims.expires_at.isoformat(),
                "token_id": claims.token_id,
            }
        return cls(
            subject=identity.subject,
            provider=identity.provider,
            email=identity.email,
            display_name=identity.display_name,
            roles=identity.roles,
            permissions=identity.permissions,
            tenant_id=identity.tenant_id,
            groups=identity.groups,
            claims=claim_map,
        )

    def has_permission(self, required: str) -> bool:
        required_parts = required.split(":")
        return any(
            permission == "*"
            or permission == required
            or (
                permission.endswith(":*")
                and required_parts[: len(permission.split(":")) - 1]
                == permission.split(":")[:-1]
            )
            for permission in self.permissions
        )

    def has_role(self, role: str) -> bool:
        return role in self.roles
