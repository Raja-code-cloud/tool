"""Analytics application module."""

from cloud_content_hub.application.analytics.commands import (
    ArchiveAnalyticsSnapshotCommand,
    ImportAnalyticsCommand,
    RefreshDashboardCacheCommand,
    RequestAnalyticsExportCommand,
)
from cloud_content_hub.application.analytics.dto.responses import (
    AnalyticsDashboardDto,
    AnalyticsExportResponse,
    AnalyticsSummaryResponse,
    ContentPerformanceResponse,
    DashboardResponse,
    DateRangeComparisonResponse,
    PlatformAnalyticsResponse,
    PostAnalyticsResponse,
)
from cloud_content_hub.application.analytics.events import (
    AnalyticsExportRequested,
    AnalyticsSnapshotArchived,
    DashboardCacheRefreshed,
)
from cloud_content_hub.application.analytics.handlers.archive_analytics_snapshot_handler import (
    ArchiveAnalyticsSnapshotHandler,
)
from cloud_content_hub.application.analytics.handlers.compare_date_ranges_handler import (
    CompareDateRangesHandler,
)
from cloud_content_hub.application.analytics.handlers.get_analytics_summary_handler import (
    GetAnalyticsSummaryHandler,
)
from cloud_content_hub.application.analytics.handlers.get_content_performance_handler import (
    GetContentPerformanceHandler,
)
from cloud_content_hub.application.analytics.handlers.get_dashboard_handler import (
    GetDashboardHandler,
)
from cloud_content_hub.application.analytics.handlers.get_platform_analytics_handler import (
    GetPlatformAnalyticsHandler,
)
from cloud_content_hub.application.analytics.handlers.get_post_analytics_handler import (
    GetPostAnalyticsHandler,
)
from cloud_content_hub.application.analytics.handlers.get_top_posts_handler import (
    GetTopPostsHandler,
)
from cloud_content_hub.application.analytics.handlers.import_analytics_handler import (
    ImportAnalyticsHandler,
)
from cloud_content_hub.application.analytics.handlers.refresh_dashboard_cache_handler import (
    RefreshDashboardCacheHandler,
)
from cloud_content_hub.application.analytics.handlers.request_analytics_export_handler import (
    RequestAnalyticsExportHandler,
)
from cloud_content_hub.application.analytics.handlers.search_analytics_handler import (
    SearchAnalyticsHandler,
)
from cloud_content_hub.application.analytics.queries import (
    CompareDateRangesQuery,
    GetAnalyticsSummaryQuery,
    GetContentPerformanceQuery,
    GetDashboardQuery,
    GetPlatformAnalyticsQuery,
    GetPostAnalyticsQuery,
    GetTopPostsQuery,
    SearchAnalyticsQuery,
)

__all__ = [
    "AnalyticsDashboardDto",
    "AnalyticsExportRequested",
    "AnalyticsExportResponse",
    "AnalyticsSnapshotArchived",
    "AnalyticsSummaryResponse",
    "ArchiveAnalyticsSnapshotCommand",
    "ArchiveAnalyticsSnapshotHandler",
    "CompareDateRangesHandler",
    "CompareDateRangesQuery",
    "ContentPerformanceResponse",
    "DashboardCacheRefreshed",
    "DashboardResponse",
    "DateRangeComparisonResponse",
    "GetAnalyticsSummaryHandler",
    "GetAnalyticsSummaryQuery",
    "GetContentPerformanceHandler",
    "GetContentPerformanceQuery",
    "GetDashboardHandler",
    "GetDashboardQuery",
    "GetPlatformAnalyticsHandler",
    "GetPlatformAnalyticsQuery",
    "GetPostAnalyticsHandler",
    "GetPostAnalyticsQuery",
    "GetTopPostsHandler",
    "GetTopPostsQuery",
    "ImportAnalyticsCommand",
    "ImportAnalyticsHandler",
    "PlatformAnalyticsResponse",
    "PostAnalyticsResponse",
    "RefreshDashboardCacheCommand",
    "RefreshDashboardCacheHandler",
    "RequestAnalyticsExportCommand",
    "RequestAnalyticsExportHandler",
    "SearchAnalyticsHandler",
    "SearchAnalyticsQuery",
]
