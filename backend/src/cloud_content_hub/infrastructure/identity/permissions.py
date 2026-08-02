"""Authorization extension contracts."""

from collections.abc import Awaitable, Callable
from typing import Protocol

from .principal import Principal

AuthorizationHook = Callable[[Principal, str, object | None], Awaitable[bool]]


class AttributePolicy(Protocol):
    async def authorize(
        self, principal: Principal, permission: str, resource: object | None = None
    ) -> bool: ...


class CsrfProtector(Protocol):
    async def validate(self, token: str, expected: str) -> bool: ...


class ReplayProtector(Protocol):
    async def consume(self, token_id: str, expires_at: int) -> bool: ...


class RevocationStore(Protocol):
    async def is_revoked(self, token_id: str) -> bool: ...

    async def revoke(self, token_id: str, expires_at: int) -> None: ...


class SecretRotationProvider(Protocol):
    async def active_secret(self, name: str) -> str: ...
