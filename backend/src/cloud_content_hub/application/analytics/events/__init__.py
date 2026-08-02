"""Analytics domain events raised by command handlers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AnalyticsExportRequested:
    """Raised when an asynchronous analytics export is queued."""

    workspace_id: UUID
    export_id: UUID
    export_type: str
    actor_id: UUID
    period_start: datetime
    period_end: datetime
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class DashboardCacheRefreshed:
    """Raised when the workspace dashboard cache is refreshed."""

    workspace_id: UUID
    actor_id: UUID
    snapshot_count: int
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class AnalyticsSnapshotArchived:
    """Raised when an analytics snapshot is archived."""

    workspace_id: UUID
    snapshot_id: UUID
    actor_id: UUID
    occurred_at: datetime


AnalyticsDomainEvent = (
    AnalyticsExportRequested | DashboardCacheRefreshed | AnalyticsSnapshotArchived
)

__all__ = [
    "AnalyticsDomainEvent",
    "AnalyticsExportRequested",
    "AnalyticsSnapshotArchived",
    "DashboardCacheRefreshed",
]
