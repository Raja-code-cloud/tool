"""Analytics request DTOs."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import Field

from cloud_content_hub.application.shared.dto.base import ApplicationDto


class ExportFormatRequestDto(StrEnum):
    CSV = "csv"
    JSON = "json"


class MetricImportDto(ApplicationDto):
    """Single metric value to import."""

    code: str = Field(min_length=1)
    value: str
    unit: str = Field(min_length=1)
    is_estimated: bool = False


class ImportAnalyticsRequestDto(ApplicationDto):
    """Request payload for importing analytics observations."""

    platform_id: UUID | None = None
    period_start: datetime
    period_end: datetime
    observations: tuple[MetricImportDto, ...] = Field(min_length=1)


class AnalyticsExportRequestDto(ApplicationDto):
    """Request payload for an asynchronous analytics export."""

    export_type: str = Field(min_length=1, max_length=64)
    format: ExportFormatRequestDto = ExportFormatRequestDto.CSV
    period_start: datetime
    period_end: datetime
    platform_ids: tuple[UUID, ...] = ()
    metric_codes: tuple[str, ...] = ()


class RefreshDashboardCacheRequestDto(ApplicationDto):
    """Request payload for refreshing dashboard cache aggregates."""

    period_start: datetime
    period_end: datetime
    time_zone: str = "UTC"
    platform_ids: tuple[UUID, ...] = ()


class ArchiveAnalyticsSnapshotRequestDto(ApplicationDto):
    """Request payload for archiving an analytics snapshot."""

    snapshot_id: UUID
