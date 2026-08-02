"""Get audit summary query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.administration.dto.responses import AuditSummaryResponse
from cloud_content_hub.application.administration.interfaces.administration_repository import (
    AuditSearchCriteria,
    IAdministrationRepository,
)
from cloud_content_hub.application.administration.mappers.administration_mapper import (
    AdministrationMapper,
)
from cloud_content_hub.application.administration.queries import GetAuditSummaryQuery
from cloud_content_hub.application.administration.validators.administration_validator import (
    is_global_admin,
    require_admin_read,
    validate_workspace_admin_scope,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class GetAuditSummaryHandler:
    """Retrieves aggregated audit evidence."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        administration_repository_factory: Callable[[IUnitOfWork], IAdministrationRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._administration_repository_factory = administration_repository_factory

    async def handle(
        self,
        actor: ActorContext,
        query: GetAuditSummaryQuery,
    ) -> AuditSummaryResponse:
        require_admin_read(actor)
        workspace_id = query.workspace_id
        if workspace_id is not None:
            validate_workspace_admin_scope(actor, workspace_id=workspace_id)
        elif not is_global_admin(actor):
            workspace_id = actor.workspace_id

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._administration_repository_factory(unit_of_work)
            summary = await repository.get_audit_summary(
                AuditSearchCriteria(
                    workspace_id=workspace_id,
                    organization_id=query.organization_id,
                    actions=query.actions,
                    outcomes=query.outcomes,
                    occurred_after=query.occurred_after,
                    occurred_before=query.occurred_before,
                    limit=query.limit,
                )
            )

        return AdministrationMapper.to_audit_summary_dto(summary)
