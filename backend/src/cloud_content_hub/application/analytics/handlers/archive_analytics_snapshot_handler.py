"""Archive analytics snapshot command handler."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from cloud_content_hub.application.analytics.commands import ArchiveAnalyticsSnapshotCommand
from cloud_content_hub.application.analytics.events import AnalyticsSnapshotArchived
from cloud_content_hub.application.analytics.interfaces.analytics_repository import (
    IAnalyticsRepository,
    NewArchivedSnapshot,
)
from cloud_content_hub.application.analytics.interfaces.event_publisher import (
    IAnalyticsEventPublisher,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


@dataclass(frozen=True, slots=True)
class ArchiveAnalyticsSnapshotResult:
    """Result of archiving an analytics snapshot."""

    snapshot_id: UUID
    archived_at: datetime


class ArchiveAnalyticsSnapshotHandler:
    """Orchestrates analytics snapshot archival."""

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
        command: ArchiveAnalyticsSnapshotCommand,
    ) -> ArchiveAnalyticsSnapshotResult:
        require_permission(actor, "analytics:read")

        async with self._unit_of_work_factory() as unit_of_work:
            analytics_repository = self._analytics_repository_factory(unit_of_work)
            archived = await analytics_repository.archive_snapshot(
                NewArchivedSnapshot(
                    workspace_id=actor.workspace_id,
                    snapshot_id=command.snapshot_id,
                    archived_by=actor.user_id,
                )
            )
            await self._event_publisher.publish(
                AnalyticsSnapshotArchived(
                    workspace_id=actor.workspace_id,
                    snapshot_id=archived.id,
                    actor_id=actor.user_id,
                    occurred_at=datetime.now(tz=UTC),
                ),
                unit_of_work=unit_of_work,
            )
            await unit_of_work.flush()

        return ArchiveAnalyticsSnapshotResult(
            snapshot_id=archived.id,
            archived_at=archived.archived_at,
        )
