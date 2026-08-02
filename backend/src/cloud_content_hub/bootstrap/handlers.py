"""Application handler registration for the composition root."""

from __future__ import annotations

from cloud_content_hub.api.dependencies import HandlerRegistry
from cloud_content_hub.bootstrap.container import Container


def wire_handlers(container: Container) -> HandlerRegistry:
    """Construct application handlers from the process container."""

    from cloud_content_hub.application.administration.handlers.get_provider_health_handler import (
        GetProviderHealthHandler,
    )
    from cloud_content_hub.application.administration.handlers.get_queue_status_handler import (
        GetQueueStatusHandler,
    )
    from cloud_content_hub.application.administration.handlers.get_system_status_handler import (
        GetSystemStatusHandler,
    )
    from cloud_content_hub.application.analytics.handlers.get_dashboard_handler import (
        GetDashboardHandler,
    )
    from cloud_content_hub.application.analytics.handlers.get_platform_analytics_handler import (
        GetPlatformAnalyticsHandler,
    )
    from cloud_content_hub.application.analytics.handlers.get_post_analytics_handler import (
        GetPostAnalyticsHandler,
    )
    from cloud_content_hub.application.analytics.handlers.get_top_posts_handler import (
        GetTopPostsHandler,
    )
    from cloud_content_hub.application.assets.handlers.delete_asset_handler import (
        DeleteAssetHandler,
    )
    from cloud_content_hub.application.assets.handlers.get_asset_handler import GetAssetHandler
    from cloud_content_hub.application.assets.handlers.replace_asset_handler import (
        ReplaceAssetHandler,
    )
    from cloud_content_hub.application.assets.handlers.search_assets_handler import (
        ListAssetsHandler,
        SearchAssetsHandler,
    )
    from cloud_content_hub.application.assets.handlers.upload_asset_handler import (
        UploadAssetHandler,
    )
    from cloud_content_hub.application.content.handlers.archive_content_handler import (
        ArchiveContentHandler,
    )
    from cloud_content_hub.application.content.handlers.create_content_version_handler import (
        CreateContentVersionHandler,
    )
    from cloud_content_hub.application.content.handlers.delete_content_handler import (
        DeleteContentHandler,
    )
    from cloud_content_hub.application.content.handlers.duplicate_content_handler import (
        DuplicateContentHandler,
    )
    from cloud_content_hub.application.content.handlers.generate_content_handler import (
        GenerateContentHandler,
    )
    from cloud_content_hub.application.content.handlers.get_content_handler import GetContentHandler
    from cloud_content_hub.application.content.handlers.regenerate_content_handler import (
        RegenerateContentHandler,
    )
    from cloud_content_hub.application.content.handlers.search_content_handler import (
        ListContentHandler,
    )
    from cloud_content_hub.application.notifications.handlers import (
        mark_notification_read_handler,
    )
    from cloud_content_hub.application.notifications.handlers.delete_notification_handler import (
        DeleteNotificationHandler,
    )
    from cloud_content_hub.application.notifications.handlers.get_notifications_handler import (
        GetNotificationsHandler,
    )
    from cloud_content_hub.application.publishing.handlers.cancel_publication_handler import (
        CancelPublicationHandler,
    )
    from cloud_content_hub.application.publishing.handlers.create_publication_handler import (
        CreatePublicationHandler,
    )
    from cloud_content_hub.application.publishing.handlers.dispatch_publication_handler import (
        DispatchPublicationHandler,
    )
    from cloud_content_hub.application.scheduler.handlers.cancel_schedule_handler import (
        CancelScheduleHandler,
    )
    from cloud_content_hub.application.scheduler.handlers.create_schedule_handler import (
        CreateScheduleHandler,
    )
    from cloud_content_hub.application.scheduler.handlers.get_schedule_handler import (
        GetScheduleHandler,
    )

    repositories = container.repositories
    events = container.events.publishers
    services = container.services

    handlers: dict[str, object] = {
        "list_assets": ListAssetsHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            asset_repository_factory=repositories.asset_repository_factory,
        ),
        "search_assets": SearchAssetsHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            asset_repository_factory=repositories.asset_repository_factory,
        ),
        "get_asset": GetAssetHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            asset_repository_factory=repositories.asset_repository_factory,
            storage=container.object_storage_port,
        ),
        "delete_asset": DeleteAssetHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            asset_repository_factory=repositories.asset_repository_factory,
            event_publisher=events.assets,
        ),
        "upload_asset": UploadAssetHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            asset_repository_factory=repositories.asset_repository_factory,
            job_repository_factory=repositories.job_repository_factory,
            event_publisher=events.assets,
            duplicate_detection=services.duplicate_detection_service,
        ),
        "replace_asset": ReplaceAssetHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            asset_repository_factory=repositories.asset_repository_factory,
            job_repository_factory=repositories.job_repository_factory,
            event_publisher=events.assets,
            duplicate_detection=services.duplicate_detection_service,
        ),
        "list_content": ListContentHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            content_repository_factory=repositories.content_repository_factory,
        ),
        "get_content": GetContentHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            content_repository_factory=repositories.content_repository_factory,
        ),
        "create_content_version": CreateContentVersionHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            content_repository_factory=repositories.content_repository_factory,
        ),
        "delete_content": DeleteContentHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            content_repository_factory=repositories.content_repository_factory,
            event_publisher_factory=lambda _uow: events.content,
        ),
        "duplicate_content": DuplicateContentHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            content_repository_factory=repositories.content_repository_factory,
            job_repository_factory=repositories.job_repository_factory,
        ),
        "archive_content": ArchiveContentHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            content_repository_factory=repositories.content_repository_factory,
            event_publisher_factory=lambda _uow: events.content,
        ),
        "generate_content": GenerateContentHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            content_repository_factory=repositories.content_repository_factory,
            generation_repository_factory=repositories.generation_repository_factory,
            job_repository_factory=repositories.job_repository_factory,
            event_publisher_factory=lambda _uow: events.content,
        ),
        "regenerate_content": RegenerateContentHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            content_repository_factory=repositories.content_repository_factory,
            generation_repository_factory=repositories.generation_repository_factory,
            job_repository_factory=repositories.job_repository_factory,
            event_publisher_factory=lambda _uow: events.content,
        ),
        "create_publication": CreatePublicationHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            publication_repository_factory=repositories.publication_repository_factory,
        ),
        "dispatch_publication": DispatchPublicationHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            publication_repository_factory=repositories.publication_repository_factory,
            job_repository_factory=repositories.job_repository_factory,
        ),
        "cancel_publication": CancelPublicationHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            publication_repository_factory=repositories.publication_repository_factory,
        ),
        "create_schedule": CreateScheduleHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            schedule_repository_factory=repositories.schedule_repository_factory,
            schedule_time_resolver=container.schedule_time_resolver,
        ),
        "get_schedule": GetScheduleHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            schedule_repository_factory=repositories.schedule_repository_factory,
        ),
        "cancel_schedule": CancelScheduleHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            schedule_repository_factory=repositories.schedule_repository_factory,
        ),
        "get_analytics_dashboard": GetDashboardHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            analytics_repository_factory=repositories.analytics_repository_factory,
        ),
        "list_analytics_posts": GetTopPostsHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            analytics_repository_factory=repositories.analytics_repository_factory,
        ),
        "list_analytics_platforms": GetPlatformAnalyticsHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            analytics_repository_factory=repositories.analytics_repository_factory,
        ),
        "get_analytics_post": GetPostAnalyticsHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            analytics_repository_factory=repositories.analytics_repository_factory,
        ),
        "list_notifications": GetNotificationsHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            notification_repository_factory=repositories.notification_repository_factory,
        ),
        "mark_notification_read": mark_notification_read_handler.MarkNotificationReadHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            notification_repository_factory=repositories.notification_repository_factory,
            event_publisher=events.notifications,
        ),
        "delete_notification": DeleteNotificationHandler(
            unit_of_work_factory=repositories.unit_of_work_factory,
            notification_repository_factory=repositories.notification_repository_factory,
            event_publisher=events.notifications,
        ),
        "list_admin_queues": GetQueueStatusHandler(queue_status_port=container.queue_status_port),
        "list_admin_providers": GetProviderHealthHandler(
            provider_health_port=container.provider_health_port
        ),
        "get_admin_system_status": GetSystemStatusHandler(
            system_status_port=container.system_status_port
        ),
    }

    return HandlerRegistry(handlers=handlers)
