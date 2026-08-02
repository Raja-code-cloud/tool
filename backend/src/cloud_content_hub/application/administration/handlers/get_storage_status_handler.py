"""Get storage status query handler."""

from __future__ import annotations

from cloud_content_hub.application.administration.dto.responses import StorageStatusResponse
from cloud_content_hub.application.administration.interfaces.storage_status_port import (
    IStorageStatusPort,
)
from cloud_content_hub.application.administration.mappers.administration_mapper import (
    AdministrationMapper,
)
from cloud_content_hub.application.administration.queries import GetStorageStatusQuery
from cloud_content_hub.application.administration.validators.administration_validator import (
    is_global_admin,
    require_admin_read,
    validate_workspace_admin_scope,
)
from cloud_content_hub.application.shared.actor import ActorContext


class GetStorageStatusHandler:
    """Retrieves storage subsystem health."""

    def __init__(self, *, storage_status_port: IStorageStatusPort) -> None:
        self._storage_status_port = storage_status_port

    async def handle(
        self,
        actor: ActorContext,
        query: GetStorageStatusQuery,
    ) -> StorageStatusResponse:
        require_admin_read(actor)
        workspace_id = query.workspace_id
        if workspace_id is not None:
            validate_workspace_admin_scope(actor, workspace_id=workspace_id)
        elif not is_global_admin(actor):
            workspace_id = actor.workspace_id

        status = await self._storage_status_port.get_status(workspace_id=workspace_id)
        return AdministrationMapper.to_storage_status_dto(status)
