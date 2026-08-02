"""Analytics repository port and read models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class MetricValueRecord:
    """Single metric observation."""

    code: str
    value: str
    unit: str
    is_estimated: bool


@dataclass(frozen=True, slots=True)
class AnalyticsDashboardRecord:
    """Workspace analytics dashboard read model."""

    period_start: datetime
    period_end: datetime
    time_zone: str
    fresh_through: datetime
    methodology_version: int
    metrics: tuple[MetricValueRecord, ...]


@dataclass(frozen=True, slots=True)
class PlatformAnalyticsRecord:
    """Platform-level aggregate read model."""

    platform_id: UUID
    platform_code: str
    account_count: int
    metrics: tuple[MetricValueRecord, ...]
    fresh_through: datetime


@dataclass(frozen=True, slots=True)
class PostPerformanceRecord:
    """Post/content performance read model."""

    content_id: UUID
    publication_target_id: UUID | None
    snapshot_at: datetime
    reach: int | None
    engagements: int | None
    clicks: int | None
    conversions: int | None
    engagement_rate: str | None
    metrics: tuple[MetricValueRecord, ...]


@dataclass(frozen=True, slots=True)
class ContentPerformanceRecord:
    """Content performance summary read model."""

    content_id: UUID
    title: str
    period_start: datetime
    period_end: datetime
    snapshot_at: datetime
    top_platform_code: str | None
    metrics: tuple[MetricValueRecord, ...]


@dataclass(frozen=True, slots=True)
class AnalyticsSummaryRecord:
    """Workspace analytics summary read model."""

    period_start: datetime
    period_end: datetime
    total_posts: int
    total_reach: int | None
    total_engagements: int | None
    platforms_active: int
    fresh_through: datetime
    methodology_version: int
    metrics: tuple[MetricValueRecord, ...]


@dataclass(frozen=True, slots=True)
class PeriodMetricsRecord:
    """Metrics aggregated for a single period."""

    period_start: datetime
    period_end: datetime
    metrics: tuple[MetricValueRecord, ...]


@dataclass(frozen=True, slots=True)
class MetricDeltaRecord:
    """Metric change between two periods."""

    code: str
    unit: str
    baseline_value: str
    comparison_value: str
    change_percent: str | None
    is_estimated: bool


@dataclass(frozen=True, slots=True)
class DateRangeComparisonRecord:
    """Comparison between two analytics periods."""

    baseline: PeriodMetricsRecord
    comparison: PeriodMetricsRecord
    deltas: tuple[MetricDeltaRecord, ...]
    time_zone: str
    fresh_through: datetime


@dataclass(frozen=True, slots=True)
class AnalyticsSearchCriteria:
    """Structured analytics search criteria."""

    workspace_id: UUID
    query: str | None
    period_start: datetime
    period_end: datetime
    platform_ids: frozenset[UUID]
    social_account_ids: frozenset[UUID]
    metric_codes: frozenset[str]
    cursor: str | None
    limit: int
    sort: str


@dataclass(frozen=True, slots=True)
class PostPerformanceSearchPage:
    """Cursor-paged post performance search results."""

    items: tuple[PostPerformanceRecord, ...]
    next_cursor: str | None
    has_more: bool


@dataclass(frozen=True, slots=True)
class TopPostsCriteria:
    """Criteria for ranking top-performing posts."""

    workspace_id: UUID
    period_start: datetime
    period_end: datetime
    platform_ids: frozenset[UUID]
    social_account_ids: frozenset[UUID]
    metric_codes: frozenset[str]
    cursor: str | None
    limit: int
    sort: str


class ExportStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class ExportFormat(StrEnum):
    CSV = "csv"
    JSON = "json"


@dataclass(frozen=True, slots=True)
class AnalyticsExportRecord:
    """Analytics export job read model."""

    id: UUID
    workspace_id: UUID
    export_type: str
    status: ExportStatus
    format: ExportFormat
    period_start: datetime
    period_end: datetime
    requested_at: datetime
    requested_by: UUID
    row_estimate: int | None


@dataclass(frozen=True, slots=True)
class AnalyticsImportRecord:
    """Imported analytics snapshot reference."""

    id: UUID
    workspace_id: UUID
    imported_at: datetime
    observation_count: int


@dataclass(frozen=True, slots=True)
class DashboardCacheRefreshRecord:
    """Result of a dashboard cache refresh."""

    workspace_id: UUID
    refreshed_at: datetime
    snapshot_count: int


@dataclass(frozen=True, slots=True)
class ArchivedSnapshotRecord:
    """Archived analytics snapshot reference."""

    id: UUID
    workspace_id: UUID
    archived_at: datetime
    archived_by: UUID


@dataclass(frozen=True, slots=True)
class NewAnalyticsImport:
    """Input for importing analytics observations."""

    workspace_id: UUID
    platform_id: UUID | None
    period_start: datetime
    period_end: datetime
    observations: tuple[MetricValueRecord, ...]
    imported_by: UUID


@dataclass(frozen=True, slots=True)
class NewAnalyticsExport:
    """Input for requesting an analytics export."""

    workspace_id: UUID
    export_type: str
    format: ExportFormat
    period_start: datetime
    period_end: datetime
    platform_ids: frozenset[UUID]
    metric_codes: frozenset[str]
    requested_by: UUID
    row_estimate: int


@dataclass(frozen=True, slots=True)
class NewArchivedSnapshot:
    """Input for archiving an analytics snapshot."""

    workspace_id: UUID
    snapshot_id: UUID
    archived_by: UUID


@dataclass(frozen=True, slots=True)
class RefreshDashboardCacheInput:
    """Input for refreshing the dashboard cache."""

    workspace_id: UUID
    period_start: datetime
    period_end: datetime
    time_zone: str
    platform_ids: frozenset[UUID]
    refreshed_by: UUID


class IAnalyticsRepository(Protocol):
    """Repository port for analytics read models and write orchestration."""

    async def get_dashboard(
        self,
        *,
        workspace_id: UUID,
        period_start: datetime,
        period_end: datetime,
        time_zone: str,
        metric_codes: frozenset[str],
        platform_ids: frozenset[UUID],
    ) -> AnalyticsDashboardRecord:
        """Return the workspace analytics dashboard for a period."""

    async def get_platform_analytics(
        self,
        *,
        workspace_id: UUID,
        period_start: datetime,
        period_end: datetime,
        metric_codes: frozenset[str],
        platform_ids: frozenset[UUID],
        sort: str,
    ) -> tuple[PlatformAnalyticsRecord, ...]:
        """Return platform-level analytics aggregates."""

    async def get_post_analytics(
        self,
        *,
        workspace_id: UUID,
        content_id: UUID,
        publication_target_id: UUID | None,
        period_start: datetime,
        period_end: datetime,
        metric_codes: frozenset[str],
    ) -> PostPerformanceRecord | None:
        """Return performance analytics for a single post/content asset."""

    async def get_content_performance(
        self,
        *,
        workspace_id: UUID,
        content_id: UUID,
        period_start: datetime,
        period_end: datetime,
        metric_codes: frozenset[str],
    ) -> ContentPerformanceRecord | None:
        """Return aggregated performance for a content asset."""

    async def get_top_posts(self, criteria: TopPostsCriteria) -> PostPerformanceSearchPage:
        """Return ranked top-performing posts."""

    async def compare_date_ranges(
        self,
        *,
        workspace_id: UUID,
        baseline_start: datetime,
        baseline_end: datetime,
        comparison_start: datetime,
        comparison_end: datetime,
        time_zone: str,
        metric_codes: frozenset[str],
        platform_ids: frozenset[UUID],
    ) -> DateRangeComparisonRecord:
        """Compare metrics across two date ranges."""

    async def search(self, criteria: AnalyticsSearchCriteria) -> PostPerformanceSearchPage:
        """Search analytics observations and post performance."""

    async def get_summary(
        self,
        *,
        workspace_id: UUID,
        period_start: datetime,
        period_end: datetime,
        platform_ids: frozenset[UUID],
    ) -> AnalyticsSummaryRecord:
        """Return a high-level analytics summary for the workspace."""

    async def validate_platform_ids(
        self,
        *,
        workspace_id: UUID,
        platform_ids: frozenset[UUID],
    ) -> bool:
        """Return whether all platform identifiers belong to the workspace."""

    async def estimate_export_rows(
        self,
        *,
        workspace_id: UUID,
        period_start: datetime,
        period_end: datetime,
        platform_ids: frozenset[UUID],
        export_type: str,
    ) -> int:
        """Estimate row count for an export request."""

    async def request_export(self, export_request: NewAnalyticsExport) -> AnalyticsExportRecord:
        """Persist an analytics export request."""

    async def refresh_dashboard_cache(
        self,
        refresh_request: RefreshDashboardCacheInput,
    ) -> DashboardCacheRefreshRecord:
        """Refresh cached dashboard aggregates."""

    async def archive_snapshot(
        self,
        archive_request: NewArchivedSnapshot,
    ) -> ArchivedSnapshotRecord:
        """Archive an analytics snapshot."""

    async def import_observations(
        self,
        import_request: NewAnalyticsImport,
    ) -> AnalyticsImportRecord:
        """Persist imported analytics observations."""
