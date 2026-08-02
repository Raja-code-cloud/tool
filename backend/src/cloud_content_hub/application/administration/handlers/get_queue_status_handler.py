"""Get queue status query handler."""

from __future__ import annotations

from cloud_content_hub.application.administration.dto.responses import QueueStatusResponse
from cloud_content_hub.application.administration.interfaces.queue_status_port import (
    IQueueStatusPort,
    QueueStatusCriteria,
)
from cloud_content_hub.application.administration.mappers.administration_mapper import (
    AdministrationMapper,
)
from cloud_content_hub.application.administration.queries import GetQueueStatusQuery
from cloud_content_hub.application.administration.validators.administration_validator import (
    is_global_admin,
    require_admin_read,
    validate_workspace_admin_scope,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.core.errors import DependencyUnavailableError


class GetQueueStatusHandler:
    """Retrieves aggregate queue summaries."""

    def __init__(self, *, queue_status_port: IQueueStatusPort) -> None:
        self._queue_status_port = queue_status_port

    async def handle(
        self,
        actor: ActorContext,
        query: GetQueueStatusQuery,
    ) -> tuple[QueueStatusResponse, ...]:
        require_admin_read(actor)
        workspace_id = query.workspace_id
        if workspace_id is not None:
            validate_workspace_admin_scope(actor, workspace_id=workspace_id)
        elif not is_global_admin(actor):
            workspace_id = actor.workspace_id

        try:
            summaries = await self._queue_status_port.list_queue_summaries(
                QueueStatusCriteria(
                    workspace_id=workspace_id,
                    queue_names=query.queue_names,
                )
            )
        except Exception as exc:
            raise DependencyUnavailableError(
                detail="Queue status service is unavailable.",
            ) from exc
        return tuple(AdministrationMapper.to_queue_status_dto(summary) for summary in summaries)
