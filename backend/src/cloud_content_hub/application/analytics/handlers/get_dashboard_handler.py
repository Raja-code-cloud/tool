"""Get analytics dashboard query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.analytics.dto.responses import DashboardResponse
from cloud_content_hub.application.analytics.interfaces.analytics_repository import (
    IAnalyticsRepository,
)
from cloud_content_hub.application.analytics.mappers.analytics_mapper import AnalyticsMapper
from cloud_content_hub.application.analytics.queries import GetDashboardQuery
from cloud_content_hub.application.analytics.validators.analytics_validator import (
    validate_dashboard_period,
    validate_metric_codes,
    validate_platform_selection,
    validate_time_zone,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class GetDashboardHandler:
    """Retrieves the workspace analytics dashboard."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        analytics_repository_factory: Callable[[IUnitOfWork], IAnalyticsRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._analytics_repository_factory = analytics_repository_factory

    async def handle(self, actor: ActorContext, query: GetDashboardQuery) -> DashboardResponse:
        require_permission(actor, "analytics:read")
        validate_dashboard_period(period_start=query.period_start, period_end=query.period_end)
        validate_time_zone(query.time_zone)
        validate_metric_codes(query.metric_codes)

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
            dashboard = await analytics_repository.get_dashboard(
                workspace_id=actor.workspace_id,
                period_start=query.period_start,
                period_end=query.period_end,
                time_zone=query.time_zone,
                metric_codes=query.metric_codes,
                platform_ids=query.platform_ids,
            )

        return AnalyticsMapper.to_dashboard_dto(dashboard)
