"""Mock handler registry for deterministic API and regression tests."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

from tests.fixtures.factories import (
    asset_dto,
    content_dto,
    dashboard_dto,
    empty_page,
    job_dto,
    notification_dto,
    operation_dto,
    platform_analytics_dto,
    post_analytics_dto,
    provider_health_dto,
    publication_dto,
    publication_history_item_dto,
    queue_status_dto,
    schedule_dto,
    single_page,
    system_status_dto,
)


def _mock_handler(return_value: object) -> AsyncMock:
    handler = AsyncMock()
    handler.handle = AsyncMock(return_value=return_value)
    return handler


def build_mock_handlers(*, asset_count: int = 1) -> dict[str, Any]:
    """Return a complete handler map covering all registered API routes."""

    asset = asset_dto()
    content = content_dto(asset_id=asset.id)
    publication = publication_dto(asset_id=asset.id, content_version_id=content.content_version_id)
    schedule = schedule_dto(publication_target_id=publication.targets[0].id)
    notification = notification_dto()
    from cloud_content_hub.application.shared.dto.base import OperationType

    upload_operation = operation_dto(resource_id=asset.id)
    generation_operation = operation_dto(
        operation_type=OperationType.GENERATION,
        resource_id=content.id,
    )
    publish_operation = operation_dto(
        operation_type=OperationType.PUBLISHING,
        resource_id=publication.id,
    )

    assets = tuple(asset_dto(title=f"Asset {index}") for index in range(asset_count))

    post_page = single_page(post_analytics_dto(content_id=content.id))
    return {
        "upload_asset": _mock_handler(upload_operation),
        "replace_asset": _mock_handler(upload_operation),
        "list_assets": _mock_handler(single_page(assets[0]) if assets else empty_page()),
        "search_assets": _mock_handler(single_page(assets[0]) if assets else empty_page()),
        "get_asset": _mock_handler(asset),
        "delete_asset": _mock_handler(None),
        "list_content": _mock_handler(single_page(content)),
        "get_content": _mock_handler(content),
        "create_content_version": _mock_handler(content),
        "delete_content": _mock_handler(None),
        "duplicate_content": _mock_handler(content),
        "archive_content": _mock_handler(content),
        "generate_content": _mock_handler(generation_operation),
        "regenerate_content": _mock_handler(generation_operation),
        "create_publication": _mock_handler(publication),
        "dispatch_publication": _mock_handler(publish_operation),
        "cancel_publication": _mock_handler(publication),
        "list_publication_history": _mock_handler(single_page(publication_history_item_dto())),
        "create_schedule": _mock_handler(schedule),
        "list_schedules": _mock_handler(single_page(schedule)),
        "get_schedule": _mock_handler(schedule),
        "update_schedule": _mock_handler(schedule),
        "cancel_schedule": _mock_handler(schedule),
        "get_analytics_dashboard": _mock_handler(dashboard_dto()),
        "list_analytics_posts": _mock_handler(post_page),
        "list_analytics_platforms": _mock_handler(single_page(platform_analytics_dto())),
        "get_analytics_post": _mock_handler(post_analytics_dto(content_id=content.id)),
        "list_notifications": _mock_handler(single_page(notification)),
        "mark_notification_read": _mock_handler(notification),
        "delete_notification": _mock_handler(None),
        "list_admin_jobs": _mock_handler(single_page(job_dto())),
        "list_admin_queues": _mock_handler((queue_status_dto(),)),
        "list_admin_providers": _mock_handler((provider_health_dto(),)),
        "get_admin_system_status": _mock_handler(system_status_dto()),
    }
