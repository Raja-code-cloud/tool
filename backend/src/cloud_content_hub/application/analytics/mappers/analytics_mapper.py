"""Analytics record to DTO mappers."""

from __future__ import annotations

from cloud_content_hub.application.analytics.dto.responses import (
    AnalyticsExportResponse,
    AnalyticsSummaryResponse,
    ContentPerformanceResponse,
    DashboardResponse,
    DateRangeComparisonResponse,
    ExportFormatDto,
    ExportStatusDto,
    MetricDeltaDto,
    MetricValueDto,
    PeriodMetricsDto,
    PlatformAnalyticsResponse,
    PostAnalyticsResponse,
)
from cloud_content_hub.application.analytics.interfaces.analytics_repository import (
    AnalyticsDashboardRecord,
    AnalyticsExportRecord,
    AnalyticsSummaryRecord,
    ContentPerformanceRecord,
    DateRangeComparisonRecord,
    MetricDeltaRecord,
    MetricValueRecord,
    PeriodMetricsRecord,
    PlatformAnalyticsRecord,
    PostPerformanceRecord,
)


class AnalyticsMapper:
    """Maps analytics read models to response DTOs."""

    @staticmethod
    def to_metric_dto(record: MetricValueRecord) -> MetricValueDto:
        return MetricValueDto(
            code=record.code,
            value=record.value,
            unit=record.unit,
            is_estimated=record.is_estimated,
        )

    @staticmethod
    def to_metrics_dto(records: tuple[MetricValueRecord, ...]) -> tuple[MetricValueDto, ...]:
        return tuple(AnalyticsMapper.to_metric_dto(record) for record in records)

    @staticmethod
    def to_dashboard_dto(record: AnalyticsDashboardRecord) -> DashboardResponse:
        return DashboardResponse(
            period_start=record.period_start,
            period_end=record.period_end,
            time_zone=record.time_zone,
            fresh_through=record.fresh_through,
            methodology_version=record.methodology_version,
            metrics=AnalyticsMapper.to_metrics_dto(record.metrics),
        )

    @staticmethod
    def to_platform_dto(record: PlatformAnalyticsRecord) -> PlatformAnalyticsResponse:
        return PlatformAnalyticsResponse(
            platform_id=record.platform_id,
            platform_code=record.platform_code,
            account_count=record.account_count,
            metrics=AnalyticsMapper.to_metrics_dto(record.metrics),
            fresh_through=record.fresh_through,
        )

    @staticmethod
    def to_post_dto(record: PostPerformanceRecord) -> PostAnalyticsResponse:
        return PostAnalyticsResponse(
            content_id=record.content_id,
            publication_target_id=record.publication_target_id,
            snapshot_at=record.snapshot_at,
            reach=record.reach,
            engagements=record.engagements,
            clicks=record.clicks,
            conversions=record.conversions,
            engagement_rate=record.engagement_rate,
            metrics=AnalyticsMapper.to_metrics_dto(record.metrics),
        )

    @staticmethod
    def to_content_performance_dto(record: ContentPerformanceRecord) -> ContentPerformanceResponse:
        return ContentPerformanceResponse(
            content_id=record.content_id,
            title=record.title,
            period_start=record.period_start,
            period_end=record.period_end,
            snapshot_at=record.snapshot_at,
            top_platform_code=record.top_platform_code,
            metrics=AnalyticsMapper.to_metrics_dto(record.metrics),
        )

    @staticmethod
    def to_summary_dto(record: AnalyticsSummaryRecord) -> AnalyticsSummaryResponse:
        return AnalyticsSummaryResponse(
            period_start=record.period_start,
            period_end=record.period_end,
            total_posts=record.total_posts,
            total_reach=record.total_reach,
            total_engagements=record.total_engagements,
            platforms_active=record.platforms_active,
            fresh_through=record.fresh_through,
            methodology_version=record.methodology_version,
            metrics=AnalyticsMapper.to_metrics_dto(record.metrics),
        )

    @staticmethod
    def to_period_dto(record: PeriodMetricsRecord) -> PeriodMetricsDto:
        return PeriodMetricsDto(
            period_start=record.period_start,
            period_end=record.period_end,
            metrics=AnalyticsMapper.to_metrics_dto(record.metrics),
        )

    @staticmethod
    def to_delta_dto(record: MetricDeltaRecord) -> MetricDeltaDto:
        return MetricDeltaDto(
            code=record.code,
            unit=record.unit,
            baseline_value=record.baseline_value,
            comparison_value=record.comparison_value,
            change_percent=record.change_percent,
            is_estimated=record.is_estimated,
        )

    @staticmethod
    def to_comparison_dto(record: DateRangeComparisonRecord) -> DateRangeComparisonResponse:
        return DateRangeComparisonResponse(
            baseline=AnalyticsMapper.to_period_dto(record.baseline),
            comparison=AnalyticsMapper.to_period_dto(record.comparison),
            deltas=tuple(AnalyticsMapper.to_delta_dto(delta) for delta in record.deltas),
            time_zone=record.time_zone,
            fresh_through=record.fresh_through,
        )

    @staticmethod
    def to_export_dto(record: AnalyticsExportRecord) -> AnalyticsExportResponse:
        return AnalyticsExportResponse(
            id=record.id,
            export_type=record.export_type,
            status=ExportStatusDto(record.status.value),
            format=ExportFormatDto(record.format.value),
            period_start=record.period_start,
            period_end=record.period_end,
            requested_at=record.requested_at,
            row_estimate=record.row_estimate,
        )
