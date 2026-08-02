"""SQLAlchemy analytics repository adapter."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from cloud_content_hub.application.analytics.exceptions.analytics_errors import (
    AnalyticsSnapshotNotFoundError,
)
from cloud_content_hub.application.analytics.interfaces.analytics_repository import (
    AnalyticsDashboardRecord,
    AnalyticsExportRecord,
    AnalyticsImportRecord,
    AnalyticsSearchCriteria,
    AnalyticsSummaryRecord,
    ArchivedSnapshotRecord,
    ContentPerformanceRecord,
    DashboardCacheRefreshRecord,
    DateRangeComparisonRecord,
    ExportStatus,
    MetricDeltaRecord,
    MetricValueRecord,
    NewAnalyticsExport,
    NewAnalyticsImport,
    NewArchivedSnapshot,
    PeriodMetricsRecord,
    PlatformAnalyticsRecord,
    PostPerformanceRecord,
    PostPerformanceSearchPage,
    RefreshDashboardCacheInput,
    TopPostsCriteria,
)
from cloud_content_hub.infrastructure.database.enums import (
    DataExportState,
    DataExportType,
    JobState,
)
from cloud_content_hub.infrastructure.database.models.analytics_snapshot import AnalyticsSnapshot
from cloud_content_hub.infrastructure.database.models.background_job import BackgroundJob
from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
from cloud_content_hub.infrastructure.database.models.content_performance_snapshot import (
    ContentPerformanceSnapshot,
)
from cloud_content_hub.infrastructure.database.models.data_export import DataExport
from cloud_content_hub.infrastructure.database.models.metric_definition import MetricDefinition
from cloud_content_hub.infrastructure.database.models.metric_observation import MetricObservation
from cloud_content_hub.infrastructure.database.models.publication_target import PublicationTarget
from cloud_content_hub.infrastructure.database.models.social_account import SocialAccount
from cloud_content_hub.infrastructure.database.models.social_platform import SocialPlatform
from cloud_content_hub.infrastructure.repositories.sqlalchemy.base import SqlAlchemyRepository
from cloud_content_hub.infrastructure.repositories.sqlalchemy.cursor_pagination import (
    apply_keyset_pagination,
    build_keyset_page,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import EntityNotFound
from cloud_content_hub.infrastructure.repositories.sqlalchemy.sorting import (
    SortColumn,
    SortDirection,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.utils import utc_now

_DEFAULT_METHODOLOGY_VERSION = 1
_POST_SORT_FIELD_MAP = {
    "reach": "reach",
    "engagements": "engagements",
    "clicks": "clicks",
    "conversions": "conversions",
    "engagementRate": "engagement_rate",
    "snapshotAt": "snapshot_at",
}


class SqlAlchemyAnalyticsRepository:
    """Persistence adapter for analytics read models and write orchestration."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._snapshots = SqlAlchemyRepository(
            session,
            AnalyticsSnapshot,
            entity_name="AnalyticsSnapshot",
            workspace_scoped=True,
        )
        self._exports = SqlAlchemyRepository(
            session,
            DataExport,
            entity_name="DataExport",
            workspace_scoped=True,
        )

    async def get_dashboard(
        self,
        *,
        workspace_id: UUID,
        period_start: datetime,
        period_end: datetime,
        time_zone: str,
        metric_codes: frozenset[str],
        platform_ids: frozenset[UUID],
    ) -> AnalyticsDashboardRecord:
        """Return the workspace analytics dashboard for a period."""

        snapshot = await self._find_workspace_kpi_snapshot(
            workspace_id=workspace_id,
            period_start=period_start,
            period_end=period_end,
            platform_ids=platform_ids,
        )
        if snapshot is not None:
            metrics = _filter_metrics(_metrics_from_snapshot(snapshot.metrics), metric_codes)
            return AnalyticsDashboardRecord(
                period_start=snapshot.period_start,
                period_end=snapshot.period_end,
                time_zone=snapshot.time_zone,
                fresh_through=snapshot.fresh_through,
                methodology_version=snapshot.methodology_version,
                metrics=metrics,
            )

        metrics = await self._aggregate_observation_metrics(
            workspace_id=workspace_id,
            period_start=period_start,
            period_end=period_end,
            platform_ids=platform_ids,
            social_account_ids=frozenset(),
            metric_codes=metric_codes,
        )
        return AnalyticsDashboardRecord(
            period_start=period_start,
            period_end=period_end,
            time_zone=time_zone,
            fresh_through=utc_now(),
            methodology_version=_DEFAULT_METHODOLOGY_VERSION,
            metrics=metrics,
        )

    async def get_platform_analytics(
        self,
        *,
        workspace_id: UUID,
        period_start: datetime,
        period_end: datetime,
        metric_codes: frozenset[str],
        platform_ids: frozenset[UUID],
        sort: str,
    ) -> tuple[PlatformAnalyticsRecord, ...]:
        """Return platform-level analytics aggregates."""

        account_counts = (
            await self._session.execute(
                select(
                    SocialAccount.platform_id,
                    SocialPlatform.code,
                    func.count(SocialAccount.id),
                )
                .join(SocialPlatform, SocialAccount.platform_id == SocialPlatform.id)
                .where(
                    SocialAccount.workspace_id == workspace_id,
                    SocialAccount.deleted_at.is_(None),
                    *(
                        (SocialAccount.platform_id.in_(tuple(platform_ids)),)
                        if platform_ids
                        else ()
                    ),
                )
                .group_by(SocialAccount.platform_id, SocialPlatform.code)
            )
        ).all()

        records: list[PlatformAnalyticsRecord] = []
        for platform_id, platform_code, account_count in account_counts:
            metrics = await self._aggregate_observation_metrics(
                workspace_id=workspace_id,
                period_start=period_start,
                period_end=period_end,
                platform_ids=frozenset({platform_id}),
                social_account_ids=frozenset(),
                metric_codes=metric_codes,
            )
            records.append(
                PlatformAnalyticsRecord(
                    platform_id=platform_id,
                    platform_code=str(platform_code),
                    account_count=int(account_count),
                    metrics=metrics,
                    fresh_through=utc_now(),
                )
            )

        reverse = sort.startswith("-")
        records.sort(key=lambda record: record.platform_code.lower(), reverse=reverse)
        return tuple(records)

    async def get_post_analytics(
        self,
        *,
        workspace_id: UUID,
        content_id: UUID,
        publication_target_id: UUID | None,
        period_start: datetime,
        period_end: datetime,
        metric_codes: frozenset[str],
    ) -> PostPerformanceRecord | None:
        """Return performance analytics for a single post/content asset."""

        statement = self._latest_snapshot_statement(
            workspace_id=workspace_id,
            period_start=period_start,
            period_end=period_end,
            platform_ids=frozenset(),
            social_account_ids=frozenset(),
        ).where(ContentPerformanceSnapshot.content_asset_id == content_id)
        if publication_target_id is not None:
            statement = statement.where(
                ContentPerformanceSnapshot.publication_target_id == publication_target_id
            )

        snapshot = (await self._session.scalars(statement)).first()
        if snapshot is None:
            return None
        return self._to_post_performance_record(snapshot, metric_codes)

    async def get_content_performance(
        self,
        *,
        workspace_id: UUID,
        content_id: UUID,
        period_start: datetime,
        period_end: datetime,
        metric_codes: frozenset[str],
    ) -> ContentPerformanceRecord | None:
        """Return aggregated performance for a content asset."""

        asset = await self._session.scalar(
            select(ContentAsset).where(
                ContentAsset.workspace_id == workspace_id,
                ContentAsset.id == content_id,
                ContentAsset.deleted_at.is_(None),
            )
        )
        if asset is None:
            return None

        snapshots = (
            await self._session.scalars(
                select(ContentPerformanceSnapshot)
                .where(
                    ContentPerformanceSnapshot.workspace_id == workspace_id,
                    ContentPerformanceSnapshot.content_asset_id == content_id,
                    ContentPerformanceSnapshot.snapshot_at >= period_start,
                    ContentPerformanceSnapshot.snapshot_at <= period_end,
                    ContentPerformanceSnapshot.deleted_at.is_(None),
                )
                .order_by(ContentPerformanceSnapshot.snapshot_at.desc())
            )
        ).all()
        if not snapshots:
            return None

        latest = snapshots[0]
        metrics = _merge_snapshot_metrics(list(snapshots), metric_codes)
        top_platform_code = await self._top_platform_code_for_content(
            workspace_id=workspace_id,
            content_id=content_id,
            period_start=period_start,
            period_end=period_end,
        )
        return ContentPerformanceRecord(
            content_id=content_id,
            title=asset.title,
            period_start=period_start,
            period_end=period_end,
            snapshot_at=latest.snapshot_at,
            top_platform_code=top_platform_code,
            metrics=metrics,
        )

    async def get_top_posts(self, criteria: TopPostsCriteria) -> PostPerformanceSearchPage:
        """Return ranked top-performing posts."""

        return await self._search_performance_snapshots(
            workspace_id=criteria.workspace_id,
            query=None,
            period_start=criteria.period_start,
            period_end=criteria.period_end,
            platform_ids=criteria.platform_ids,
            social_account_ids=criteria.social_account_ids,
            metric_codes=criteria.metric_codes,
            cursor=criteria.cursor,
            limit=criteria.limit,
            sort=criteria.sort,
        )

    async def compare_date_ranges(
        self,
        *,
        workspace_id: UUID,
        baseline_start: datetime,
        baseline_end: datetime,
        comparison_start: datetime,
        comparison_end: datetime,
        time_zone: str,
        metric_codes: frozenset[str],
        platform_ids: frozenset[UUID],
    ) -> DateRangeComparisonRecord:
        """Compare metrics across two date ranges."""

        baseline_metrics = await self._period_metrics(
            workspace_id=workspace_id,
            period_start=baseline_start,
            period_end=baseline_end,
            platform_ids=platform_ids,
            metric_codes=metric_codes,
        )
        comparison_metrics = await self._period_metrics(
            workspace_id=workspace_id,
            period_start=comparison_start,
            period_end=comparison_end,
            platform_ids=platform_ids,
            metric_codes=metric_codes,
        )
        record = DateRangeComparisonRecord(
            baseline=PeriodMetricsRecord(
                period_start=baseline_start,
                period_end=baseline_end,
                metrics=baseline_metrics,
            ),
            comparison=PeriodMetricsRecord(
                period_start=comparison_start,
                period_end=comparison_end,
                metrics=comparison_metrics,
            ),
            deltas=(),
            time_zone=time_zone,
            fresh_through=utc_now(),
        )
        return _enrich_comparison(record)

    async def search(self, criteria: AnalyticsSearchCriteria) -> PostPerformanceSearchPage:
        """Search analytics observations and post performance."""

        return await self._search_performance_snapshots(
            workspace_id=criteria.workspace_id,
            query=criteria.query,
            period_start=criteria.period_start,
            period_end=criteria.period_end,
            platform_ids=criteria.platform_ids,
            social_account_ids=criteria.social_account_ids,
            metric_codes=criteria.metric_codes,
            cursor=criteria.cursor,
            limit=criteria.limit,
            sort=criteria.sort,
        )

    async def get_summary(
        self,
        *,
        workspace_id: UUID,
        period_start: datetime,
        period_end: datetime,
        platform_ids: frozenset[UUID],
    ) -> AnalyticsSummaryRecord:
        """Return a high-level analytics summary for the workspace."""

        snapshot = await self._find_workspace_kpi_snapshot(
            workspace_id=workspace_id,
            period_start=period_start,
            period_end=period_end,
            platform_ids=platform_ids,
        )
        if snapshot is not None:
            metrics = _metrics_from_snapshot(snapshot.metrics)
            return AnalyticsSummaryRecord(
                period_start=snapshot.period_start,
                period_end=snapshot.period_end,
                total_posts=_metric_int(metrics, "totalPosts") or 0,
                total_reach=_metric_int(metrics, "reach"),
                total_engagements=_metric_int(metrics, "engagements"),
                platforms_active=_metric_int(metrics, "platformsActive") or 0,
                fresh_through=snapshot.fresh_through,
                methodology_version=snapshot.methodology_version,
                metrics=metrics,
            )

        latest_targets = self._latest_snapshot_subquery(
            workspace_id=workspace_id,
            period_start=period_start,
            period_end=period_end,
            platform_ids=platform_ids,
            social_account_ids=frozenset(),
        )
        totals = await self._session.execute(
            select(
                func.count(ContentPerformanceSnapshot.id),
                func.coalesce(func.sum(ContentPerformanceSnapshot.reach), 0),
                func.coalesce(func.sum(ContentPerformanceSnapshot.engagements), 0),
                func.count(func.distinct(PublicationTarget.platform_id)),
            )
            .select_from(ContentPerformanceSnapshot)
            .join(
                latest_targets,
                and_(
                    ContentPerformanceSnapshot.publication_target_id
                    == latest_targets.c.publication_target_id,
                    ContentPerformanceSnapshot.snapshot_at == latest_targets.c.max_snapshot_at,
                ),
            )
            .join(
                PublicationTarget,
                and_(
                    PublicationTarget.workspace_id == ContentPerformanceSnapshot.workspace_id,
                    PublicationTarget.id == ContentPerformanceSnapshot.publication_target_id,
                ),
            )
            .where(ContentPerformanceSnapshot.workspace_id == workspace_id)
        )
        row = totals.one()
        metrics = await self._aggregate_observation_metrics(
            workspace_id=workspace_id,
            period_start=period_start,
            period_end=period_end,
            platform_ids=platform_ids,
            social_account_ids=frozenset(),
            metric_codes=frozenset(),
        )
        return AnalyticsSummaryRecord(
            period_start=period_start,
            period_end=period_end,
            total_posts=int(row[0]),
            total_reach=int(row[1]) if row[1] else None,
            total_engagements=int(row[2]) if row[2] else None,
            platforms_active=int(row[3]),
            fresh_through=utc_now(),
            methodology_version=_DEFAULT_METHODOLOGY_VERSION,
            metrics=metrics,
        )

    async def validate_platform_ids(
        self,
        *,
        workspace_id: UUID,
        platform_ids: frozenset[UUID],
    ) -> bool:
        """Return whether all platform identifiers belong to the workspace."""

        if not platform_ids:
            return True

        matched = await self._session.scalar(
            select(func.count(func.distinct(SocialAccount.platform_id))).where(
                SocialAccount.workspace_id == workspace_id,
                SocialAccount.platform_id.in_(tuple(platform_ids)),
                SocialAccount.deleted_at.is_(None),
            )
        )
        return matched == len(platform_ids)

    async def estimate_export_rows(
        self,
        *,
        workspace_id: UUID,
        period_start: datetime,
        period_end: datetime,
        platform_ids: frozenset[UUID],
        export_type: str,
    ) -> int:
        """Estimate row count for an export request."""

        _ = export_type
        statement = (
            select(func.count())
            .select_from(MetricObservation)
            .where(
                MetricObservation.workspace_id == workspace_id,
                MetricObservation.observed_at >= period_start,
                MetricObservation.observed_at <= period_end,
                MetricObservation.deleted_at.is_(None),
            )
        )
        if platform_ids:
            statement = statement.join(
                SocialAccount,
                MetricObservation.social_account_id == SocialAccount.id,
            ).where(
                SocialAccount.workspace_id == workspace_id,
                SocialAccount.platform_id.in_(tuple(platform_ids)),
            )
        return int(await self._session.scalar(statement) or 0)

    async def request_export(self, export_request: NewAnalyticsExport) -> AnalyticsExportRecord:
        """Persist an analytics export request."""

        now = utc_now()
        export_id = uuid4()
        data_export = DataExport(
            id=export_id,
            workspace_id=export_request.workspace_id,
            requested_by=export_request.requested_by,
            export_type=DataExportType.WORKSPACE_EXPORT,
            state=DataExportState.QUEUED,
            requested_at=now,
            created_by=export_request.requested_by,
            updated_by=export_request.requested_by,
        )
        await self._exports.create(data_export)

        payload = {
            "export_type": export_request.export_type,
            "format": export_request.format.value,
            "period_start": export_request.period_start.isoformat(),
            "period_end": export_request.period_end.isoformat(),
            "platform_ids": [str(platform_id) for platform_id in export_request.platform_ids],
            "metric_codes": sorted(export_request.metric_codes),
            "row_estimate": export_request.row_estimate,
        }
        job = BackgroundJob(
            workspace_id=export_request.workspace_id,
            job_type=f"analytics_export.{export_request.export_type}",
            queue_name="maintenance",
            state=JobState.QUEUED,
            resource_type="data_export",
            resource_id=export_id,
            idempotency_key=json.dumps(payload, separators=(",", ":"), sort_keys=True),
            available_at=now,
            created_by=export_request.requested_by,
            updated_by=export_request.requested_by,
        )
        self._session.add(job)
        await self._session.flush()
        await self._session.refresh(job)

        return AnalyticsExportRecord(
            id=export_id,
            workspace_id=export_request.workspace_id,
            export_type=export_request.export_type,
            status=ExportStatus.QUEUED,
            format=export_request.format,
            period_start=export_request.period_start,
            period_end=export_request.period_end,
            requested_at=now,
            requested_by=export_request.requested_by,
            row_estimate=export_request.row_estimate,
        )

    async def refresh_dashboard_cache(
        self,
        refresh_request: RefreshDashboardCacheInput,
    ) -> DashboardCacheRefreshRecord:
        """Refresh cached dashboard aggregates."""

        metrics = await self._aggregate_observation_metrics(
            workspace_id=refresh_request.workspace_id,
            period_start=refresh_request.period_start,
            period_end=refresh_request.period_end,
            platform_ids=refresh_request.platform_ids,
            social_account_ids=frozenset(),
            metric_codes=frozenset(),
        )
        metrics_payload = {
            metric.code: {
                "value": metric.value,
                "unit": metric.unit,
                "is_estimated": metric.is_estimated,
            }
            for metric in metrics
        }
        dimensions = _platform_dimensions(refresh_request.platform_ids)
        existing = await self._find_workspace_kpi_snapshot(
            workspace_id=refresh_request.workspace_id,
            period_start=refresh_request.period_start,
            period_end=refresh_request.period_end,
            platform_ids=refresh_request.platform_ids,
        )
        if existing is None:
            snapshot = AnalyticsSnapshot(
                workspace_id=refresh_request.workspace_id,
                snapshot_type="workspace_kpi",
                period_start=refresh_request.period_start,
                period_end=refresh_request.period_end,
                time_zone=refresh_request.time_zone,
                dimensions=dimensions,
                metrics=metrics_payload,
                fresh_through=utc_now(),
                methodology_version=_DEFAULT_METHODOLOGY_VERSION,
                created_by=refresh_request.refreshed_by,
                updated_by=refresh_request.refreshed_by,
            )
            await self._snapshots.create(snapshot)
            snapshot_count = 1
        else:
            snapshot_count = 1

        return DashboardCacheRefreshRecord(
            workspace_id=refresh_request.workspace_id,
            refreshed_at=utc_now(),
            snapshot_count=snapshot_count,
        )

    async def archive_snapshot(
        self,
        archive_request: NewArchivedSnapshot,
    ) -> ArchivedSnapshotRecord:
        """Archive an analytics snapshot."""

        source = await self._session.scalar(
            select(AnalyticsSnapshot).where(
                AnalyticsSnapshot.workspace_id == archive_request.workspace_id,
                AnalyticsSnapshot.id == archive_request.snapshot_id,
                AnalyticsSnapshot.deleted_at.is_(None),
            )
        )
        if source is None:
            raise AnalyticsSnapshotNotFoundError(
                detail=f"Analytics snapshot {archive_request.snapshot_id} was not found."
            )

        archived_at = utc_now()
        archive_reference = AnalyticsSnapshot(
            workspace_id=archive_request.workspace_id,
            snapshot_type=source.snapshot_type,
            period_start=source.period_start,
            period_end=source.period_end,
            time_zone=source.time_zone,
            dimensions={
                **_as_str_dict(source.dimensions),
                "archive_reference": True,
                "source_snapshot_id": str(source.id),
                "archived_at": archived_at.isoformat(),
                "archived_by": str(archive_request.archived_by),
            },
            metrics=source.metrics,
            fresh_through=source.fresh_through,
            methodology_version=source.methodology_version,
            created_by=archive_request.archived_by,
            updated_by=archive_request.archived_by,
        )
        self._session.add(archive_reference)
        await self._session.flush()

        return ArchivedSnapshotRecord(
            id=source.id,
            workspace_id=archive_request.workspace_id,
            archived_at=archived_at,
            archived_by=archive_request.archived_by,
        )

    async def import_observations(
        self,
        import_request: NewAnalyticsImport,
    ) -> AnalyticsImportRecord:
        """Persist imported analytics observations."""

        definitions = await self._load_metric_definitions(
            codes=frozenset(observation.code for observation in import_request.observations)
        )
        missing = {
            observation.code
            for observation in import_request.observations
            if observation.code not in definitions
        }
        if missing:
            codes = ", ".join(sorted(missing))
            raise EntityNotFound(f"Metric definitions not found for codes: {codes}.")

        imported_at = utc_now()
        batch_id = uuid4()
        entities: list[MetricObservation] = []
        for index, observation in enumerate(import_request.observations):
            definition = definitions[observation.code]
            fingerprint_source = (
                f"{import_request.workspace_id}:{batch_id}:{index}:{observation.code}:"
                f"{observation.value}:{import_request.period_start.isoformat()}:"
                f"{import_request.period_end.isoformat()}"
            ).encode()
            entities.append(
                MetricObservation(
                    workspace_id=import_request.workspace_id,
                    metric_definition_id=definition.id,
                    social_account_id=None,
                    publication_target_id=None,
                    content_asset_id=None,
                    observed_at=imported_at,
                    bucket_start=import_request.period_start,
                    bucket_end=import_request.period_end,
                    value=Decimal(observation.value),
                    currency=None,
                    is_estimated=observation.is_estimated,
                    source_fingerprint=hashlib.sha256(fingerprint_source).digest(),
                    provider_fragment={
                        "import_batch_id": str(batch_id),
                        "platform_id": (
                            str(import_request.platform_id)
                            if import_request.platform_id is not None
                            else None
                        ),
                    },
                    created_by=import_request.imported_by,
                    updated_by=import_request.imported_by,
                )
            )

        self._session.add_all(entities)
        await self._session.flush()
        return AnalyticsImportRecord(
            id=batch_id,
            workspace_id=import_request.workspace_id,
            imported_at=imported_at,
            observation_count=len(entities),
        )

    async def _period_metrics(
        self,
        *,
        workspace_id: UUID,
        period_start: datetime,
        period_end: datetime,
        platform_ids: frozenset[UUID],
        metric_codes: frozenset[str],
    ) -> tuple[MetricValueRecord, ...]:
        snapshot = await self._find_workspace_kpi_snapshot(
            workspace_id=workspace_id,
            period_start=period_start,
            period_end=period_end,
            platform_ids=platform_ids,
        )
        if snapshot is not None:
            return _filter_metrics(_metrics_from_snapshot(snapshot.metrics), metric_codes)
        return await self._aggregate_observation_metrics(
            workspace_id=workspace_id,
            period_start=period_start,
            period_end=period_end,
            platform_ids=platform_ids,
            social_account_ids=frozenset(),
            metric_codes=metric_codes,
        )

    async def _find_workspace_kpi_snapshot(
        self,
        *,
        workspace_id: UUID,
        period_start: datetime,
        period_end: datetime,
        platform_ids: frozenset[UUID],
    ) -> AnalyticsSnapshot | None:
        dimensions = _platform_dimensions(platform_ids)
        statement = (
            select(AnalyticsSnapshot)
            .where(
                AnalyticsSnapshot.workspace_id == workspace_id,
                AnalyticsSnapshot.snapshot_type == "workspace_kpi",
                AnalyticsSnapshot.period_start == period_start,
                AnalyticsSnapshot.period_end == period_end,
                AnalyticsSnapshot.dimensions == dimensions,
                AnalyticsSnapshot.deleted_at.is_(None),
                ~AnalyticsSnapshot.dimensions.has_key("archive_reference"),
            )
            .order_by(AnalyticsSnapshot.fresh_through.desc(), AnalyticsSnapshot.id.desc())
            .limit(1)
        )
        return (await self._session.scalars(statement)).first()

    async def _aggregate_observation_metrics(
        self,
        *,
        workspace_id: UUID,
        period_start: datetime,
        period_end: datetime,
        platform_ids: frozenset[UUID],
        social_account_ids: frozenset[UUID],
        metric_codes: frozenset[str],
    ) -> tuple[MetricValueRecord, ...]:
        statement = (
            select(
                MetricDefinition.code,
                MetricDefinition.unit,
                func.coalesce(func.sum(MetricObservation.value), 0),
                func.bool_or(MetricObservation.is_estimated),
            )
            .join(
                MetricDefinition,
                MetricObservation.metric_definition_id == MetricDefinition.id,
            )
            .where(
                MetricObservation.workspace_id == workspace_id,
                MetricObservation.observed_at >= period_start,
                MetricObservation.observed_at <= period_end,
                MetricObservation.deleted_at.is_(None),
            )
            .group_by(MetricDefinition.code, MetricDefinition.unit)
            .order_by(MetricDefinition.code)
        )
        if platform_ids or social_account_ids:
            statement = statement.outerjoin(
                SocialAccount,
                MetricObservation.social_account_id == SocialAccount.id,
            )
            if platform_ids:
                statement = statement.where(
                    or_(
                        SocialAccount.platform_id.in_(tuple(platform_ids)),
                        MetricObservation.social_account_id.is_(None),
                    )
                )
            if social_account_ids:
                statement = statement.where(
                    MetricObservation.social_account_id.in_(tuple(social_account_ids))
                )

        rows = (await self._session.execute(statement)).all()
        metrics = tuple(
            MetricValueRecord(
                code=str(code),
                value=_decimal_to_str(value),
                unit=str(unit),
                is_estimated=bool(is_estimated),
            )
            for code, unit, value, is_estimated in rows
        )
        return _filter_metrics(metrics, metric_codes)

    async def _search_performance_snapshots(
        self,
        *,
        workspace_id: UUID,
        query: str | None,
        period_start: datetime,
        period_end: datetime,
        platform_ids: frozenset[UUID],
        social_account_ids: frozenset[UUID],
        metric_codes: frozenset[str],
        cursor: str | None,
        limit: int,
        sort: str,
    ) -> PostPerformanceSearchPage:
        sort_column = _normalize_post_sort(sort)
        statement = self._latest_snapshot_statement(
            workspace_id=workspace_id,
            period_start=period_start,
            period_end=period_end,
            platform_ids=platform_ids,
            social_account_ids=social_account_ids,
        )
        if query:
            statement = statement.join(
                ContentAsset,
                and_(
                    ContentAsset.workspace_id == ContentPerformanceSnapshot.workspace_id,
                    ContentAsset.id == ContentPerformanceSnapshot.content_asset_id,
                ),
            ).where(ContentAsset.title.ilike(f"%{query.strip()}%"))

        statement = apply_keyset_pagination(
            statement,
            ContentPerformanceSnapshot,
            sort_column=sort_column,
            cursor=cursor,
            limit=limit,
        )
        snapshots = (await self._session.scalars(statement)).all()
        snapshot_list = list(snapshots)
        page_snapshots, next_cursor, has_more = build_keyset_page(
            snapshot_list,
            limit=limit,
            sort_column=sort_column,
            sort_value_getter=lambda snapshot: _snapshot_sort_value(snapshot, sort_column.name),
            id_getter=lambda snapshot: snapshot.id,
        )
        items = tuple(
            self._to_post_performance_record(snapshot, metric_codes) for snapshot in page_snapshots
        )
        return PostPerformanceSearchPage(
            items=items,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    def _latest_snapshot_subquery(
        self,
        *,
        workspace_id: UUID,
        period_start: datetime,
        period_end: datetime,
        platform_ids: frozenset[UUID],
        social_account_ids: frozenset[UUID],
    ) -> Any:
        statement = (
            select(
                ContentPerformanceSnapshot.publication_target_id,
                func.max(ContentPerformanceSnapshot.snapshot_at).label("max_snapshot_at"),
            )
            .where(
                ContentPerformanceSnapshot.workspace_id == workspace_id,
                ContentPerformanceSnapshot.snapshot_at >= period_start,
                ContentPerformanceSnapshot.snapshot_at <= period_end,
                ContentPerformanceSnapshot.deleted_at.is_(None),
            )
            .group_by(ContentPerformanceSnapshot.publication_target_id)
        )
        if platform_ids or social_account_ids:
            statement = statement.join(
                PublicationTarget,
                and_(
                    PublicationTarget.workspace_id == ContentPerformanceSnapshot.workspace_id,
                    PublicationTarget.id == ContentPerformanceSnapshot.publication_target_id,
                ),
            )
            if platform_ids:
                statement = statement.where(PublicationTarget.platform_id.in_(tuple(platform_ids)))
            if social_account_ids:
                statement = statement.where(
                    PublicationTarget.social_account_id.in_(tuple(social_account_ids))
                )
        return statement.subquery()

    def _latest_snapshot_statement(
        self,
        *,
        workspace_id: UUID,
        period_start: datetime,
        period_end: datetime,
        platform_ids: frozenset[UUID],
        social_account_ids: frozenset[UUID],
    ) -> Any:
        latest = self._latest_snapshot_subquery(
            workspace_id=workspace_id,
            period_start=period_start,
            period_end=period_end,
            platform_ids=platform_ids,
            social_account_ids=social_account_ids,
        )
        return (
            select(ContentPerformanceSnapshot)
            .join(
                latest,
                and_(
                    ContentPerformanceSnapshot.publication_target_id
                    == latest.c.publication_target_id,
                    ContentPerformanceSnapshot.snapshot_at == latest.c.max_snapshot_at,
                ),
            )
            .where(ContentPerformanceSnapshot.workspace_id == workspace_id)
        )

    async def _top_platform_code_for_content(
        self,
        *,
        workspace_id: UUID,
        content_id: UUID,
        period_start: datetime,
        period_end: datetime,
    ) -> str | None:
        platform = aliased(SocialPlatform)
        row = (
            await self._session.execute(
                select(
                    platform.code,
                    func.coalesce(func.sum(ContentPerformanceSnapshot.engagements), 0),
                )
                .select_from(ContentPerformanceSnapshot)
                .join(
                    PublicationTarget,
                    and_(
                        PublicationTarget.workspace_id == ContentPerformanceSnapshot.workspace_id,
                        PublicationTarget.id == ContentPerformanceSnapshot.publication_target_id,
                    ),
                )
                .join(platform, PublicationTarget.platform_id == platform.id)
                .where(
                    ContentPerformanceSnapshot.workspace_id == workspace_id,
                    ContentPerformanceSnapshot.content_asset_id == content_id,
                    ContentPerformanceSnapshot.snapshot_at >= period_start,
                    ContentPerformanceSnapshot.snapshot_at <= period_end,
                    ContentPerformanceSnapshot.deleted_at.is_(None),
                )
                .group_by(platform.code)
                .order_by(func.coalesce(func.sum(ContentPerformanceSnapshot.engagements), 0).desc())
                .limit(1)
            )
        ).first()
        return str(row[0]) if row is not None else None

    async def _load_metric_definitions(
        self,
        *,
        codes: frozenset[str],
    ) -> dict[str, MetricDefinition]:
        if not codes:
            return {}

        rows = (
            await self._session.scalars(
                select(MetricDefinition)
                .where(
                    MetricDefinition.code.in_(tuple(codes)),
                    MetricDefinition.deleted_at.is_(None),
                )
                .order_by(MetricDefinition.code, MetricDefinition.methodology_version.desc())
            )
        ).all()
        definitions: dict[str, MetricDefinition] = {}
        for row in rows:
            definitions.setdefault(row.code, row)
        return definitions

    @staticmethod
    def _to_post_performance_record(
        snapshot: ContentPerformanceSnapshot,
        metric_codes: frozenset[str],
    ) -> PostPerformanceRecord:
        metrics = _filter_metrics(_metrics_from_snapshot(snapshot.metrics), metric_codes)
        engagement_rate = (
            _decimal_to_str(snapshot.engagement_rate)
            if snapshot.engagement_rate is not None
            else None
        )
        return PostPerformanceRecord(
            content_id=snapshot.content_asset_id,
            publication_target_id=snapshot.publication_target_id,
            snapshot_at=snapshot.snapshot_at,
            reach=snapshot.reach,
            engagements=snapshot.engagements,
            clicks=snapshot.clicks,
            conversions=snapshot.conversions,
            engagement_rate=engagement_rate,
            metrics=metrics,
        )


def _platform_dimensions(platform_ids: frozenset[UUID]) -> dict[str, Any]:
    if not platform_ids:
        return {}
    return {"platform_ids": sorted(str(platform_id) for platform_id in platform_ids)}


def _as_str_dict(value: dict[str, Any]) -> dict[str, Any]:
    return {str(key): value for key, value in value.items()}


def _metrics_from_snapshot(raw: dict[str, Any]) -> tuple[MetricValueRecord, ...]:
    records: list[MetricValueRecord] = []
    for code, value in raw.items():
        if isinstance(value, dict):
            records.append(
                MetricValueRecord(
                    code=str(code),
                    value=str(value.get("value", "0")),
                    unit=str(value.get("unit", "count")),
                    is_estimated=bool(value.get("is_estimated", False)),
                )
            )
        else:
            records.append(
                MetricValueRecord(
                    code=str(code),
                    value=str(value),
                    unit="count",
                    is_estimated=False,
                )
            )
    return tuple(records)


def _merge_snapshot_metrics(
    snapshots: Sequence[ContentPerformanceSnapshot],
    metric_codes: frozenset[str],
) -> tuple[MetricValueRecord, ...]:
    totals: dict[str, Decimal] = {}
    units: dict[str, str] = {}
    estimated: dict[str, bool] = {}
    for snapshot in snapshots:
        for metric in _metrics_from_snapshot(snapshot.metrics):
            totals[metric.code] = totals.get(metric.code, Decimal(0)) + Decimal(metric.value)
            units[metric.code] = metric.unit
            estimated[metric.code] = estimated.get(metric.code, False) or metric.is_estimated
    metrics = tuple(
        MetricValueRecord(
            code=code,
            value=_decimal_to_str(total),
            unit=units[code],
            is_estimated=estimated[code],
        )
        for code, total in sorted(totals.items())
    )
    return _filter_metrics(metrics, metric_codes)


def _filter_metrics(
    metrics: tuple[MetricValueRecord, ...],
    metric_codes: frozenset[str],
) -> tuple[MetricValueRecord, ...]:
    if not metric_codes:
        return metrics
    return tuple(metric for metric in metrics if metric.code in metric_codes)


def _change_percent(baseline_value: str, comparison_value: str) -> str | None:
    try:
        baseline = Decimal(baseline_value)
        comparison = Decimal(comparison_value)
    except InvalidOperation:
        return None
    if baseline == 0:
        return None if comparison == 0 else "100"
    change = ((comparison - baseline) / baseline) * Decimal(100)
    return format(change.quantize(Decimal("0.01")), "f")


def _compute_deltas(
    baseline: PeriodMetricsRecord,
    comparison: PeriodMetricsRecord,
) -> tuple[MetricDeltaRecord, ...]:
    baseline_by_code = {metric.code: metric for metric in baseline.metrics}
    comparison_by_code = {metric.code: metric for metric in comparison.metrics}
    all_codes = sorted(set(baseline_by_code) | set(comparison_by_code))

    deltas: list[MetricDeltaRecord] = []
    for code in all_codes:
        baseline_metric = baseline_by_code.get(code)
        comparison_metric = comparison_by_code.get(code)
        baseline_value = baseline_metric.value if baseline_metric else "0"
        comparison_value = comparison_metric.value if comparison_metric else "0"
        reference_metric = baseline_metric or comparison_metric
        unit = reference_metric.unit if reference_metric is not None else "count"
        is_estimated = bool(
            (baseline_metric and baseline_metric.is_estimated)
            or (comparison_metric and comparison_metric.is_estimated)
        )
        deltas.append(
            MetricDeltaRecord(
                code=code,
                unit=unit,
                baseline_value=baseline_value,
                comparison_value=comparison_value,
                change_percent=_change_percent(baseline_value, comparison_value),
                is_estimated=is_estimated,
            )
        )
    return tuple(deltas)


def _enrich_comparison(record: DateRangeComparisonRecord) -> DateRangeComparisonRecord:
    deltas = _compute_deltas(record.baseline, record.comparison)
    return DateRangeComparisonRecord(
        baseline=record.baseline,
        comparison=record.comparison,
        deltas=deltas,
        time_zone=record.time_zone,
        fresh_through=record.fresh_through,
    )


def _metric_int(metrics: tuple[MetricValueRecord, ...], code: str) -> int | None:
    for metric in metrics:
        if metric.code == code:
            try:
                return int(Decimal(metric.value))
            except Exception:
                return None
    return None


def _decimal_to_str(value: Any) -> str:
    if isinstance(value, Decimal):
        return format(value, "f")
    return str(value)


def _normalize_post_sort(sort: str) -> SortColumn:
    token = sort.strip() if sort.strip() else "-engagements"
    descending = token.startswith("-")
    field = token[1:] if descending else token
    mapped = _POST_SORT_FIELD_MAP.get(field)
    if mapped is None:
        raise EntityNotFound(f"Unsupported sort column: {field}")
    return SortColumn(
        name=mapped,
        direction=SortDirection.DESC if descending else SortDirection.ASC,
    )


def _snapshot_sort_value(snapshot: ContentPerformanceSnapshot, column_name: str) -> Any:
    if column_name == "engagement_rate":
        return _decimal_to_str(snapshot.engagement_rate) if snapshot.engagement_rate else "0"
    if column_name == "snapshot_at":
        return snapshot.snapshot_at
    value = getattr(snapshot, column_name, None)
    return value if value is not None else 0
