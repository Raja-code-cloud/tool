"""Get provider health query handler."""

from __future__ import annotations

from cloud_content_hub.application.administration.dto.responses import ProviderHealthResponse
from cloud_content_hub.application.administration.interfaces.provider_health_port import (
    IProviderHealthPort,
    ProviderHealthCriteria,
)
from cloud_content_hub.application.administration.mappers.administration_mapper import (
    AdministrationMapper,
)
from cloud_content_hub.application.administration.queries import GetProviderHealthQuery
from cloud_content_hub.application.administration.validators.administration_validator import (
    is_global_admin,
    require_admin_read,
    validate_workspace_admin_scope,
)
from cloud_content_hub.application.shared.actor import ActorContext


class GetProviderHealthHandler:
    """Retrieves normalized provider health summaries."""

    def __init__(self, *, provider_health_port: IProviderHealthPort) -> None:
        self._provider_health_port = provider_health_port

    async def handle(
        self,
        actor: ActorContext,
        query: GetProviderHealthQuery,
    ) -> tuple[ProviderHealthResponse, ...]:
        require_admin_read(actor)
        workspace_id = query.workspace_id
        if workspace_id is not None:
            validate_workspace_admin_scope(actor, workspace_id=workspace_id)
        elif not is_global_admin(actor):
            workspace_id = actor.workspace_id

        providers = await self._provider_health_port.list_providers(
            ProviderHealthCriteria(
                workspace_id=workspace_id,
                provider_types=query.provider_types,
                statuses=query.statuses,
            )
        )
        return tuple(
            AdministrationMapper.to_provider_health_dto(provider) for provider in providers
        )
