"""Import analytics command handler."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

from cloud_content_hub.application.analytics.commands import ImportAnalyticsCommand
from cloud_content_hub.application.analytics.interfaces.analytics_repository import (
    IAnalyticsRepository,
    MetricValueRecord,
    NewAnalyticsImport,
)
from cloud_content_hub.application.analytics.validators.analytics_validator import (
    validate_import_request,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


@dataclass(frozen=True, slots=True)
class ImportAnalyticsResult:
    """Result of an analytics import command."""

    import_id: UUID
    observation_count: int


class ImportAnalyticsHandler:
    """Orchestrates analytics observation import."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        analytics_repository_factory: Callable[[IUnitOfWork], IAnalyticsRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._analytics_repository_factory = analytics_repository_factory

    async def handle(
        self,
        actor: ActorContext,
        command: ImportAnalyticsCommand,
    ) -> ImportAnalyticsResult:
        require_permission(actor, "analytics:read")
        validate_import_request(command.request)

        async with self._unit_of_work_factory() as unit_of_work:
            analytics_repository = self._analytics_repository_factory(unit_of_work)
            imported = await analytics_repository.import_observations(
                NewAnalyticsImport(
                    workspace_id=actor.workspace_id,
                    platform_id=command.request.platform_id,
                    period_start=command.request.period_start,
                    period_end=command.request.period_end,
                    observations=tuple(
                        MetricValueRecord(
                            code=observation.code,
                            value=observation.value,
                            unit=observation.unit,
                            is_estimated=observation.is_estimated,
                        )
                        for observation in command.request.observations
                    ),
                    imported_by=actor.user_id,
                )
            )
            await unit_of_work.flush()

        return ImportAnalyticsResult(
            import_id=imported.id,
            observation_count=imported.observation_count,
        )
