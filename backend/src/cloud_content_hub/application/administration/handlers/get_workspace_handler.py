"""Get current workspace query handler."""

from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

from cloud_content_hub.application.administration.dto.responses import WorkspaceSummaryResponse
from cloud_content_hub.application.administration.interfaces.administration_repository import (
    IAdministrationRepository,
)
from cloud_content_hub.application.administration.mappers.administration_mapper import (
    AdministrationMapper,
)
from cloud_content_hub.application.administration.validators.administration_validator import (
    validate_workspace_exists,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class GetWorkspaceHandler:
    """Retrieves the current workspace summary."""

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
        *,
        workspace_id: UUID,
    ) -> WorkspaceSummaryResponse:
        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._administration_repository_factory(unit_of_work)
            workspace = await repository.get_workspace(workspace_id)

        validate_workspace_exists(workspace, workspace_id=workspace_id)
        assert workspace is not None
        return AdministrationMapper.to_workspace_summary_dto(workspace)
