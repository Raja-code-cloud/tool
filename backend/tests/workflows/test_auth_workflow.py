"""End-to-end authentication and authorization workflow tests."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from cloud_content_hub.api.dependencies import build_actor_context
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.core.errors import AuthorizationError
from cloud_content_hub.infrastructure.identity.claims import to_unified_identity
from cloud_content_hub.infrastructure.identity.principal import Principal
from cloud_content_hub.infrastructure.identity.exceptions import InvalidToken, OAuthValidationError
from cloud_content_hub.infrastructure.identity.testing.fixtures import identity_factory
from tests.fixtures.auth import issue_access_token, workflow_actor
from tests.fixtures.seed import E2ESeedBundle

pytestmark = pytest.mark.e2e


@pytest.mark.asyncio
async def test_mock_provider_login_issues_tokens() -> None:
    """User login via mock OAuth provider issues application tokens."""

    factory = identity_factory()
    registry = factory.build_registry()
    provider = registry.get("mock")
    auth = await provider.authenticate("http://localhost:3000/callback")
    code = provider.issue_mock_code("e2e-user")  # type: ignore[attr-defined]
    result = await provider.exchange_code(
        code,
        "http://localhost:3000/callback",
        state=auth.state,
        expected_state=auth.state,
        nonce=auth.nonce,
        code_verifier=auth.code_verifier,
    )

    assert result.tokens is not None
    assert result.tokens.access_token
    assert result.user.email == "e2e-user@example.test"


@pytest.mark.asyncio
async def test_workspace_selection_scopes_actor(e2e_seed: E2ESeedBundle) -> None:
    """Workspace selection binds the actor to the requested tenant."""

    token = issue_access_token(user_id=e2e_seed.user_id)
    factory = identity_factory()
    decoded = await factory.jwt_service.decode_and_verify(token)
    principal = Principal.from_unified(to_unified_identity(decoded.claims), claims=decoded.claims)
    actor = build_actor_context(principal, e2e_seed.workspace_id)

    assert actor.workspace_id == e2e_seed.workspace_id
    assert actor.user_id == e2e_seed.user_id


@pytest.mark.asyncio
async def test_jwt_validation_rejects_tampered_token(e2e_seed: E2ESeedBundle) -> None:
    """JWT validation rejects tampered bearer tokens."""

    token = issue_access_token(user_id=e2e_seed.user_id)
    tampered = f"{token[:-4]}dead"
    factory = identity_factory()

    with pytest.raises(InvalidToken):
        await factory.jwt_service.decode_and_verify(tampered)


@pytest.mark.asyncio
async def test_permission_enforcement_blocks_missing_scope(e2e_seed: E2ESeedBundle) -> None:
    """Authorization rejects actors without required permissions."""

    actor = workflow_actor(user_id=e2e_seed.user_id, workspace_id=e2e_seed.workspace_id)
    actor_readonly = ActorContext(
        user_id=e2e_seed.user_id,
        workspace_id=e2e_seed.workspace_id,
        permissions=frozenset({"assets:read"}),
    )

    require_permission(actor, "assets:write")
    with pytest.raises(AuthorizationError):
        require_permission(actor_readonly, "assets:write")


@pytest.mark.asyncio
async def test_authenticated_api_requires_workspace_header(
    auth_client: AsyncClient,
    e2e_seed: E2ESeedBundle,
) -> None:
    """HTTP requests without workspace context are rejected."""

    token = issue_access_token(user_id=e2e_seed.user_id)
    response = await auth_client.get(
        "/api/v1/assets",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_authenticated_list_assets_succeeds(auth_client: AsyncClient) -> None:
    """Authenticated requests with workspace context succeed."""

    response = await auth_client.get("/api/v1/assets")

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
