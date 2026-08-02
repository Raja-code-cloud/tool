import pytest

from cloud_content_hub.infrastructure.identity.claims import (
    map_entra_claims,
    map_google_claims,
    to_unified_identity,
)
from cloud_content_hub.infrastructure.identity.models import TokenType
from cloud_content_hub.infrastructure.identity.principal import Principal
from cloud_content_hub.infrastructure.identity.testing.fixtures import identity_factory, sample_rbac
from cloud_content_hub.infrastructure.identity.utils import (
    generate_code_challenge,
    generate_code_verifier,
)


def test_pkce_challenge_is_deterministic() -> None:
    verifier = generate_code_verifier()
    assert generate_code_challenge(verifier) == generate_code_challenge(verifier)


def test_claim_mapping_normalizes_provider_fields() -> None:
    claims = map_entra_claims(
        {
            "sub": "abc",
            "iss": "https://login.microsoftonline.com/tenant/v2.0",
            "aud": "client",
            "exp": 4102444800,
            "roles": ["Admin"],
            "groups": ["engineering"],
            "email": "user@example.test",
        }
    )
    unified = to_unified_identity(claims)
    assert unified.provider == "entra"
    assert unified.roles == frozenset({"Admin"})
    assert unified.groups == frozenset({"engineering"})


def test_google_claim_mapping() -> None:
    claims = map_google_claims(
        {
            "sub": "google-user",
            "iss": "https://accounts.google.com",
            "aud": "client",
            "exp": 4102444800,
            "email": "user@gmail.com",
            "given_name": "Example",
        }
    )
    assert claims.email == "user@gmail.com"
    assert claims.name == "Example"


@pytest.mark.asyncio
async def test_jwt_issue_and_verify_round_trip() -> None:
    factory = identity_factory()
    jwt_service = factory.jwt_service
    token = jwt_service.create_access_token(
        "user-1",
        provider="mock",
        roles=frozenset({"user"}),
        permissions=frozenset({"profile:read"}),
    )
    decoded = await jwt_service.decode_and_verify(token, token_type=TokenType.ACCESS)
    assert decoded.claims.subject == "user-1"
    assert decoded.claims.permissions == frozenset({"profile:read"})


@pytest.mark.asyncio
async def test_mock_provider_exchange_issues_application_tokens() -> None:
    factory = identity_factory()
    registry = factory.build_registry()
    provider = registry.get("mock")
    auth = await provider.authenticate("http://localhost:3000/callback")
    code = provider.issue_mock_code("alice")  # type: ignore[attr-defined]
    result = await provider.exchange_code(
        code,
        "http://localhost:3000/callback",
        state=auth.state,
        expected_state=auth.state,
        nonce=auth.nonce,
        code_verifier=auth.code_verifier,
    )
    assert result.user.email == "alice@example.test"
    assert result.tokens is not None
    assert result.tokens.access_token


@pytest.mark.asyncio
async def test_token_refresh_and_revocation() -> None:
    from cloud_content_hub.infrastructure.identity.factory import IdentityFactory
    from cloud_content_hub.infrastructure.identity.testing.fixtures import identity_settings
    from cloud_content_hub.infrastructure.identity.testing.revocation import InMemoryRevocationStore
    from cloud_content_hub.infrastructure.identity.tokens import InvalidRefreshToken, TokenService

    settings = identity_settings()
    factory = IdentityFactory(settings)
    revocation = InMemoryRevocationStore()
    token_service = TokenService(settings, factory.jwt_service, revocation_store=revocation)
    session = await token_service.issue_session(
        to_unified_identity(
            map_google_claims(
                {
                    "sub": "user-1",
                    "iss": "cloud-content-hub",
                    "aud": "cloud-content-hub-api",
                    "exp": 4102444800,
                    "provider": "mock",
                }
            )
        )
    )
    refreshed = await token_service.refresh_access_token(session.refresh_token)
    assert refreshed.access_token
    await token_service.revoke_refresh_token(session.refresh_token)
    with pytest.raises(InvalidRefreshToken):
        await token_service.refresh_access_token(session.refresh_token)


@pytest.mark.asyncio
async def test_rbac_inheritance_and_groups() -> None:
    rbac = sample_rbac()
    principal = Principal(
        subject="user-1",
        provider="mock",
        roles=frozenset({"editor"}),
    )
    assert await rbac.authorize(principal, "profile:read")
    assert await rbac.authorize(principal, "content:read")
    assert await rbac.authorize(principal, "content:write")
    assert not await rbac.authorize(principal, "billing:manage")


def test_principal_permission_wildcards() -> None:
    principal = Principal(
        subject="admin",
        provider="mock",
        permissions=frozenset({"content:*"}),
    )
    assert principal.has_permission("content:read")
    assert principal.has_permission("content:write")
    assert not principal.has_permission("billing:read")


def test_registry_lists_enabled_providers() -> None:
    factory = identity_factory()
    registry = factory.build_registry()
    codes = {descriptor.code for descriptor in registry.descriptors()}
    assert "mock" in codes
