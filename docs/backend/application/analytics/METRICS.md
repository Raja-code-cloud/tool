# Metrics and Performance Queries

## Metric codes

Known metric codes (allowlist):

| Code             | Typical unit |
| ---------------- | ------------ |
| `reach`          | count        |
| `engagements`    | count        |
| `clicks`         | count        |
| `conversions`    | count        |
| `engagementRate` | ratio        |
| `impressions`    | count        |
| `shares`         | count        |
| `comments`       | count        |
| `likes`          | count        |
| `views`          | count        |

Handlers validate requested codes against this allowlist. Empty `metric_codes` means no filter (all available metrics returned by the repository).

## Platform analytics

**Query:** `GetPlatformAnalyticsQuery`

**Returns:** `tuple[PlatformAnalyticsResponse, ...]`

Compares platform/account aggregates for a period. Supports sorting by `platformCode` or `-platformCode`.

Each `PlatformAnalyticsResponse` includes:

- `platform_id`, `platform_code`
- `account_count`
- `metrics` — tuple of `MetricValueDto`
- `fresh_through`

## Post and content performance

### GetPostAnalytics

**Query:** `GetPostAnalyticsQuery`

**Returns:** `PostAnalyticsResponse`

Retrieves performance for a single content/post asset, optionally scoped to a `publication_target_id`. Raises `AnalyticsNotFoundError` when no data exists for the workspace-scoped content.

### GetContentPerformance

**Query:** `GetContentPerformanceQuery`

**Returns:** `ContentPerformanceResponse`

Aggregated content performance including title, period, top platform, and metrics.

### GetTopPosts

**Query:** `GetTopPostsQuery`

**Returns:** `PagedResultDto[PostAnalyticsResponse]`

Ranks top-performing posts with cursor pagination. Default sort is `-snapshotAt`.

Allowed sort fields: `reach`, `engagements`, `clicks`, `conversions`, `engagementRate`, `snapshotAt` (prefix `-` for descending).

## Search analytics

**Query:** `SearchAnalyticsQuery`

**Returns:** `PagedResultDto[PostAnalyticsResponse]`

Full-text or structured search over post performance with period, platform, social account, and metric filters. Limit is validated between 1 and 100.

## Date range comparison

**Query:** `CompareDateRangesQuery`

**Returns:** `DateRangeComparisonResponse`

Compares two periods of equal duration:

| Field                                | Description       |
| ------------------------------------ | ----------------- |
| `baseline_start`, `baseline_end`     | Reference period  |
| `comparison_start`, `comparison_end` | Comparison period |
| `time_zone`                          | IANA time zone    |
| `metric_codes`                       | Optional filter   |
| `platform_ids`                       | Optional filter   |

`AggregationService` computes per-metric deltas including `change_percent` when values are numeric. Non-numeric or zero-baseline metrics omit percentage change.

## Validation summary

| Rule                           | Validator                     |
| ------------------------------ | ----------------------------- |
| Ordered period, max 366 days   | `validate_dashboard_period`   |
| Equal comparison period length | `validate_compare_periods`    |
| Known metric codes             | `validate_metric_codes`       |
| Workspace platform ownership   | `validate_platform_selection` |
| Post/search sort allowlist     | `validate_post_sort`          |
| Platform sort allowlist        | `validate_platform_sort`      |
| Pagination limit 1–100         | `validate_search_limit`       |

All aggregations are read-only. Handlers delegate aggregation to `IAnalyticsRepository`; the application layer does not compute rollups from raw observations unless enriching comparison deltas.
