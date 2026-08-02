"""Shared fixtures for smoke tests."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import httpx
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from cloud_content_hub.api.dependencies import HandlerRegistry
from cloud_content_hub.api.errors import install_exception_handlers
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
from cloud_content_hub.infrastructure.identity.testing.fixtures import identity_factory
from helpers.import_utils import load_module_from_file, try_import_root_router

pytestmark = pytest.mark.smoke

WORKSPACE_ID = UUID("01900000-0000-7000-8000-000000000001")
USER_ID = UUID("01900000-0000-7000-8000-000000000010")

_health_module = load_module_from_file("smoke_health_router", "api/routers/v1/health.py")
health_router = _health_module.router
_router_module = try_import_root_router()


def smoke_base_url() -> str | None:
    return os.getenv("SMOKE_BASE_URL")


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
        title="Smoke Asset",
        summary=None,
        lifecycle_status=AssetLifecycleStatusDto.ACTIVE,
        owner_id=USER_ID,
        is_favorite=False,
    )


@pytest.fixture
def access_token() -> str:
    factory = identity_factory()
    return factory.jwt_service.create_access_token(
        str(USER_ID),
        provider="mock",
        roles=frozenset({"admin"}),
        permissions=frozenset({"*"}),
    )


@pytest.fixture
def mock_handlers() -> dict[str, Any]:
    asset = _asset_dto()
    now = datetime.now(tz=UTC)
    operation = OperationDto(
        id=uuid4(),
        version=1,
        created_at=now,
        updated_at=now,
        type=OperationType.UPLOAD,
        status=OperationStatus.QUEUED,
        resource_type="asset",
        resource_id=asset.id,
    )

    handlers: dict[str, Any] = {
        "upload_asset": AsyncMock(handle=AsyncMock(return_value=operation)),
        "list_assets": AsyncMock(
            handle=AsyncMock(
                return_value=PagedResultDto(
                    items=(asset,),
                    page=PageInfoDto(next_cursor=None, has_more=False, limit=25),
                )
            )
        ),
        "get_asset": AsyncMock(handle=AsyncMock(return_value=asset)),
        "delete_asset": AsyncMock(handle=AsyncMock(return_value=None)),
        "list_content": AsyncMock(
            handle=AsyncMock(
                return_value=PagedResultDto(
                    items=(),
                    page=PageInfoDto(next_cursor=None, has_more=False, limit=25),
                )
            )
        ),
        "generate_content": AsyncMock(handle=AsyncMock(return_value=operation)),
        "list_publication_history": AsyncMock(
            handle=AsyncMock(
                return_value=PagedResultDto(
                    items=(),
                    page=PageInfoDto(next_cursor=None, has_more=False, limit=25),
                )
            )
        ),
        "list_schedules": AsyncMock(
            handle=AsyncMock(
                return_value=PagedResultDto(
                    items=(),
                    page=PageInfoDto(next_cursor=None, has_more=False, limit=25),
                )
            )
        ),
        "get_analytics_dashboard": AsyncMock(handle=AsyncMock(return_value={"widgets": []})),
        "list_notifications": AsyncMock(
            handle=AsyncMock(
                return_value=PagedResultDto(
                    items=(),
                    page=PageInfoDto(next_cursor=None, has_more=False, limit=25),
                )
            )
        ),
        "get_admin_system_status": AsyncMock(handle=AsyncMock(return_value={"status": "healthy"})),
    }
    return handlers


@pytest.fixture
async def health_client() -> AsyncIterator[AsyncClient]:
    app = FastAPI(title="smoke-health")
    container = MagicMock()
    container.settings.service_version = "smoke"
    container.settings.database_timeout_seconds = 1.0
    container.settings.redis_timeout_seconds = 1.0
    connection = AsyncMock()
    connection.execute = AsyncMock()
    connect_cm = AsyncMock()
    connect_cm.__aenter__.return_value = connection
    connect_cm.__aexit__.return_value = None
    container.database_engine.connect.return_value = connect_cm
    container.redis.ping = AsyncMock()
    app.state.container = container
    install_exception_handlers(app)
    app.include_router(health_router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def local_client(mock_handlers: dict[str, Any]) -> AsyncIterator[AsyncClient]:
    if _router_module is None:
        pytest.skip("Application routers are unavailable in this environment.")
    app = FastAPI(title="smoke-test")
    container = MagicMock()
    container.settings.service_version = "smoke"
    app.state.container = container
    app.state.handlers = HandlerRegistry(handlers=mock_handlers)
    install_exception_handlers(app)
    app.include_router(_router_module.root_router)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def external_client() -> AsyncIterator[AsyncClient]:
    base_url = smoke_base_url()
    if base_url is None:
        pytest.skip("SMOKE_BASE_URL is not configured.")
    async with AsyncClient(base_url=base_url, timeout=httpx.Timeout(30.0)) as client:
        yield client


@pytest.fixture
def bind_admin() -> AsyncIterator[None]:
    token = bind_principal(_principal(permissions=frozenset({"*"})))
    try:
        yield
    finally:
        clear_principal(token)
