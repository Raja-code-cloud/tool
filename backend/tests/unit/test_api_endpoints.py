"""Endpoint tests for the HTTP delivery layer."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from cloud_content_hub.api.dependencies import HandlerRegistry
from cloud_content_hub.api.errors import install_exception_handlers
from cloud_content_hub.api.routers.v1.router import root_router
from cloud_content_hub.application.assets.dto.responses import (
    AssetDto,
    AssetLifecycleStatusDto,
    AssetTypeDto,
)
from cloud_content_hub.application.shared.dto.base import (
    OperationDto,
    OperationStatus,
    OperationType,
    PagedResultDto,
    PageInfoDto,
)
from cloud_content_hub.infrastructure.identity.middleware import bind_principal, clear_principal
from cloud_content_hub.infrastructure.identity.principal import Principal

WORKSPACE_ID = UUID("01900000-0000-7000-8000-000000000001")
USER_ID = UUID("01900000-0000-7000-8000-000000000010")


def _principal(*, permissions: frozenset[str]) -> Principal:
    return Principal(
        subject=str(USER_ID),
        provider="mock",
        authenticated=True,
        permissions=permissions,
    )


def _asset_dto() -> AssetDto:
    now = datetime.now(tz=UTC)
    return AssetDto(
        id=uuid4(),
        version=1,
        created_at=now,
        updated_at=now,
        asset_type=AssetTypeDto.POSTER,
        title="Launch",
        summary=None,
        lifecycle_status=AssetLifecycleStatusDto.ACTIVE,
        owner_id=USER_ID,
        is_favorite=False,
    )


@pytest.fixture
def mock_handlers() -> dict[str, Any]:
    asset = _asset_dto()
    operation = OperationDto(
        id=uuid4(),
        version=1,
        created_at=datetime.now(tz=UTC),
        updated_at=datetime.now(tz=UTC),
        type=OperationType.UPLOAD,
        status=OperationStatus.QUEUED,
        resource_type="asset",
        resource_id=asset.id,
    )

    upload_handler = AsyncMock()
    upload_handler.handle.return_value = operation

    list_handler = AsyncMock()
    list_handler.handle.return_value = PagedResultDto(
        items=(asset,),
        page=PageInfoDto(next_cursor=None, has_more=False, limit=25),
    )

    get_handler = AsyncMock()
    get_handler.handle.return_value = asset

    delete_handler = AsyncMock()
    delete_handler.handle.return_value = None

    return {
        "upload_asset": upload_handler,
        "list_assets": list_handler,
        "get_asset": get_handler,
        "delete_asset": delete_handler,
    }


@pytest.fixture
async def client(mock_handlers: dict[str, Any]) -> AsyncClient:
    app = FastAPI(title="test")
    container = MagicMock()
    container.settings.service_version = "1.0.0"
    app.state.container = container
    app.state.handlers = HandlerRegistry(handlers=mock_handlers)
    install_exception_handlers(app)
    app.include_router(root_router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client


@pytest.mark.asyncio
async def test_list_assets_returns_envelope(
    client: AsyncClient,
    mock_handlers: dict[str, Any],
) -> None:
    principal_token = bind_principal(_principal(permissions=frozenset({"assets:read"})))
    try:
        response = await client.get(
            "/api/v1/assets",
            headers={
                "Authorization": "Bearer test-token",
                "X-Workspace-ID": str(WORKSPACE_ID),
            },
        )
    finally:
        clear_principal(principal_token)

    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["message"] == "Assets retrieved."
    assert len(body["data"]) == 1
    assert body["meta"]["page"]["limit"] == 25
    mock_handlers["list_assets"].handle.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_asset_returns_etag(client: AsyncClient) -> None:
    principal_token = bind_principal(_principal(permissions=frozenset({"assets:read"})))
    asset_id = uuid4()
    try:
        response = await client.get(
            f"/api/v1/assets/{asset_id}",
            headers={
                "Authorization": "Bearer test-token",
                "X-Workspace-ID": str(WORKSPACE_ID),
            },
        )
    finally:
        clear_principal(principal_token)

    assert response.status_code == 200
    assert response.headers["etag"] == '"1"'


@pytest.mark.asyncio
async def test_delete_asset_requires_if_match(client: AsyncClient) -> None:
    principal_token = bind_principal(_principal(permissions=frozenset({"assets:delete"})))
    try:
        response = await client.delete(
            f"/api/v1/assets/{uuid4()}",
            headers={
                "Authorization": "Bearer test-token",
                "X-Workspace-ID": str(WORKSPACE_ID),
            },
        )
    finally:
        clear_principal(principal_token)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_health_is_public(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_problem_response_on_missing_workspace(client: AsyncClient) -> None:
    principal_token = bind_principal(_principal(permissions=frozenset({"assets:read"})))
    try:
        response = await client.get(
            "/api/v1/assets",
            headers={"Authorization": "Bearer test-token"},
        )
    finally:
        clear_principal(principal_token)

    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "validation_failed"
