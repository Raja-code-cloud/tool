"""Worker composition root."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.bootstrap.container import Container
from cloud_content_hub.infrastructure.events.models import EventEnvelope
from cloud_content_hub.workers.base import WorkerHandler, WorkerTaskPayload, WorkerTaskRunner
from cloud_content_hub.workers.config import WorkerRuntimeConfig
from cloud_content_hub.workers.dispatcher import (
    TaskDispatcher,
    WorkerHandlerRegistry,
    handler_adapter,
)
from cloud_content_hub.workers.health import WorkerHealthService
from cloud_content_hub.workers.retry import DeadLetterQueue, WorkerRetryPolicy


@dataclass(frozen=True, slots=True)
class WorkerBundle:
    """Process-scoped worker infrastructure bundle."""

    config: WorkerRuntimeConfig
    registry: WorkerHandlerRegistry
    dispatcher: TaskDispatcher
    runner: WorkerTaskRunner
    health: WorkerHealthService
    container: Container


def create_worker_bundle(container: Container) -> WorkerBundle:
    """Construct worker infrastructure from the process container."""

    config = WorkerRuntimeConfig.with_defaults()
    retry_policy = WorkerRetryPolicy(config.retry)
    dead_letter_queue = DeadLetterQueue(container.redis, config.retry)
    registry = _build_handler_registry(container)
    dispatcher = TaskDispatcher(registry)
    runner = WorkerTaskRunner(
        config=config,
        retry_policy=retry_policy,
        dead_letter_queue=dead_letter_queue,
        dispatch=dispatcher.dispatch,
        metrics=container.observability.metrics,
        tracer=container.observability.tracer,
    )
    health = WorkerHealthService.from_container(container, config)
    return WorkerBundle(
        config=config,
        registry=registry,
        dispatcher=dispatcher,
        runner=runner,
        health=health,
        container=container,
    )


def _build_handler_registry(container: Container) -> WorkerHandlerRegistry:
    repositories = container.repositories
    events = container.events
    services = container.services

    from cloud_content_hub.application.analytics.commands import (
        ArchiveAnalyticsSnapshotCommand,
        ImportAnalyticsCommand,
        RefreshDashboardCacheCommand,
    )
    from cloud_content_hub.application.analytics.dto.requests import (
        ImportAnalyticsRequestDto,
        RefreshDashboardCacheRequestDto,
    )
    from cloud_content_hub.application.analytics.handlers.archive_analytics_snapshot_handler import (  # noqa: E501
        ArchiveAnalyticsSnapshotHandler,
    )
    from cloud_content_hub.application.analytics.handlers.import_analytics_handler import (
        ImportAnalyticsHandler,
    )
    from cloud_content_hub.application.analytics.handlers.refresh_dashboard_cache_handler import (
        RefreshDashboardCacheHandler,
    )
    from cloud_content_hub.application.assets.commands import (
        DeleteAssetCommand,
        ReplaceAssetCommand,
        RestoreAssetCommand,
        UploadAssetCommand,
    )
    from cloud_content_hub.application.assets.dto.requests import (
        ReplaceAssetRequestDto,
        UploadAssetRequestDto,
    )
    from cloud_content_hub.application.assets.handlers.delete_asset_handler import (
        DeleteAssetHandler,
    )
    from cloud_content_hub.application.assets.handlers.replace_asset_handler import (
        ReplaceAssetHandler,
    )
    from cloud_content_hub.application.assets.handlers.restore_asset_handler import (
        RestoreAssetHandler,
    )
    from cloud_content_hub.application.assets.handlers.upload_asset_handler import (
        UploadAssetHandler,
    )
    from cloud_content_hub.application.content.commands import (
        ArchiveContentCommand,
        DuplicateContentCommand,
        GenerateContentCommand,
        RegenerateContentCommand,
    )
    from cloud_content_hub.application.content.dto.requests import (
        DuplicateContentRequestDto,
        GenerationRequestDto,
        RegenerationRequestDto,
    )
    from cloud_content_hub.application.content.handlers.archive_content_handler import (
        ArchiveContentHandler,
    )
    from cloud_content_hub.application.content.handlers.duplicate_content_handler import (
        DuplicateContentHandler,
    )
    from cloud_content_hub.application.content.handlers.generate_content_handler import (
        GenerateContentHandler,
    )
    from cloud_content_hub.application.content.handlers.regenerate_content_handler import (
        RegenerateContentHandler,
    )
    from cloud_content_hub.application.notifications.commands import CreateNotificationCommand
    from cloud_content_hub.application.notifications.dto.requests import NotificationRequestDto
    from cloud_content_hub.application.notifications.handlers.create_notification_handler import (
        CreateNotificationHandler,
    )
    from cloud_content_hub.application.publishing.commands import (
        CancelPublicationCommand,
        DispatchPublicationCommand,
    )
    from cloud_content_hub.application.publishing.dto.requests import (
        DispatchPublicationRequestDto,
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
    from cloud_content_hub.application.scheduler.handlers.get_schedule_handler import (
        GetScheduleHandler,
    )

    upload_asset = UploadAssetHandler(
        unit_of_work_factory=repositories.unit_of_work_factory,
        asset_repository_factory=repositories.asset_repository_factory,
        job_repository_factory=repositories.job_repository_factory,
        event_publisher=events.publishers.assets,
        duplicate_detection=services.duplicate_detection_service,
    )
    replace_asset = ReplaceAssetHandler(
        unit_of_work_factory=repositories.unit_of_work_factory,
        asset_repository_factory=repositories.asset_repository_factory,
        job_repository_factory=repositories.job_repository_factory,
        event_publisher=events.publishers.assets,
        duplicate_detection=services.duplicate_detection_service,
    )
    delete_asset = DeleteAssetHandler(
        unit_of_work_factory=repositories.unit_of_work_factory,
        asset_repository_factory=repositories.asset_repository_factory,
        event_publisher=events.publishers.assets,
    )
    restore_asset = RestoreAssetHandler(
        unit_of_work_factory=repositories.unit_of_work_factory,
        asset_repository_factory=repositories.asset_repository_factory,
        event_publisher=events.publishers.assets,
    )
    generate_content = GenerateContentHandler(
        unit_of_work_factory=repositories.unit_of_work_factory,
        content_repository_factory=repositories.content_repository_factory,
        generation_repository_factory=repositories.generation_repository_factory,
        job_repository_factory=repositories.job_repository_factory,
        event_publisher_factory=lambda _uow: events.publishers.content,
    )
    regenerate_content = RegenerateContentHandler(
        unit_of_work_factory=repositories.unit_of_work_factory,
        content_repository_factory=repositories.content_repository_factory,
        generation_repository_factory=repositories.generation_repository_factory,
        job_repository_factory=repositories.job_repository_factory,
        event_publisher_factory=lambda _uow: events.publishers.content,
    )
    duplicate_content = DuplicateContentHandler(
        unit_of_work_factory=repositories.unit_of_work_factory,
        content_repository_factory=repositories.content_repository_factory,
        job_repository_factory=repositories.job_repository_factory,
    )
    archive_content = ArchiveContentHandler(
        unit_of_work_factory=repositories.unit_of_work_factory,
        content_repository_factory=repositories.content_repository_factory,
        event_publisher_factory=lambda _uow: events.publishers.content,
    )
    create_publication = CreatePublicationHandler(
        unit_of_work_factory=repositories.unit_of_work_factory,
        publication_repository_factory=repositories.publication_repository_factory,
    )
    dispatch_publication = DispatchPublicationHandler(
        unit_of_work_factory=repositories.unit_of_work_factory,
        publication_repository_factory=repositories.publication_repository_factory,
        job_repository_factory=repositories.job_repository_factory,
    )
    cancel_publication = CancelPublicationHandler(
        unit_of_work_factory=repositories.unit_of_work_factory,
        publication_repository_factory=repositories.publication_repository_factory,
    )
    import_analytics = ImportAnalyticsHandler(
        unit_of_work_factory=repositories.unit_of_work_factory,
        analytics_repository_factory=repositories.analytics_repository_factory,
    )
    refresh_dashboard = RefreshDashboardCacheHandler(
        unit_of_work_factory=repositories.unit_of_work_factory,
        analytics_repository_factory=repositories.analytics_repository_factory,
        event_publisher=events.publishers.analytics,
    )
    archive_snapshot = ArchiveAnalyticsSnapshotHandler(
        unit_of_work_factory=repositories.unit_of_work_factory,
        analytics_repository_factory=repositories.analytics_repository_factory,
        event_publisher=events.publishers.analytics,
    )
    create_notification = CreateNotificationHandler(
        unit_of_work_factory=repositories.unit_of_work_factory,
        notification_repository_factory=repositories.notification_repository_factory,
        preference_repository_factory=repositories.notification_preference_repository_factory,
        event_publisher=events.publishers.notifications,
    )
    get_schedule = GetScheduleHandler(
        unit_of_work_factory=repositories.unit_of_work_factory,
        schedule_repository_factory=repositories.schedule_repository_factory,
    )

    audit_service = services.audit_service
    uow_factory = repositories.unit_of_work_factory

    registry = WorkerHandlerRegistry(
        {
            "cloud_content_hub.tasks.upload_asset": handler_adapter(
                upload_asset.handle,
                command_builder=lambda payload: UploadAssetCommand(
                    request=UploadAssetRequestDto.model_validate(payload.command["request"]),
                    idempotency_key=_idempotency_key(payload),
                ),
            ),
            "cloud_content_hub.tasks.replace_asset": handler_adapter(
                replace_asset.handle,
                command_builder=lambda payload: ReplaceAssetCommand(
                    asset_id=_require_uuid(payload, "asset_id"),
                    expected_version=int(payload.command["expected_version"]),
                    request=ReplaceAssetRequestDto.model_validate(payload.command["request"]),
                    idempotency_key=_idempotency_key(payload),
                ),
            ),
            "cloud_content_hub.tasks.delete_asset": handler_adapter(
                delete_asset.handle,
                command_builder=lambda payload: DeleteAssetCommand(
                    asset_id=_require_uuid(payload, "asset_id"),
                    expected_version=int(payload.command["expected_version"]),
                ),
            ),
            "cloud_content_hub.tasks.restore_asset": handler_adapter(
                restore_asset.handle,
                command_builder=lambda payload: RestoreAssetCommand(
                    asset_id=_require_uuid(payload, "asset_id"),
                    expected_version=int(payload.command["expected_version"]),
                ),
            ),
            "cloud_content_hub.tasks.virus_scan": _audit_logged_handler(
                audit_service=audit_service,
                uow_factory=uow_factory,
                action="virus_scan",
                target_type="asset",
            ),
            "cloud_content_hub.tasks.metadata_extraction": _audit_logged_handler(
                audit_service=audit_service,
                uow_factory=uow_factory,
                action="metadata_extraction",
                target_type="asset",
            ),
            "cloud_content_hub.tasks.generate_content": handler_adapter(
                generate_content.handle,
                command_builder=lambda payload: GenerateContentCommand(
                    request=GenerationRequestDto.model_validate(payload.command["request"]),
                    idempotency_key=_idempotency_key(payload),
                ),
            ),
            "cloud_content_hub.tasks.regenerate_content": handler_adapter(
                regenerate_content.handle,
                command_builder=lambda payload: RegenerateContentCommand(
                    request=RegenerationRequestDto.model_validate(payload.command["request"]),
                    idempotency_key=_idempotency_key(payload),
                ),
            ),
            "cloud_content_hub.tasks.duplicate_content": handler_adapter(
                duplicate_content.handle,
                command_builder=lambda payload: DuplicateContentCommand(
                    content_id=_require_uuid(payload, "content_id"),
                    request=DuplicateContentRequestDto.model_validate(payload.command["request"]),
                    idempotency_key=_idempotency_key(payload),
                ),
            ),
            "cloud_content_hub.tasks.archive_content": handler_adapter(
                archive_content.handle,
                command_builder=lambda payload: ArchiveContentCommand(
                    content_id=_require_uuid(payload, "content_id"),
                    expected_version=int(payload.command["expected_version"]),
                ),
            ),
            "cloud_content_hub.tasks.publish_content": _publish_content_handler(
                create_publication=create_publication,
                dispatch_publication=dispatch_publication,
            ),
            "cloud_content_hub.tasks.retry_publish": handler_adapter(
                dispatch_publication.handle,
                command_builder=lambda payload: DispatchPublicationCommand(
                    publication_id=_require_uuid(payload, "publication_id"),
                    expected_version=int(payload.command["expected_version"]),
                    request=DispatchPublicationRequestDto.model_validate(payload.command["request"]),
                    idempotency_key=_idempotency_key(payload),
                ),
            ),
            "cloud_content_hub.tasks.cancel_publish": handler_adapter(
                cancel_publication.handle,
                command_builder=lambda payload: CancelPublicationCommand(
                    publication_id=_require_uuid(payload, "publication_id"),
                    expected_version=int(payload.command["expected_version"]),
                ),
            ),
            "cloud_content_hub.tasks.verify_publish_status": _audit_logged_handler(
                audit_service=audit_service,
                uow_factory=uow_factory,
                action="verify_publish_status",
                target_type="publication",
            ),
            "cloud_content_hub.tasks.import_analytics": handler_adapter(
                import_analytics.handle,
                command_builder=lambda payload: ImportAnalyticsCommand(
                    request=ImportAnalyticsRequestDto.model_validate(payload.command["request"]),
                    idempotency_key=_idempotency_key(payload),
                ),
            ),
            "cloud_content_hub.tasks.refresh_dashboard": handler_adapter(
                refresh_dashboard.handle,
                command_builder=lambda payload: RefreshDashboardCacheCommand(
                    request=RefreshDashboardCacheRequestDto.model_validate(payload.command["request"]),
                ),
            ),
            "cloud_content_hub.tasks.archive_snapshot": handler_adapter(
                archive_snapshot.handle,
                command_builder=lambda payload: ArchiveAnalyticsSnapshotCommand(
                    snapshot_id=_require_uuid(payload, "snapshot_id"),
                ),
            ),
            "cloud_content_hub.tasks.deliver_notification": handler_adapter(
                create_notification.handle,
                command_builder=lambda payload: CreateNotificationCommand(
                    request=NotificationRequestDto.model_validate(payload.command["request"]),
                ),
            ),
            "cloud_content_hub.tasks.retry_notification": _audit_logged_handler(
                audit_service=audit_service,
                uow_factory=uow_factory,
                action="retry_notification",
                target_type="notification",
            ),
            "cloud_content_hub.tasks.cleanup_notifications": _audit_logged_handler(
                audit_service=audit_service,
                uow_factory=uow_factory,
                action="cleanup_notifications",
                target_type="notification",
            ),
            "cloud_content_hub.tasks.cleanup_temp_files": _audit_logged_handler(
                audit_service=audit_service,
                uow_factory=uow_factory,
                action="cleanup_temp_files",
                target_type="maintenance",
            ),
            "cloud_content_hub.tasks.cleanup_expired_tokens": _audit_logged_handler(
                audit_service=audit_service,
                uow_factory=uow_factory,
                action="cleanup_expired_tokens",
                target_type="maintenance",
            ),
            "cloud_content_hub.tasks.cleanup_soft_deletes": _audit_logged_handler(
                audit_service=audit_service,
                uow_factory=uow_factory,
                action="cleanup_soft_deletes",
                target_type="maintenance",
            ),
            "cloud_content_hub.tasks.cleanup_outbox": _cleanup_outbox_handler(container),
            "cloud_content_hub.tasks.cleanup_failed_jobs": _audit_logged_handler(
                audit_service=audit_service,
                uow_factory=uow_factory,
                action="cleanup_failed_jobs",
                target_type="maintenance",
            ),
            "cloud_content_hub.tasks.execute_scheduled_publish": _scheduled_publish_handler(
                get_schedule=get_schedule,
                dispatch_publication=dispatch_publication,
            ),
            "cloud_content_hub.tasks.execute_scheduled_analytics": handler_adapter(
                refresh_dashboard.handle,
                command_builder=lambda payload: RefreshDashboardCacheCommand(
                    request=RefreshDashboardCacheRequestDto.model_validate(payload.command["request"]),
                ),
            ),
            "cloud_content_hub.tasks.execute_scheduled_cleanup": _audit_logged_handler(
                audit_service=audit_service,
                uow_factory=uow_factory,
                action="execute_scheduled_cleanup",
                target_type="maintenance",
            ),
            container.events.config.celery_task_name: _deliver_outbox_handler(container),
        }
    )
    return registry


def _idempotency_key(payload: WorkerTaskPayload) -> str:
    if payload.idempotency_key is not None:
        return payload.idempotency_key
    if payload.job_id is not None:
        return str(payload.job_id)
    return str(payload.resource_id or payload.workspace_id)


def _require_uuid(payload: WorkerTaskPayload, field: str) -> UUID:
    value = payload.command.get(field, payload.resource_id)
    if value is None:
        msg = f"Worker payload is missing required field '{field}'."
        raise ValueError(msg)
    return UUID(str(value))


def _audit_logged_handler(
    *,
    audit_service: Any,
    uow_factory: Callable[[], Any],
    action: str,
    target_type: str,
) -> WorkerHandler:
    async def _handle(actor: ActorContext, payload: WorkerTaskPayload) -> None:
        async with uow_factory() as unit_of_work:
            await audit_service.record_success(
                unit_of_work=unit_of_work,
                actor_user_id=actor.user_id,
                action=action,
                target_type=target_type,
                target_id=payload.resource_id,
                workspace_id=actor.workspace_id,
                source="worker",
                request_id=payload.request_id,
            )
            await unit_of_work.flush()

    return _handle


def _cleanup_outbox_handler(container: Container) -> WorkerHandler:
    async def _handle(_actor: ActorContext, _payload: WorkerTaskPayload) -> int:
        async with container.session_factory() as session:
            try:
                dispatched = await container.events.dispatcher.dispatch_batch(session)
                await session.commit()
                return dispatched
            except BaseException:
                await session.rollback()
                raise

    return _handle


def _deliver_outbox_handler(container: Container) -> WorkerHandler:
    async def _handle(_actor: ActorContext, payload: WorkerTaskPayload) -> None:
        if payload.envelope is None:
            msg = "deliver_outbox_event requires an envelope payload."
            raise ValueError(msg)
        envelope = EventEnvelope.model_validate(payload.envelope)
        async with container.session_factory() as session:
            try:
                await container.events.delivery_service.deliver(session, envelope)
                await session.commit()
            except BaseException:
                await session.rollback()
                raise

    return _handle


def _publish_content_handler(
    *,
    create_publication: Any,
    dispatch_publication: Any,
) -> WorkerHandler:
    from cloud_content_hub.application.publishing.commands import (
        DispatchPublicationCommand,
        PublishContentCommand,
    )
    from cloud_content_hub.application.publishing.dto.requests import (
        CreatePublicationRequestDto,
        DispatchPublicationRequestDto,
    )

    async def _handle(actor: ActorContext, payload: WorkerTaskPayload) -> object | None:
        create_command = PublishContentCommand(
            request=CreatePublicationRequestDto.model_validate(payload.command["create"]),
            idempotency_key=_idempotency_key(payload),
        )
        created = await create_publication.handle(actor, create_command)
        dispatch_command = DispatchPublicationCommand(
            publication_id=created.id,
            expected_version=created.version,
            request=DispatchPublicationRequestDto.model_validate(payload.command["dispatch"]),
            idempotency_key=f"{_idempotency_key(payload)}:dispatch",
        )
        return await dispatch_publication.handle(actor, dispatch_command)

    return _handle


def _scheduled_publish_handler(
    *,
    get_schedule: Any,
    dispatch_publication: Any,
) -> WorkerHandler:
    from cloud_content_hub.application.publishing.commands import DispatchPublicationCommand
    from cloud_content_hub.application.publishing.dto.requests import DispatchPublicationRequestDto
    from cloud_content_hub.application.scheduler.queries import GetScheduleQuery

    async def _handle(actor: ActorContext, payload: WorkerTaskPayload) -> object | None:
        schedule_id = _require_uuid(payload, "schedule_id")
        schedule = await get_schedule.handle(actor, GetScheduleQuery(schedule_id=schedule_id))
        _ = schedule
        dispatch_command = DispatchPublicationCommand(
            publication_id=_require_uuid(payload, "publication_id"),
            expected_version=int(payload.command["publication_version"]),
            request=DispatchPublicationRequestDto.model_validate(payload.command["dispatch"]),
            idempotency_key=_idempotency_key(payload),
        )
        return await dispatch_publication.handle(actor, dispatch_command)

    return _handle
