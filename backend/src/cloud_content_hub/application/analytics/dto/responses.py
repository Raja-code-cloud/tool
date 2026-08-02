"""Analytics response DTOs."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from cloud_content_hub.application.shared.dto.base import ApplicationDto


class ExportStatusDto(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ExportFormatDto(StrEnum):
    CSV = "csv"
    JSON = "json"


class MetricValueDto(ApplicationDto):
    """Metric value returned in analytics responses."""

    code: str
    value: str
    unit: str
    is_estimated: bool


class DashboardResponse(ApplicationDto):
    """Analytics dashboard projection."""

    period_start: datetime
    period_end: datetime
    time_zone: str
    fresh_through: datetime
    methodology_version: int
    metrics: tuple[MetricValueDto, ...]


# Backward-compatible alias used by existing handlers and docs.
AnalyticsDashboardDto = DashboardResponse


class PlatformAnalyticsResponse(ApplicationDto):
    """Platform-level analytics aggregate."""

    platform_id: UUID
    platform_code: str
    account_count: int
    metrics: tuple[MetricValueDto, ...]
    fresh_through: datetime


class PostAnalyticsResponse(ApplicationDto):
    """Post/content performance projection."""

    content_id: UUID
    publication_target_id: UUID | None = None
    snapshot_at: datetime
    reach: int | None = None
    engagements: int | None = None
    clicks: int | None = None
    conversions: int | None = None
    engagement_rate: str | None = None
    metrics: tuple[MetricValueDto, ...]


class ContentPerformanceResponse(ApplicationDto):
    """Content performance summary projection."""

    content_id: UUID
    title: str
    period_start: datetime
    period_end: datetime
    snapshot_at: datetime
    top_platform_code: str | None = None
    metrics: tuple[MetricValueDto, ...]


class AnalyticsSummaryResponse(ApplicationDto):
    """High-level workspace analytics summary."""

    period_start: datetime
    period_end: datetime
    total_posts: int
    total_reach: int | None = None
    total_engagements: int | None = None
    platforms_active: int
    fresh_through: datetime
    methodology_version: int
    metrics: tuple[MetricValueDto, ...]


class PeriodMetricsDto(ApplicationDto):
    """Metrics for a single analytics period."""

    period_start: datetime
    period_end: datetime
    metrics: tuple[MetricValueDto, ...]


class MetricDeltaDto(ApplicationDto):
    """Metric change between two periods."""

    code: str
    unit: str
    baseline_value: str
    comparison_value: str
    change_percent: str | None = None
    is_estimated: bool


class DateRangeComparisonResponse(ApplicationDto):
    """Comparison between two analytics periods."""

    baseline: PeriodMetricsDto
    comparison: PeriodMetricsDto
    deltas: tuple[MetricDeltaDto, ...]
    time_zone: str
    fresh_through: datetime


class AnalyticsExportResponse(ApplicationDto):
    """Analytics export request projection."""

    id: UUID
    export_type: str
    status: ExportStatusDto
    format: ExportFormatDto
    period_start: datetime
    period_end: datetime
    requested_at: datetime
    row_estimate: int | None = None
