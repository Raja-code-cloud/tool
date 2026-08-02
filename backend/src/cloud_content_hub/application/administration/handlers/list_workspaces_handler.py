"""List workspaces query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.administration.dto.responses import WorkspaceSummaryResponse
from cloud_content_hub.application.administration.interfaces.administration_repository import (
    IAdministrationRepository,
    WorkspaceSearchCriteria,
)
from cloud_content_hub.application.administration.mappers.administration_mapper import (
    AdministrationMapper,
)
from cloud_content_hub.application.administration.queries import ListWorkspacesQuery
from cloud_content_hub.application.administration.validators.administration_validator import (
    is_global_admin,
    require_admin_read,
    validate_workspace_admin_scope,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.dto.base import PagedResultDto, PageInfoDto
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class ListWorkspacesHandler:
    """Lists workspaces within an administrative scope."""

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
        query: ListWorkspacesQuery,
    ) -> PagedResultDto[WorkspaceSummaryResponse]:
        require_admin_read(actor)
        workspace_id = query.workspace_id
        if workspace_id is not None:
            validate_workspace_admin_scope(actor, workspace_id=workspace_id)
        elif not is_global_admin(actor):
            workspace_id = actor.workspace_id

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._administration_repository_factory(unit_of_work)
            page = await repository.list_workspaces(
                WorkspaceSearchCriteria(
                    organization_id=query.organization_id,
                    workspace_id=workspace_id,
                    query=query.query,
                    statuses=query.statuses,
                    cursor=query.cursor,
                    limit=query.limit,
                    sort=query.sort,
                )
            )

        items = tuple(
            AdministrationMapper.to_workspace_summary_dto(record) for record in page.items
        )
        return PagedResultDto(
            items=items,
            page=PageInfoDto(
                next_cursor=page.next_cursor, has_more=page.has_more, limit=query.limit
            ),
        )
