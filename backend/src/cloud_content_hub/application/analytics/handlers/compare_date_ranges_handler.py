"""Compare date ranges query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.analytics.dto.responses import DateRangeComparisonResponse
from cloud_content_hub.application.analytics.interfaces.analytics_repository import (
    IAnalyticsRepository,
)
from cloud_content_hub.application.analytics.mappers.analytics_mapper import AnalyticsMapper
from cloud_content_hub.application.analytics.queries import CompareDateRangesQuery
from cloud_content_hub.application.analytics.services.aggregation_service import AggregationService
from cloud_content_hub.application.analytics.validators.analytics_validator import (
    validate_compare_periods,
    validate_metric_codes,
    validate_platform_selection,
    validate_time_zone,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class CompareDateRangesHandler:
    """Compares metrics across two date ranges."""

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
        query: CompareDateRangesQuery,
    ) -> DateRangeComparisonResponse:
        require_permission(actor, "analytics:read")
        validate_compare_periods(
            baseline_start=query.baseline_start,
            baseline_end=query.baseline_end,
            comparison_start=query.comparison_start,
            comparison_end=query.comparison_end,
        )
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
            record = await analytics_repository.compare_date_ranges(
                workspace_id=actor.workspace_id,
                baseline_start=query.baseline_start,
                baseline_end=query.baseline_end,
                comparison_start=query.comparison_start,
                comparison_end=query.comparison_end,
                time_zone=query.time_zone,
                metric_codes=query.metric_codes,
                platform_ids=query.platform_ids,
            )

        enriched = AggregationService.enrich_comparison(record)
        return AnalyticsMapper.to_comparison_dto(enriched)
