"""Synthetic identity fixtures for tests."""

from __future__ import annotations

from cloud_content_hub.infrastructure.identity.config import IdentitySettings
from cloud_content_hub.infrastructure.identity.factory import IdentityFactory, generate_rsa_key_pair
from cloud_content_hub.infrastructure.identity.models import IdentityClaims, UnifiedIdentity
from cloud_content_hub.infrastructure.identity.rbac import Rbac, Role
from cloud_content_hub.infrastructure.identity.utils import utc_now


def identity_settings(**overrides: object) -> IdentitySettings:
    private_pem, _public_pem = generate_rsa_key_pair()
    defaults = {
        "environment": "test",
        "default_provider": "mock",
        "mock_enabled": True,
        "https_only": False,
        "signing_key_pem": private_pem,
    }
    defaults.update(overrides)
    return IdentitySettings(**defaults)  # type: ignore[arg-type]


def identity_factory(**overrides: object) -> IdentityFactory:
    return IdentityFactory(identity_settings(**overrides))


def sample_unified_identity() -> UnifiedIdentity:
    return UnifiedIdentity(
        user_id="user-1",
        subject="user-1",
        provider="mock",
        email="user@example.test",
        display_name="Example User",
        roles=frozenset({"user"}),
        permissions=frozenset({"profile:read", "content:read"}),
    )


def sample_claims() -> IdentityClaims:
    return IdentityClaims(
        subject="user-1",
        issuer="cloud-content-hub",
        audience=("cloud-content-hub-api",),
        expires_at=utc_now(),
        email="user@example.test",
        name="Example User",
        roles=frozenset({"user"}),
        permissions=frozenset({"profile:read"}),
        provider="mock",
    )


def sample_rbac() -> Rbac:
    return Rbac(
        roles={
            "user": Role(name="user", permissions=frozenset({"profile:read"})),
            "editor": Role(
                name="editor",
                permissions=frozenset({"content:write"}),
                inherits=frozenset({"user"}),
            ),
            "admin": Role(name="admin", permissions=frozenset({"*"})),
        },
        groups={"content:write": frozenset({"content:read"})},
    )
