# Analytics Application Module

## Purpose

The analytics application module orchestrates read-only analytics queries and write-side cache/export orchestration for Cloud Content Hub AI. It lives in `backend/src/cloud_content_hub/application/analytics/` and depends only on application shared primitives, repository ports, and `core.errors`.

## Structure

```text
analytics/
├── commands/         # RefreshDashboardCache, RequestAnalyticsExport, ArchiveAnalyticsSnapshot
├── queries/          # Dashboard, platform, post, content, top posts, compare, search, summary
├── handlers/         # One handler per query or command
├── dto/              # Request and response DTOs (never ORM models)
├── validators/       # Date ranges, platforms, metrics, export limits
├── mappers/          # Read model → response DTO mapping
├── interfaces/       # IAnalyticsRepository, IAnalyticsEventPublisher
├── services/         # AggregationService, ExportOrchestrationService
├── events/           # Domain events for exports, cache refresh, snapshot archival
└── exceptions/       # Analytics-specific application errors
```

## Use cases

| Use case                   | Handler                           | Permission       |
| -------------------------- | --------------------------------- | ---------------- |
| Get dashboard              | `GetDashboardHandler`             | `analytics:read` |
| Get platform analytics     | `GetPlatformAnalyticsHandler`     | `analytics:read` |
| Get post analytics         | `GetPostAnalyticsHandler`         | `analytics:read` |
| Get content performance    | `GetContentPerformanceHandler`    | `analytics:read` |
| Get top posts              | `GetTopPostsHandler`              | `analytics:read` |
| Compare date ranges        | `CompareDateRangesHandler`        | `analytics:read` |
| Search analytics           | `SearchAnalyticsHandler`          | `analytics:read` |
| Get analytics summary      | `GetAnalyticsSummaryHandler`      | `analytics:read` |
| Refresh dashboard cache    | `RefreshDashboardCacheHandler`    | `analytics:read` |
| Request analytics export   | `RequestAnalyticsExportHandler`   | `analytics:read` |
| Archive analytics snapshot | `ArchiveAnalyticsSnapshotHandler` | `analytics:read` |
| Import analytics           | `ImportAnalyticsHandler`          | `analytics:read` |

## Business rules

- All analytics are scoped to `ActorContext.workspace_id`.
- Date ranges must be ordered and cannot exceed 366 days.
- Comparison periods must have equal duration.
- Aggregations are read-only; handlers never mutate metric observations directly.
- Exports are asynchronous: handlers persist the export request and raise `AnalyticsExportRequested`; background workers perform the actual export.
- Handlers never return SQLAlchemy models or repository read models to callers.

## Repository port

`IAnalyticsRepository` declares read models as frozen dataclasses and exposes methods for dashboard, platform, post, content, search, comparison, summary, export estimation, cache refresh, and snapshot archival. Infrastructure implements the port; application code does not issue SQL.

## Events

| Event                       | Raised by                         |
| --------------------------- | --------------------------------- |
| `AnalyticsExportRequested`  | `RequestAnalyticsExportHandler`   |
| `DashboardCacheRefreshed`   | `RefreshDashboardCacheHandler`    |
| `AnalyticsSnapshotArchived` | `ArchiveAnalyticsSnapshotHandler` |

Events are published through `IAnalyticsEventPublisher` within the same unit of work as the originating mutation.

## Related documentation

- [`DASHBOARD.md`](DASHBOARD.md) — dashboard and summary queries
- [`METRICS.md`](METRICS.md) — metric codes, post/platform performance, comparisons
- [`EXPORTS.md`](EXPORTS.md) — export orchestration and limits

See also: [`../APPLICATION_LAYER.md`](../APPLICATION_LAYER.md), [`../../api/ANALYTICS_API.md`](../../api/ANALYTICS_API.md).
