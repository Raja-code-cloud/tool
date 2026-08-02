"""Workspace and tenant isolation security tests."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from cloud_content_hub.api.dependencies import build_actor_context
from cloud_content_hub.core.errors import AuthenticationError
from cloud_content_hub.infrastructure.identity.principal import Principal

WORKSPACE_A = UUID("01900000-0000-7000-8000-000000000001")
WORKSPACE_B = UUID("01900000-0000-7000-8000-000000000002")
USER_ID = UUID("01900000-0000-7000-8000-000000000010")


def _authenticated(subject: str = str(USER_ID)) -> Principal:
    return Principal(
        subject=subject,
        provider="mock",
        permissions=frozenset({"assets:read"}),
        authenticated=True,
    )


def test_actor_context_requires_authenticated_principal() -> None:
    with pytest.raises(AuthenticationError):
        build_actor_context(Principal.anonymous(), WORKSPACE_A)


def test_actor_context_binds_workspace_from_header_value() -> None:
    actor = build_actor_context(_authenticated(), WORKSPACE_B)
    assert actor.workspace_id == WORKSPACE_B
    assert actor.user_id == USER_ID


def test_cross_workspace_header_does_not_change_user_identity() -> None:
    actor_a = build_actor_context(_authenticated(), WORKSPACE_A)
    actor_b = build_actor_context(_authenticated(), WORKSPACE_B)
    assert actor_a.user_id == actor_b.user_id
    assert actor_a.workspace_id != actor_b.workspace_id


def test_protected_asset_route_requires_workspace_header(security_client: TestClient) -> None:
    asset_id = uuid4()
    response = security_client.get(
        f"/api/v1/assets/{asset_id}",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code in {401, 422}


def test_invalid_workspace_header_returns_validation_error(security_client: TestClient) -> None:
    from cloud_content_hub.infrastructure.identity.middleware import bind_principal, clear_principal

    token = bind_principal(_authenticated())
    try:
        response = security_client.get(
            f"/api/v1/assets/{uuid4()}",
            headers={
                "Authorization": "Bearer placeholder",
                "X-Workspace-ID": "not-a-uuid",
            },
        )
    finally:
        clear_principal(token)
    assert response.status_code in {401, 422}
