"""Get top posts query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.analytics.dto.responses import PostAnalyticsResponse
from cloud_content_hub.application.analytics.interfaces.analytics_repository import (
    IAnalyticsRepository,
    TopPostsCriteria,
)
from cloud_content_hub.application.analytics.mappers.analytics_mapper import AnalyticsMapper
from cloud_content_hub.application.analytics.queries import GetTopPostsQuery
from cloud_content_hub.application.analytics.validators.analytics_validator import (
    validate_dashboard_period,
    validate_metric_codes,
    validate_platform_selection,
    validate_post_sort,
    validate_search_limit,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.dto.base import PagedResultDto, PageInfoDto
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class GetTopPostsHandler:
    """Retrieves ranked top-performing posts."""

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
        query: GetTopPostsQuery,
    ) -> PagedResultDto[PostAnalyticsResponse]:
        require_permission(actor, "analytics:read")
        validate_dashboard_period(period_start=query.period_start, period_end=query.period_end)
        validate_metric_codes(query.metric_codes)
        validate_post_sort(query.sort)
        validate_search_limit(query.limit)

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
            page = await analytics_repository.get_top_posts(
                TopPostsCriteria(
                    workspace_id=actor.workspace_id,
                    period_start=query.period_start,
                    period_end=query.period_end,
                    platform_ids=query.platform_ids,
                    social_account_ids=query.social_account_ids,
                    metric_codes=query.metric_codes,
                    cursor=query.cursor,
                    limit=query.limit,
                    sort=query.sort,
                )
            )

        items = tuple(AnalyticsMapper.to_post_dto(record) for record in page.items)
        return PagedResultDto(
            items=items,
            page=PageInfoDto(
                next_cursor=page.next_cursor,
                has_more=page.has_more,
                limit=query.limit,
            ),
        )
