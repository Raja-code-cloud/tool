"""Get post analytics query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.analytics.dto.responses import PostAnalyticsResponse
from cloud_content_hub.application.analytics.exceptions.analytics_errors import (
    AnalyticsNotFoundError,
)
from cloud_content_hub.application.analytics.interfaces.analytics_repository import (
    IAnalyticsRepository,
)
from cloud_content_hub.application.analytics.mappers.analytics_mapper import AnalyticsMapper
from cloud_content_hub.application.analytics.queries import GetPostAnalyticsQuery
from cloud_content_hub.application.analytics.validators.analytics_validator import (
    validate_dashboard_period,
    validate_metric_codes,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class GetPostAnalyticsHandler:
    """Retrieves performance analytics for a single post."""

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
        query: GetPostAnalyticsQuery,
    ) -> PostAnalyticsResponse:
        require_permission(actor, "analytics:read")
        validate_dashboard_period(period_start=query.period_start, period_end=query.period_end)
        validate_metric_codes(query.metric_codes)

        async with self._unit_of_work_factory() as unit_of_work:
            analytics_repository = self._analytics_repository_factory(unit_of_work)
            record = await analytics_repository.get_post_analytics(
                workspace_id=actor.workspace_id,
                content_id=query.content_id,
                publication_target_id=query.publication_target_id,
                period_start=query.period_start,
                period_end=query.period_end,
                metric_codes=query.metric_codes,
            )

        if record is None:
            raise AnalyticsNotFoundError(
                detail="Post analytics were not found for the requested content."
            )

        return AnalyticsMapper.to_post_dto(record)
