"""Analytics business validation."""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from cloud_content_hub.application.analytics.dto.requests import (
    AnalyticsExportRequestDto,
    ImportAnalyticsRequestDto,
    RefreshDashboardCacheRequestDto,
)
from cloud_content_hub.application.analytics.exceptions.analytics_errors import (
    AnalyticsExportLimitError,
    AnalyticsMetricError,
    AnalyticsPlatformError,
    AnalyticsValidationError,
)

MAX_PERIOD_DAYS = 366
MAX_EXPORT_ROWS = 100_000
MAX_SEARCH_LIMIT = 100
MIN_SEARCH_LIMIT = 1

KNOWN_METRIC_CODES: frozenset[str] = frozenset(
    {
        "reach",
        "engagements",
        "clicks",
        "conversions",
        "engagementRate",
        "impressions",
        "shares",
        "comments",
        "likes",
        "views",
    }
)

POST_PERFORMANCE_SORT_FIELDS: frozenset[str] = frozenset(
    {
        "reach",
        "engagements",
        "clicks",
        "conversions",
        "engagementRate",
        "snapshotAt",
        "-reach",
        "-engagements",
        "-clicks",
        "-conversions",
        "-engagementRate",
        "-snapshotAt",
    }
)

PLATFORM_ANALYTICS_SORT_FIELDS: frozenset[str] = frozenset({"platformCode", "-platformCode"})


def validate_dashboard_period(*, period_start: datetime, period_end: datetime) -> None:
    """Validate analytics period constraints."""

    if period_end <= period_start:
        raise AnalyticsValidationError(detail="periodEnd must be after periodStart.")
    if period_end - period_start > timedelta(days=MAX_PERIOD_DAYS):
        raise AnalyticsValidationError(
            detail=f"Analytics period cannot exceed {MAX_PERIOD_DAYS} days."
        )


def validate_time_zone(time_zone: str) -> None:
    """Validate an IANA time zone identifier."""

    try:
        ZoneInfo(time_zone)
    except ZoneInfoNotFoundError as exc:
        raise AnalyticsValidationError(detail=f"Unknown time zone: {time_zone}.") from exc


def validate_metric_codes(metric_codes: frozenset[str]) -> None:
    """Validate requested metric codes against the known allowlist."""

    if not metric_codes:
        return
    unknown = metric_codes - KNOWN_METRIC_CODES
    if unknown:
        codes = ", ".join(sorted(unknown))
        raise AnalyticsMetricError(detail=f"Unknown metric codes: {codes}.")


def validate_platform_selection(*, platform_ids: frozenset[UUID], platforms_valid: bool) -> None:
    """Validate that platform identifiers belong to the workspace."""

    if platform_ids and not platforms_valid:
        raise AnalyticsPlatformError(detail="One or more platform identifiers are invalid.")


def validate_post_sort(sort: str) -> None:
    """Validate post performance sort field."""

    if sort not in POST_PERFORMANCE_SORT_FIELDS:
        raise AnalyticsValidationError(
            detail=(
                "Invalid sort field. Allowed values: "
                "reach, engagements, clicks, conversions, engagementRate, snapshotAt "
                "(prefix with '-' for descending)."
            )
        )


def validate_platform_sort(sort: str) -> None:
    """Validate platform analytics sort field."""

    if sort not in PLATFORM_ANALYTICS_SORT_FIELDS:
        raise AnalyticsValidationError(
            detail="Invalid sort field. Allowed values: platformCode, -platformCode."
        )


def validate_search_limit(limit: int) -> None:
    """Validate cursor pagination limit."""

    if limit < MIN_SEARCH_LIMIT or limit > MAX_SEARCH_LIMIT:
        raise AnalyticsValidationError(
            detail=f"Limit must be between {MIN_SEARCH_LIMIT} and {MAX_SEARCH_LIMIT}."
        )


def validate_compare_periods(
    *,
    baseline_start: datetime,
    baseline_end: datetime,
    comparison_start: datetime,
    comparison_end: datetime,
) -> None:
    """Validate date range comparison inputs."""

    validate_dashboard_period(period_start=baseline_start, period_end=baseline_end)
    validate_dashboard_period(period_start=comparison_start, period_end=comparison_end)

    baseline_length = baseline_end - baseline_start
    comparison_length = comparison_end - comparison_start
    if baseline_length != comparison_length:
        raise AnalyticsValidationError(
            detail="Baseline and comparison periods must have equal duration."
        )


def validate_export_request(request: AnalyticsExportRequestDto, *, row_estimate: int) -> None:
    """Validate analytics export business rules."""

    validate_dashboard_period(period_start=request.period_start, period_end=request.period_end)
    validate_metric_codes(frozenset(request.metric_codes))
    if row_estimate > MAX_EXPORT_ROWS:
        raise AnalyticsExportLimitError(
            detail=(
                f"Export would produce approximately {row_estimate} rows, "
                f"exceeding the limit of {MAX_EXPORT_ROWS}."
            )
        )


def validate_import_request(request: ImportAnalyticsRequestDto) -> None:
    """Validate analytics import business rules."""

    validate_dashboard_period(period_start=request.period_start, period_end=request.period_end)


def validate_refresh_cache_request(request: RefreshDashboardCacheRequestDto) -> None:
    """Validate dashboard cache refresh inputs."""

    validate_dashboard_period(period_start=request.period_start, period_end=request.period_end)
    validate_time_zone(request.time_zone)
