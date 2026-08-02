# Dashboard Queries

## Overview

Dashboard queries return workspace-level KPI aggregates for a validated period. All dashboard handlers require `analytics:read` and scope reads to the actor's workspace.

## GetDashboard

**Query:** `GetDashboardQuery`

| Field          | Type              | Notes                             |
| -------------- | ----------------- | --------------------------------- |
| `period_start` | `datetime`        | Inclusive period start (RFC 3339) |
| `period_end`   | `datetime`        | Exclusive period end              |
| `time_zone`    | `str`             | IANA time zone, default `UTC`     |
| `metric_codes` | `frozenset[str]`  | Optional metric filter            |
| `platform_ids` | `frozenset[UUID]` | Optional platform filter          |

**Returns:** `DashboardResponse`

**Validation:**

- `period_end > period_start`
- Range ≤ 366 days
- Valid IANA time zone
- Known metric codes when provided
- Platform IDs must belong to the workspace when provided

**Handler flow:**

1. Authorize `analytics:read`
2. Validate period, time zone, and metric codes
3. Validate platform ownership when platforms are filtered
4. Call `IAnalyticsRepository.get_dashboard`
5. Map `AnalyticsDashboardRecord` → `DashboardResponse`

## GetAnalyticsSummary

**Query:** `GetAnalyticsSummaryQuery`

Returns a high-level summary including total posts, reach, engagements, active platforms, and aggregate metrics.

**Returns:** `AnalyticsSummaryResponse`

Uses the same period validation as the dashboard. Optional `platform_ids` filter is workspace-validated.

## RefreshDashboardCache

**Command:** `RefreshDashboardCacheCommand`

**Request:** `RefreshDashboardCacheRequestDto`

Refreshes cached dashboard aggregates for the requested period. This is a mutating operation that:

1. Validates period and time zone
2. Calls `IAnalyticsRepository.refresh_dashboard_cache`
3. Publishes `DashboardCacheRefreshed`
4. Returns `RefreshDashboardCacheResult` with snapshot count and refresh timestamp

Background ingestion and snapshot materialization are out of scope for the application module; the repository port owns persistence details.

## Response shape

`DashboardResponse` aligns with the API `AnalyticsDashboard` schema:

```python
class DashboardResponse(ApplicationDto):
    period_start: datetime
    period_end: datetime
    time_zone: str
    fresh_through: datetime
    methodology_version: int
    metrics: tuple[MetricValueDto, ...]
```

Decimal metric values are strings per API contract. `fresh_through` indicates data freshness; `methodology_version` tracks aggregation methodology changes.

## Read-only transactions

Dashboard and summary queries open a unit of work for repository access but do not flush or commit mutations. Cache refresh uses a transactional unit of work with flush and event publication.
