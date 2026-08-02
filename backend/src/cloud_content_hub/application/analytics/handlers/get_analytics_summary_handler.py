"""Get analytics summary query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.analytics.dto.responses import AnalyticsSummaryResponse
from cloud_content_hub.application.analytics.interfaces.analytics_repository import (
    IAnalyticsRepository,
)
from cloud_content_hub.application.analytics.mappers.analytics_mapper import AnalyticsMapper
from cloud_content_hub.application.analytics.queries import GetAnalyticsSummaryQuery
from cloud_content_hub.application.analytics.validators.analytics_validator import (
    validate_dashboard_period,
    validate_platform_selection,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class GetAnalyticsSummaryHandler:
    """Retrieves a high-level analytics summary."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        analytics_repository_factory: Callable[[IUnitOfWork], IAnalyticsRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._analytics_repository_factory = analytics_repository_factory

    async def handle(
        self,
        actor: ActorContext,
        query: GetAnalyticsSummaryQuery,
    ) -> AnalyticsSummaryResponse:
        require_permission(actor, "analytics:read")
        validate_dashboard_period(period_start=query.period_start, period_end=query.period_end)

        async with self._unit_of_work_factory() as unit_of_work:
            analytics_repository = self._analytics_repository_factory(unit_of_work)
            if query.platform_ids:
                platforms_valid = await analytics_repository.validate_platform_ids(
                    workspace_id=actor.workspace_id,
                    platform_ids=query.platform_ids,
                )
                validate_platform_selection(
                    platform_ids=query.platform_ids,
                    platforms_valid=platforms_valid,
                )
            record = await analytics_repository.get_summary(
                workspace_id=actor.workspace_id,
                period_start=query.period_start,
                period_end=query.period_end,
                platform_ids=query.platform_ids,
            )

        return AnalyticsMapper.to_summary_dto(record)
