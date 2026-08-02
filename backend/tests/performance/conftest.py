"""Shared fixtures for performance validation tests."""

from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient

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
from cloud_content_hub.infrastructure.events.config import EventPublishingConfig
from cloud_content_hub.infrastructure.events.testing.fakes import FakeCeleryBroker
from cloud_content_hub.infrastructure.identity.middleware import bind_principal, clear_principal
from cloud_content_hub.infrastructure.storage.testing.fake import InMemoryStorageProvider
from tests.performance.helpers.http import (
    DEFAULT_USER_ID,
    DEFAULT_WORKSPACE_ID,
    auth_headers,
    build_principal,
    create_async_client,
    noop_handler,
)

pytestmark = pytest.mark.performance


@pytest.fixture
def workspace_id() -> Any:
    return DEFAULT_WORKSPACE_ID


@pytest.fixture
def user_id() -> Any:
    return DEFAULT_USER_ID


@pytest.fixture
def perf_headers() -> dict[str, str]:
    return auth_headers()


@pytest.fixture
def asset_dto() -> AssetDto:
    now = datetime.now(tz=UTC)
    return AssetDto(
        id=uuid4(),
        version=1,
        created_at=now,
        updated_at=now,
        asset_type=AssetTypeDto.POSTER,
        title="Performance Asset",
        summary=None,
        lifecycle_status=AssetLifecycleStatusDto.ACTIVE,
        owner_id=DEFAULT_USER_ID,
        is_favorite=False,
    )


@pytest.fixture
def operation_dto(asset_dto: AssetDto) -> OperationDto:
    now = datetime.now(tz=UTC)
    return OperationDto(
        id=uuid4(),
        version=1,
        created_at=now,
        updated_at=now,
        type=OperationType.UPLOAD,
        status=OperationStatus.QUEUED,
        resource_type="asset",
        resource_id=asset_dto.id,
    )


@pytest.fixture
def mock_handlers(asset_dto: AssetDto, operation_dto: OperationDto) -> dict[str, Any]:
    paged = PagedResultDto(
        items=(asset_dto,),
        page=PageInfoDto(next_cursor=None, has_more=False, limit=25),
    )
    return {
        "list_assets": noop_handler(paged),
        "get_asset": noop_handler(asset_dto),
        "search_assets": noop_handler(paged),
        "upload_asset": noop_handler(operation_dto),
        "delete_asset": noop_handler(None),
        "list_content": noop_handler(paged),
        "get_content": noop_handler(asset_dto),
        "generate_content": noop_handler(operation_dto),
        "list_publications": noop_handler(paged),
        "create_publication": noop_handler(operation_dto),
        "list_schedules": noop_handler(paged),
        "get_analytics_dashboard": noop_handler({"widgets": []}),
        "list_notifications": noop_handler(paged),
        "list_admin_jobs": noop_handler(paged),
        "list_admin_queues": noop_handler([]),
        "get_admin_system_status": noop_handler({"status": "healthy"}),
    }


@pytest.fixture
async def perf_client(mock_handlers: dict[str, Any]) -> AsyncIterator[AsyncClient]:
    async for client in create_async_client(handlers=mock_handlers):
        yield client


@pytest.fixture
def principal_token() -> Any:
    token = bind_principal(
        build_principal(
            permissions=frozenset(
                {
                    "assets:read",
                    "assets:write",
                    "assets:delete",
                    "content:read",
                    "content:generate",
                    "content:write",
                    "publishing:read",
                    "publishing:write",
                    "analytics:read",
                    "notifications:read",
                    "admin:read",
                }
            )
        )
    )
    yield token
    clear_principal(token)


@pytest.fixture
def storage_provider() -> InMemoryStorageProvider:
    return InMemoryStorageProvider()


@pytest.fixture
def celery_broker() -> FakeCeleryBroker:
    return FakeCeleryBroker()


@pytest.fixture
def event_config() -> EventPublishingConfig:
    return EventPublishingConfig(batch_size=100, max_attempts=3, poison_message_threshold=2)
