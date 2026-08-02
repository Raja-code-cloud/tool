"""Endpoint tests for the HTTP delivery layer."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from cloud_content_hub.api.dependencies import HandlerRegistry, build_actor_context
from cloud_content_hub.bootstrap.api import create_app
from cloud_content_hub.core.config import Environment, Settings
from cloud_content_hub.infrastructure.identity.principal import Principal

WORKSPACE_ID = UUID("01900000-0000-7000-8000-000000000001")
USER_ID = UUID("01900000-0000-7000-8000-000000000002")
ASSET_ID = UUID("01900000-0000-7000-8000-000000000201")


def _principal(*permissions: str) -> Principal:
    return Principal(
        subject=str(USER_ID),
        provider="mock",
        permissions=frozenset(permissions),
        authenticated=True,
    )


def _asset_payload() -> dict[str, object]:
    now = datetime.now(tz=UTC).isoformat().replace("+00:00", "Z")
    return {
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
    }


class _AssetDto:
    def __init__(self) -> None:
        self.id = ASSET_ID
        self.version = 2

    def model_dump(self, **kwargs: object) -> dict[str, object]:
        return _asset_payload()


class _PagedAssets:
    def __init__(self) -> None:
        self.items = (_AssetDto(),)
        self.page = type(
            "Page",
            (),
            {"next_cursor": None, "has_more": False, "limit": 25},
        )()


class _OperationDto:
    def __init__(self) -> None:
        self.id = uuid4()
        self.resource_id = ASSET_ID
        self.type = "upload"
        self.status = "queued"

    def model_dump(self, **kwargs: object) -> dict[str, object]:
        now = datetime.now(tz=UTC).isoformat().replace("+00:00", "Z")
        return {
            "id": str(self.id),
            "version": 1,
            "createdAt": now,
            "updatedAt": now,
            "type": self.type,
            "status": self.status,
            "resourceType": "asset",
            "resourceId": str(self.resource_id),
        }


@pytest.fixture
def client() -> TestClient:
    app = create_app(Settings(environment=Environment.TEST))
    app.state.handlers = HandlerRegistry(handlers={})
    return TestClient(app, raise_server_exceptions=False)


def test_health_envelope(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"
    assert "requestId" in body["meta"]


def test_liveness_probe(client: TestClient) -> None:
    response = client.get("/live")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "live"


def test_get_asset_requires_workspace(client: TestClient) -> None:
    response = client.get(
        f"/api/v1/assets/{ASSET_ID}",
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 401


def test_get_asset_success_with_mocked_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    from cloud_content_hub.infrastructure import identity

    monkeypatch.setattr(
        identity.dependencies,
        "authenticated_principal",
        lambda: _principal("assets:read"),
    )

    app = create_app(Settings(environment=Environment.TEST))
    handler = AsyncMock()
    dto = _AssetDto()
    handler.handle.return_value = dto
    app.state.handlers = HandlerRegistry(handlers={"get_asset": handler})

    with TestClient(app) as test_client:
        response = test_client.get(
            f"/api/v1/assets/{ASSET_ID}",
            headers={"X-Workspace-ID": str(WORKSPACE_ID)},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["id"] == str(ASSET_ID)
    assert response.headers["ETag"] == '"2"'
    handler.handle.assert_awaited_once()
    actor_arg, query_arg = handler.handle.await_args.args
    assert actor_arg.workspace_id == WORKSPACE_ID
    assert query_arg.asset_id == ASSET_ID


def test_list_assets_paged_envelope(monkeypatch: pytest.MonkeyPatch) -> None:
    from cloud_content_hub.infrastructure import identity

    monkeypatch.setattr(
        identity.dependencies,
        "authenticated_principal",
        lambda: _principal("assets:read"),
    )

    app = create_app(Settings(environment=Environment.TEST))
    handler = AsyncMock()
    handler.handle.return_value = _PagedAssets()
    app.state.handlers = HandlerRegistry(handlers={"list_assets": handler})

    with TestClient(app) as test_client:
        response = test_client.get(
            "/api/v1/assets",
            headers={"X-Workspace-ID": str(WORKSPACE_ID)},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["meta"]["page"]["limit"] == 25
    assert body["meta"]["page"]["hasMore"] is False
    assert len(body["data"]) == 1


def test_upload_asset_returns_202(monkeypatch: pytest.MonkeyPatch) -> None:
    from cloud_content_hub.infrastructure import identity

    monkeypatch.setattr(
        identity.dependencies,
        "authenticated_principal",
        lambda: _principal("assets:write"),
    )

    app = create_app(Settings(environment=Environment.TEST))
    handler = AsyncMock()
    handler.handle.return_value = _OperationDto()
    app.state.handlers = HandlerRegistry(handlers={"upload_asset": handler})

    with TestClient(app) as test_client:
        response = test_client.post(
            "/api/v1/assets/upload",
            headers={
                "X-Workspace-ID": str(WORKSPACE_ID),
                "Idempotency-Key": "upload-key-0123",
            },
            data={"assetType": "poster", "title": "Launch"},
            files={"file": ("launch.webp", b"fake-image", "image/webp")},
        )

    assert response.status_code == 202
    body = response.json()
    assert body["success"] is True
    assert body["data"]["type"] == "upload"
    assert "Location" in response.headers


def test_problem_details_v1_envelope(monkeypatch: pytest.MonkeyPatch) -> None:
    from cloud_content_hub.core.errors import ResourceNotFoundError
    from cloud_content_hub.infrastructure import identity

    monkeypatch.setattr(
        identity.dependencies,
        "authenticated_principal",
        lambda: _principal("assets:read"),
    )

    app = create_app(Settings(environment=Environment.TEST))
    handler = AsyncMock()
    handler.handle.side_effect = ResourceNotFoundError()
    app.state.handlers = HandlerRegistry(handlers={"get_asset": handler})

    with TestClient(app) as test_client:
        response = test_client.get(
            f"/api/v1/assets/{ASSET_ID}",
            headers={"X-Workspace-ID": str(WORKSPACE_ID)},
        )

    assert response.status_code == 404
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "resource_not_found"
    assert response.headers["content-type"].startswith("application/problem+json")
