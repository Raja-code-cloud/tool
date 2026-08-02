"""Analytics export orchestration helpers."""

from __future__ import annotations

from uuid import UUID

from cloud_content_hub.application.analytics.dto.requests import AnalyticsExportRequestDto
from cloud_content_hub.application.analytics.interfaces.analytics_repository import (
    ExportFormat,
    IAnalyticsRepository,
    NewAnalyticsExport,
)
from cloud_content_hub.application.analytics.validators.analytics_validator import (
    validate_export_request,
)


class ExportOrchestrationService:
    """Orchestrates analytics export validation and persistence."""

    def __init__(self, *, analytics_repository: IAnalyticsRepository) -> None:
        self._analytics_repository = analytics_repository

    async def create_export(
        self,
        *,
        workspace_id: UUID,
        request: AnalyticsExportRequestDto,
        requested_by: UUID,
    ) -> NewAnalyticsExport:
        """Validate export limits and build the repository input."""

        platform_ids = frozenset(request.platform_ids)
        row_estimate = await self._analytics_repository.estimate_export_rows(
            workspace_id=workspace_id,
            period_start=request.period_start,
            period_end=request.period_end,
            platform_ids=platform_ids,
            export_type=request.export_type,
        )
        validate_export_request(request, row_estimate=row_estimate)
        return NewAnalyticsExport(
            workspace_id=workspace_id,
            export_type=request.export_type,
            format=ExportFormat(request.format.value),
            period_start=request.period_start,
            period_end=request.period_end,
            platform_ids=platform_ids,
            metric_codes=frozenset(request.metric_codes),
            requested_by=requested_by,
            row_estimate=row_estimate,
        )
