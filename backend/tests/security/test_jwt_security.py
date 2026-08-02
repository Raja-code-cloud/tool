"""JWT hardening and token validation security tests."""

from __future__ import annotations

from datetime import timedelta

import jwt
import pytest

from cloud_content_hub.infrastructure.identity.config import IdentitySettings
from cloud_content_hub.infrastructure.identity.exceptions import InvalidToken, TokenExpired
from cloud_content_hub.infrastructure.identity.jwt import JwtService
from cloud_content_hub.infrastructure.identity.models import TokenType
from cloud_content_hub.infrastructure.identity.testing.fixtures import (
    identity_factory,
    identity_settings,
)
from cloud_content_hub.infrastructure.identity.utils import utc_now


@pytest.mark.asyncio
async def test_rejects_expired_access_token(jwt_service: JwtService) -> None:
    factory = identity_factory()
    service = factory.jwt_service
    private_key = factory.jwt_service._private_key
    assert private_key is not None
    token = service.create_access_token("user-1", provider="mock")
    decoded = jwt.decode(token, options={"verify_signature": False})
    decoded["exp"] = int((utc_now() - timedelta(minutes=5)).timestamp())
    expired = jwt.encode(
        decoded,
        private_key,
        algorithm="RS256",
        headers={"kid": "default"},
    )
    with pytest.raises(TokenExpired):
        await service.decode_and_verify(expired, token_type=TokenType.ACCESS)


@pytest.mark.asyncio
async def test_rejects_wrong_token_type(jwt_service: JwtService) -> None:
    refresh = jwt_service.create_refresh_token("user-1", provider="mock", token_id="jti-1")
    with pytest.raises(InvalidToken, match="unexpected token type"):
        await jwt_service.decode_and_verify(refresh, token_type=TokenType.ACCESS)


@pytest.mark.asyncio
async def test_rejects_untrusted_issuer(jwt_service: JwtService) -> None:
    token = jwt_service.create_access_token("user-1", provider="mock")
    private_key = jwt_service._private_key
    assert private_key is not None
    decoded = jwt.decode(token, options={"verify_signature": False})
    decoded["iss"] = "https://evil.example.test"
    tampered = jwt.encode(
        decoded,
        private_key,
        algorithm="RS256",
        headers={"kid": "default"},
    )
    with pytest.raises(InvalidToken):
        await jwt_service.decode_and_verify(tampered, token_type=TokenType.ACCESS)


@pytest.mark.asyncio
async def test_rejects_tampered_signature(jwt_service: JwtService) -> None:
    token = jwt_service.create_access_token("user-1", provider="mock")
    parts = token.split(".")
    tampered = f"{parts[0]}.{parts[1]}.invalidsignature"
    with pytest.raises(InvalidToken):
        await jwt_service.decode_and_verify(tampered, token_type=TokenType.ACCESS)


def test_production_rejects_hs256_algorithm() -> None:
    with pytest.raises(ValueError, match="asymmetric"):
        IdentitySettings(
            environment="production",
            allowed_algorithms=("HS256",),
            issuer="https://auth.example.test",
            mock_enabled=False,
            default_provider="entra",
            entra_enabled=True,
            entra_client_id="client",
            entra_tenant_id="tenant",
            entra_redirect_uris=("https://app.example.test/callback",),
        )


def test_production_rejects_none_algorithm() -> None:
    with pytest.raises(ValueError, match="asymmetric"):
        IdentitySettings(
            environment="production",
            allowed_algorithms=("none",),
            mock_enabled=False,
            default_provider="entra",
            entra_enabled=True,
            entra_client_id="client",
            entra_tenant_id="tenant",
            entra_redirect_uris=("https://app.example.test/callback",),
            issuer="https://auth.example.test",
        )


def test_production_rejects_mock_provider() -> None:
    with pytest.raises(ValueError, match="mock identity provider"):
        identity_settings(environment="production", mock_enabled=True)


def test_production_rejects_wildcard_cors() -> None:
    with pytest.raises(ValueError, match="wildcard CORS"):
        identity_settings(
            environment="production",
            cors_origins=("*",),
            mock_enabled=False,
            default_provider="entra",
            entra_enabled=True,
            entra_client_id="client",
            entra_tenant_id="tenant",
            entra_redirect_uris=("https://app.example.test/callback",),
            issuer="https://auth.example.test",
        )


def test_clock_skew_is_bounded() -> None:
    with pytest.raises(ValueError):
        IdentitySettings(clock_skew_seconds=400)
