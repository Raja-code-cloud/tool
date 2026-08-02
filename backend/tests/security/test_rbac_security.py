"""RBAC and function-level authorization security tests."""

from __future__ import annotations

import pytest

from cloud_content_hub.infrastructure.identity.exceptions import PermissionDenied, RoleDenied
from cloud_content_hub.infrastructure.identity.principal import Principal
from cloud_content_hub.infrastructure.identity.testing.fixtures import sample_rbac


@pytest.mark.asyncio
async def test_rbac_role_inheritance_grants_grouped_permissions() -> None:
    rbac = sample_rbac()
    principal = Principal(
        subject="editor-1",
        provider="mock",
        roles=frozenset({"editor"}),
        permissions=frozenset(),
    )
    assert await rbac.authorize(principal, "content:read") is True
    assert await rbac.authorize(principal, "content:write") is True


@pytest.mark.asyncio
async def test_rbac_denies_missing_permission() -> None:
    rbac = sample_rbac()
    principal = Principal(subject="user-1", provider="mock", roles=frozenset({"user"}))
    assert await rbac.authorize(principal, "admin:delete") is False


def test_wildcard_permission_grants_namespace_access() -> None:
    principal = Principal(
        subject="admin-1",
        provider="mock",
        permissions=frozenset({"content:*"}),
    )
    assert principal.has_permission("content:read") is True
    assert principal.has_permission("content:write") is True
    assert principal.has_permission("assets:read") is False


def test_global_wildcard_grants_all_permissions() -> None:
    principal = Principal(subject="admin-1", provider="mock", permissions=frozenset({"*"}))
    assert principal.has_permission("publishing:delete") is True


def test_require_permission_dependency_raises_for_anonymous() -> None:
    from cloud_content_hub.infrastructure.identity.dependencies import require_permission
    from cloud_content_hub.infrastructure.identity.exceptions import AuthenticationException
    from cloud_content_hub.infrastructure.identity.middleware import bind_principal, clear_principal

    dependency = require_permission("assets:read")
    token = bind_principal(Principal.anonymous())
    try:
        with pytest.raises(AuthenticationException):
            _ = dependency()
    finally:
        clear_principal(token)


def test_current_admin_requires_admin_role() -> None:
    from cloud_content_hub.infrastructure.identity.dependencies import current_admin
    from cloud_content_hub.infrastructure.identity.middleware import bind_principal, clear_principal

    token = bind_principal(
        Principal(subject="user-1", provider="mock", roles=frozenset({"user"}))
    )
    try:
        with pytest.raises(RoleDenied):
            current_admin()
    finally:
        clear_principal(token)
