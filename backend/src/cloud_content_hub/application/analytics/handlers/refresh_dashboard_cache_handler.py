"""Refresh dashboard cache command handler."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime

from cloud_content_hub.application.analytics.commands import RefreshDashboardCacheCommand
from cloud_content_hub.application.analytics.events import DashboardCacheRefreshed
from cloud_content_hub.application.analytics.interfaces.analytics_repository import (
    IAnalyticsRepository,
    RefreshDashboardCacheInput,
)
from cloud_content_hub.application.analytics.interfaces.event_publisher import (
    IAnalyticsEventPublisher,
)
from cloud_content_hub.application.analytics.validators.analytics_validator import (
    validate_platform_selection,
    validate_refresh_cache_request,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


@dataclass(frozen=True, slots=True)
class RefreshDashboardCacheResult:
    """Result of a dashboard cache refresh command."""

    snapshot_count: int
    refreshed_at: datetime


class RefreshDashboardCacheHandler:
    """Orchestrates dashboard cache refresh."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        analytics_repository_factory: Callable[[IUnitOfWork], IAnalyticsRepository],
        event_publisher: IAnalyticsEventPublisher,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._analytics_repository_factory = analytics_repository_factory
        self._event_publisher = event_publisher

    async def handle(
        self,
        actor: ActorContext,
        command: RefreshDashboardCacheCommand,
    ) -> RefreshDashboardCacheResult:
        require_permission(actor, "analytics:read")
        validate_refresh_cache_request(command.request)
        platform_ids = frozenset(command.request.platform_ids)

        async with self._unit_of_work_factory() as unit_of_work:
            analytics_repository = self._analytics_repository_factory(unit_of_work)
            if platform_ids:
                platforms_valid = await analytics_repository.validate_platform_ids(
                    workspace_id=actor.workspace_id,
                    platform_ids=platform_ids,
                )
                validate_platform_selection(
                    platform_ids=platform_ids,
                    platforms_valid=platforms_valid,
                )
            refreshed = await analytics_repository.refresh_dashboard_cache(
                RefreshDashboardCacheInput(
                    workspace_id=actor.workspace_id,
                    period_start=command.request.period_start,
                    period_end=command.request.period_end,
                    time_zone=command.request.time_zone,
                    platform_ids=platform_ids,
                    refreshed_by=actor.user_id,
                )
            )
            await self._event_publisher.publish(
                DashboardCacheRefreshed(
                    workspace_id=actor.workspace_id,
                    actor_id=actor.user_id,
                    snapshot_count=refreshed.snapshot_count,
                    occurred_at=datetime.now(tz=UTC),
                ),
                unit_of_work=unit_of_work,
            )
            await unit_of_work.flush()

        return RefreshDashboardCacheResult(
            snapshot_count=refreshed.snapshot_count,
            refreshed_at=refreshed.refreshed_at,
        )
