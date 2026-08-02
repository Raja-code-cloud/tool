"""Analytics command definitions."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from cloud_content_hub.application.analytics.dto.requests import (
    AnalyticsExportRequestDto,
    ImportAnalyticsRequestDto,
    RefreshDashboardCacheRequestDto,
)


@dataclass(frozen=True, slots=True)
class ImportAnalyticsCommand:
    """Command to import analytics observations."""

    request: ImportAnalyticsRequestDto
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RefreshDashboardCacheCommand:
    """Command to refresh cached dashboard aggregates."""

    request: RefreshDashboardCacheRequestDto


@dataclass(frozen=True, slots=True)
class RequestAnalyticsExportCommand:
    """Command to request an asynchronous analytics export."""

    request: AnalyticsExportRequestDto
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class ArchiveAnalyticsSnapshotCommand:
    """Command to archive an analytics snapshot."""

    snapshot_id: UUID
