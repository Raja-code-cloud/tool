"""Application token lifecycle helpers."""

from __future__ import annotations

import secrets
from dataclasses import dataclass

from .config import IdentitySettings
from .exceptions import InvalidToken
from .jwt import JwtService
from .models import TokenSet, TokenType, UnifiedIdentity
from .permissions import RevocationStore


@dataclass(frozen=True, slots=True)
class IssuedSession:
    access_token: str
    refresh_token: str
    token_id: str
    expires_in: int


class InvalidRefreshToken(InvalidToken):
    """Refresh token is invalid, expired, or revoked."""


class TokenService:
    def __init__(
        self,
        settings: IdentitySettings,
        jwt_service: JwtService,
        *,
        revocation_store: RevocationStore | None = None,
    ) -> None:
        self._settings = settings
        self._jwt = jwt_service
        self._revocation = revocation_store

    async def issue_session(self, identity: UnifiedIdentity) -> IssuedSession:
        token_id = secrets.token_urlsafe(16)
        access_token = self._jwt.create_access_token(
            identity.subject,
            provider=identity.provider,
            roles=identity.roles,
            permissions=identity.permissions,
            tenant_id=identity.tenant_id,
            email=identity.email,
            name=identity.display_name,
        )
        refresh_token = self._jwt.create_refresh_token(
            identity.subject, provider=identity.provider, token_id=token_id
        )
        return IssuedSession(
            access_token=access_token,
            refresh_token=refresh_token,
            token_id=token_id,
            expires_in=self._settings.access_token_minutes * 60,
        )

    async def refresh_access_token(self, refresh_token: str) -> TokenSet:
        decoded = await self._jwt.decode_and_verify(refresh_token, token_type=TokenType.REFRESH)
        if decoded.claims.token_id and self._revocation is not None:
            if await self._revocation.is_revoked(decoded.claims.token_id):
                raise InvalidRefreshToken("refresh token has been revoked")
        access_token = self._jwt.create_access_token(
            decoded.claims.subject,
            provider=decoded.claims.provider or "local",
            roles=decoded.claims.roles,
            permissions=decoded.claims.permissions,
            tenant_id=decoded.claims.tenant_id,
            email=decoded.claims.email,
            name=decoded.claims.name,
        )
        return TokenSet(
            access_token=access_token,
            expires_in=self._settings.access_token_minutes * 60,
        )

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        if self._revocation is None:
            return
        decoded = await self._jwt.decode_and_verify(refresh_token, token_type=TokenType.REFRESH)
        if decoded.claims.token_id:
            await self._revocation.revoke(
                decoded.claims.token_id,
                int(decoded.claims.expires_at.timestamp()),
            )
