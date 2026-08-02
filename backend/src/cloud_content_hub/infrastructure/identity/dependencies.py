"""Reusable FastAPI identity dependencies."""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, Request

from .exceptions import AuthenticationException, PermissionDenied, RoleDenied
from .middleware import get_current_principal, require_bearer_token
from .principal import Principal
from .rbac import Rbac


def authenticated_principal() -> Principal:
    principal = get_current_principal()
    if not principal.authenticated:
        raise AuthenticationException("authentication is required")
    return principal


def optional_principal() -> Principal:
    return get_current_principal()


def current_user() -> Principal:
    return authenticated_principal()


def optional_user() -> Principal:
    return optional_principal()


def current_admin() -> Principal:
    principal = authenticated_principal()
    if not principal.has_role("admin"):
        raise RoleDenied("admin role is required")
    return principal


def require_role(role: str) -> Callable[[], Principal]:
    def dependency() -> Principal:
        principal = authenticated_principal()
        if not principal.has_role(role):
            raise RoleDenied(f"role '{role}' is required")
        return principal

    return dependency


def require_permission(
    permission: str, rbac: Rbac | None = None
) -> Callable[[], Principal]:
    async def dependency() -> Principal:
        principal = authenticated_principal()
        if rbac is None:
            if not principal.has_permission(permission):
                raise PermissionDenied(f"permission '{permission}' is required")
            return principal
        if not await rbac.authorize(principal, permission):
            raise PermissionDenied(f"permission '{permission}' is required")
        return principal

    return dependency


AuthenticatedPrincipal = Annotated[Principal, Depends(authenticated_principal)]
CurrentUser = Annotated[Principal, Depends(current_user)]
OptionalUser = Annotated[Principal, Depends(optional_user)]
CurrentAdmin = Annotated[Principal, Depends(current_admin)]


def bearer_token(request: Request) -> str:
    return require_bearer_token(request)

BearerToken = Annotated[str, Depends(bearer_token)]
