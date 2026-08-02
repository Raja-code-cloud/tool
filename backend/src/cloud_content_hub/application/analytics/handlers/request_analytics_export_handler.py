"""Request analytics export command handler."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from cloud_content_hub.application.analytics.commands import RequestAnalyticsExportCommand
from cloud_content_hub.application.analytics.dto.responses import AnalyticsExportResponse
from cloud_content_hub.application.analytics.events import AnalyticsExportRequested
from cloud_content_hub.application.analytics.interfaces.analytics_repository import (
    IAnalyticsRepository,
)
from cloud_content_hub.application.analytics.interfaces.event_publisher import (
    IAnalyticsEventPublisher,
)
from cloud_content_hub.application.analytics.mappers.analytics_mapper import AnalyticsMapper
from cloud_content_hub.application.analytics.services.export_orchestration_service import (
    ExportOrchestrationService,
)
from cloud_content_hub.application.analytics.validators.analytics_validator import (
    validate_platform_selection,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class RequestAnalyticsExportHandler:
    """Orchestrates asynchronous analytics export requests."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        analytics_repository_factory: Callable[[IUnitOfWork], IAnalyticsRepository],
        event_publisher: IAnalyticsEventPublisher,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._analytics_repository_factory = analytics_repository_factory
        self._event_publisher = event_publisher

    async def handle(
        self,
        actor: ActorContext,
        command: RequestAnalyticsExportCommand,
    ) -> AnalyticsExportResponse:
        require_permission(actor, "analytics:read")
        platform_ids = frozenset(command.request.platform_ids)

        async with self._unit_of_work_factory() as unit_of_work:
            analytics_repository = self._analytics_repository_factory(unit_of_work)
            if platform_ids:
                platforms_valid = await analytics_repository.validate_platform_ids(
                    workspace_id=actor.workspace_id,
                    platform_ids=platform_ids,
                )
                validate_platform_selection(
                    platform_ids=platform_ids,
                    platforms_valid=platforms_valid,
                )
            export_service = ExportOrchestrationService(analytics_repository=analytics_repository)
            export_input = await export_service.create_export(
                workspace_id=actor.workspace_id,
                request=command.request,
                requested_by=actor.user_id,
            )
            export_record = await analytics_repository.request_export(export_input)
            await self._event_publisher.publish(
                AnalyticsExportRequested(
                    workspace_id=actor.workspace_id,
                    export_id=export_record.id,
                    export_type=export_record.export_type,
                    actor_id=actor.user_id,
                    period_start=export_record.period_start,
                    period_end=export_record.period_end,
                    occurred_at=datetime.now(tz=UTC),
                ),
                unit_of_work=unit_of_work,
            )
            await unit_of_work.flush()

        return AnalyticsMapper.to_export_dto(export_record)
