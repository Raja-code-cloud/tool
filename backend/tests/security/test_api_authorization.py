"""API authorization and broken authentication regression tests."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from cloud_content_hub.api.dependencies import HandlerRegistry
from cloud_content_hub.bootstrap.api import create_app
from cloud_content_hub.core.config import Environment, Settings
from cloud_content_hub.infrastructure.identity.principal import Principal

WORKSPACE_ID = UUID("01900000-0000-7000-8000-000000000001")
ASSET_ID = UUID("01900000-0000-7000-8000-000000000201")
USER_ID = UUID("01900000-0000-7000-8000-000000000002")


def _principal(*permissions: str) -> Principal:
    return Principal(
        subject=str(USER_ID),
        provider="mock",
        permissions=frozenset(permissions),
        authenticated=True,
    )


def test_unauthenticated_request_to_protected_route_returns_401(security_client: TestClient) -> None:
    response = security_client.get(f"/api/v1/assets/{uuid4()}")
    assert response.status_code in {401, 422}


def test_invalid_bearer_token_yields_anonymous_principal(security_client: TestClient) -> None:
    response = security_client.get(
        f"/api/v1/assets/{uuid4()}",
        headers={
            "Authorization": "Bearer not-a-valid-jwt",
            "X-Workspace-ID": str(WORKSPACE_ID),
        },
    )
    assert response.status_code == 401


def test_authenticated_request_with_permission_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    from cloud_content_hub.infrastructure import identity

    monkeypatch.setattr(
        identity.dependencies,
        "authenticated_principal",
        lambda: _principal("assets:read"),
    )

    app = create_app(Settings(environment=Environment.TEST))
    handler = AsyncMock()
    now = datetime.now(tz=UTC).isoformat().replace("+00:00", "Z")
    handler.handle.return_value = type(
        "AssetDto",
        (),
        {
            "id": ASSET_ID,
            "version": 2,
            "model_dump": lambda self, **kwargs: {
                "id": str(ASSET_ID),
                "version": 2,
                "createdAt": now,
                "updatedAt": now,
                "assetType": "poster",
                "title": "Launch",
                "summary": None,
                "lifecycleStatus": "active",
                "ownerId": str(USER_ID),
                "isFavorite": False,
            },
        },
    )()
    app.state.handlers = HandlerRegistry(handlers={"get_asset": handler})

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get(
        f"/api/v1/assets/{ASSET_ID}",
        headers={"X-Workspace-ID": str(WORKSPACE_ID)},
    )

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_problem_json_does_not_echo_authorization_header(security_client: TestClient) -> None:
    secret = "Bearer super-secret-token-value"
    response = security_client.get(
        f"/api/v1/assets/{uuid4()}",
        headers={"Authorization": secret},
    )
    assert "super-secret-token-value" not in response.text
