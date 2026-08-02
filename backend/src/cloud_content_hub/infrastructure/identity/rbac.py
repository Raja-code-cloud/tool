"""Role-based authorization with inheritance and policy hooks."""

from collections.abc import Mapping
from dataclasses import dataclass

from .permissions import AttributePolicy, AuthorizationHook
from .principal import Principal


@dataclass(frozen=True, slots=True)
class Role:
    name: str
    permissions: frozenset[str] = frozenset()
    inherits: frozenset[str] = frozenset()


class Rbac:
    def __init__(
        self,
        roles: Mapping[str, Role],
        *,
        groups: Mapping[str, frozenset[str]] | None = None,
        hook: AuthorizationHook | None = None,
        attribute_policy: AttributePolicy | None = None,
    ) -> None:
        self._roles = dict(roles)
        self._groups = dict(groups or {})
        self._hook = hook
        self._attribute_policy = attribute_policy
        for role_name in roles:
            self._resolve(role_name, ())

    def _resolve(self, name: str, path: tuple[str, ...]) -> frozenset[str]:
        if name in path:
            raise ValueError(f"role inheritance cycle: {' -> '.join((*path, name))}")
        role = self._roles.get(name)
        if role is None:
            raise ValueError(f"unknown inherited role: {name}")
        permissions = set(role.permissions)
        for permission in tuple(permissions):
            permissions.update(self._groups.get(permission, ()))
        for parent in role.inherits:
            permissions.update(self._resolve(parent, (*path, name)))
        return frozenset(permissions)

    def permissions_for(self, roles: frozenset[str]) -> frozenset[str]:
        permissions: set[str] = set()
        for role in roles:
            permissions.update(self._resolve(role, ()))
        return frozenset(permissions)

    async def authorize(
        self, principal: Principal, permission: str, resource: object | None = None
    ) -> bool:
        effective = Principal(
            subject=principal.subject,
            provider=principal.provider,
            email=principal.email,
            display_name=principal.display_name,
            roles=principal.roles,
            permissions=principal.permissions | self.permissions_for(principal.roles),
            tenant_id=principal.tenant_id,
            groups=principal.groups,
            authenticated=principal.authenticated,
            claims=principal.claims,
        )
        if effective.has_permission(permission):
            return True
        if self._hook is not None and await self._hook(effective, permission, resource):
            return True
        return bool(
            self._attribute_policy is not None
            and await self._attribute_policy.authorize(effective, permission, resource)
        )
