"""Analytics query definitions."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class GetDashboardQuery:
    """Query to retrieve the analytics dashboard."""

    period_start: datetime
    period_end: datetime
    time_zone: str = "UTC"
    metric_codes: frozenset[str] = frozenset()
    platform_ids: frozenset[UUID] = frozenset()


@dataclass(frozen=True, slots=True)
class GetPlatformAnalyticsQuery:
    """Query to retrieve platform-level analytics aggregates."""

    period_start: datetime
    period_end: datetime
    metric_codes: frozenset[str] = frozenset()
    platform_ids: frozenset[UUID] = frozenset()
    sort: str = "platformCode"


@dataclass(frozen=True, slots=True)
class GetPostAnalyticsQuery:
    """Query to retrieve performance analytics for a single post."""

    content_id: UUID
    publication_target_id: UUID | None
    period_start: datetime
    period_end: datetime
    metric_codes: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class GetContentPerformanceQuery:
    """Query to retrieve aggregated content performance."""

    content_id: UUID
    period_start: datetime
    period_end: datetime
    metric_codes: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class GetTopPostsQuery:
    """Query to retrieve top-performing posts."""

    period_start: datetime
    period_end: datetime
    platform_ids: frozenset[UUID] = frozenset()
    social_account_ids: frozenset[UUID] = frozenset()
    metric_codes: frozenset[str] = frozenset()
    cursor: str | None = None
    limit: int = 25
    sort: str = "-snapshotAt"


@dataclass(frozen=True, slots=True)
class CompareDateRangesQuery:
    """Query to compare metrics across two date ranges."""

    baseline_start: datetime
    baseline_end: datetime
    comparison_start: datetime
    comparison_end: datetime
    time_zone: str = "UTC"
    metric_codes: frozenset[str] = frozenset()
    platform_ids: frozenset[UUID] = frozenset()


@dataclass(frozen=True, slots=True)
class SearchAnalyticsQuery:
    """Query to search analytics observations and post performance."""

    query: str | None
    period_start: datetime
    period_end: datetime
    platform_ids: frozenset[UUID] = frozenset()
    social_account_ids: frozenset[UUID] = frozenset()
    metric_codes: frozenset[str] = frozenset()
    cursor: str | None = None
    limit: int = 25
    sort: str = "-snapshotAt"


@dataclass(frozen=True, slots=True)
class GetAnalyticsSummaryQuery:
    """Query to retrieve a high-level analytics summary."""

    period_start: datetime
    period_end: datetime
    platform_ids: frozenset[UUID] = frozenset()
