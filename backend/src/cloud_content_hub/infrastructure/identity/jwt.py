"""JWT encoding, decoding, verification, and JWKS retrieval."""

from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any

import httpx
import jwt
from cryptography.hazmat.primitives import serialization
from jwt import PyJWKClient, PyJWTError

from .claims import map_standard_claims, to_unified_identity
from .config import IdentitySettings
from .exceptions import InvalidToken, ProviderUnavailable, TokenExpired, TokenValidationError
from .models import DecodedToken, TokenType, UnifiedIdentity
from .utils import utc_now


@dataclass
class JwksCache:
    client: PyJWKClient
    fetched_at: datetime = field(default_factory=utc_now)


class JwtService:
    def __init__(
        self,
        settings: IdentitySettings,
        *,
        private_key_pem: str | None = None,
        public_key_pem: str | None = None,
    ) -> None:
        self._settings = settings
        self._private_key = private_key_pem or settings.signing_key_pem
        self._public_key = public_key_pem or self._derive_public_key(self._private_key)
        self._jwks_clients: dict[str, JwksCache] = {}
        self._lock = asyncio.Lock()

    @staticmethod
    def _derive_public_key(private_key_pem: str | None) -> str | None:
        if private_key_pem is None:
            return None
        private_key = serialization.load_pem_private_key(
            private_key_pem.encode("ascii"),
            password=None,
        )
        public_key = private_key.public_key()
        return public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        ).decode("ascii")

    def create_access_token(
        self,
        subject: str,
        *,
        provider: str,
        roles: frozenset[str] = frozenset(),
        permissions: frozenset[str] = frozenset(),
        tenant_id: str | None = None,
        email: str | None = None,
        name: str | None = None,
        extra: Mapping[str, object] | None = None,
    ) -> str:
        if not self._private_key:
            raise TokenValidationError("signing key is not configured")
        now = utc_now()
        payload: dict[str, object] = {
            "sub": subject,
            "iss": self._settings.issuer,
            "aud": self._settings.audience,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=self._settings.access_token_minutes)).timestamp()),
            "provider": provider,
            "roles": sorted(roles),
            "permissions": sorted(permissions),
            "token_type": TokenType.ACCESS.value,
        }
        if tenant_id:
            payload["tenant_id"] = tenant_id
        if email:
            payload["email"] = email
        if name:
            payload["name"] = name
        if extra:
            payload.update(dict(extra))
        return jwt.encode(
            payload,
            self._private_key,
            algorithm=self._settings.allowed_algorithms[0],
            headers={"kid": self._settings.signing_key_id},
        )

    def create_refresh_token(self, subject: str, *, provider: str, token_id: str) -> str:
        if not self._private_key:
            raise TokenValidationError("signing key is not configured")
        now = utc_now()
        payload = {
            "sub": subject,
            "iss": self._settings.issuer,
            "aud": self._settings.audience,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(days=self._settings.refresh_token_days)).timestamp()),
            "provider": provider,
            "jti": token_id,
            "token_type": TokenType.REFRESH.value,
        }
        return jwt.encode(
            payload,
            self._private_key,
            algorithm=self._settings.allowed_algorithms[0],
            headers={"kid": self._settings.signing_key_id},
        )

    async def decode_and_verify(
        self,
        token: str,
        *,
        token_type: TokenType = TokenType.ACCESS,
        jwks_url: str | None = None,
        issuer: str | None = None,
        audience: str | None = None,
    ) -> DecodedToken:
        try:
            header = jwt.get_unverified_header(token)
            key = await self._resolve_verification_key(token, header, jwks_url)
            decoded = jwt.decode(
                token,
                key,
                algorithms=list(self._settings.allowed_algorithms),
                audience=audience or self._settings.audience,
                issuer=issuer or self._settings.issuer,
                leeway=self._settings.clock_skew_seconds,
                options={"require": ["exp", "sub", "iss", "aud"]},
            )
        except jwt.ExpiredSignatureError as error:
            raise TokenExpired("token has expired") from error
        except PyJWTError as error:
            raise InvalidToken("token verification failed") from error

        claims = map_standard_claims(decoded, provider=str(decoded.get("provider", "local")))
        if claims.token_type != token_type:
            raise InvalidToken("unexpected token type")
        self._validate_issuer(claims.issuer)
        return DecodedToken(claims=claims, raw_header=dict(header))

    def decode_unverified(self, token: str) -> Mapping[str, Any]:
        return jwt.decode(token, options={"verify_signature": False})

    async def _resolve_verification_key(
        self, token: str, header: Mapping[str, Any], jwks_url: str | None
    ) -> str | jwt.PyJWK:
        if jwks_url:
            client = await self._get_jwks_client(jwks_url)
            try:
                signing_key = client.get_signing_key_from_jwt(token)
            except PyJWTError as error:
                raise InvalidToken("unable to resolve signing key") from error
            return signing_key.key
        if self._public_key:
            return self._public_key
        if self._private_key:
            return self._private_key
        raise TokenValidationError("verification key source is not configured")

    async def _get_jwks_client(self, jwks_url: str) -> PyJWKClient:
        async with self._lock:
            cached = self._jwks_clients.get(jwks_url)
            if cached is not None:
                age = utc_now() - cached.fetched_at
                if age.total_seconds() <= self._settings.jwks_cache_seconds:
                    return cached.client
            try:
                client = PyJWKClient(
                    jwks_url,
                    cache_keys=True,
                    lifespan=self._settings.jwks_cache_seconds,
                )
            except Exception as error:
                raise ProviderUnavailable("jwks client initialization failed") from error
            self._jwks_clients[jwks_url] = JwksCache(client=client)
            return client

    def _validate_issuer(self, issuer: str) -> None:
        allowed = self._settings.effective_allowed_issuers
        if allowed and issuer not in allowed:
            raise InvalidToken("issuer is not trusted")

    async def verify_external_token(
        self,
        token: str,
        *,
        jwks_url: str,
        issuer: str,
        audience: str | tuple[str, ...],
        provider: str,
    ) -> UnifiedIdentity:
        try:
            header = jwt.get_unverified_header(token)
            key = await self._resolve_verification_key(token, header, jwks_url)
            decoded = jwt.decode(
                token,
                key,
                algorithms=list(self._settings.allowed_algorithms),
                audience=audience,
                issuer=issuer,
                leeway=self._settings.clock_skew_seconds,
            )
        except jwt.ExpiredSignatureError as error:
            raise TokenExpired("external token has expired") from error
        except PyJWTError as error:
            raise InvalidToken("external token verification failed") from error
        claims = map_standard_claims(decoded, provider=provider, token_type=TokenType.ID)
        return to_unified_identity(claims)


class JwksHealthChecker:
    def __init__(self, *, timeout_seconds: float = 5.0) -> None:
        self._timeout = timeout_seconds

    async def check(self, jwks_url: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(jwks_url)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPError:
            return False
        keys = payload.get("keys")
        return isinstance(keys, list) and len(keys) > 0
