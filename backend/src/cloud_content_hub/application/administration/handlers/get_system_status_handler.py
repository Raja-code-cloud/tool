"""Get system status query handler."""

from __future__ import annotations

from cloud_content_hub.application.administration.dto.responses import SystemStatusResponse
from cloud_content_hub.application.administration.interfaces.system_status_port import (
    ISystemStatusPort,
)
from cloud_content_hub.application.administration.mappers.administration_mapper import (
    AdministrationMapper,
)
from cloud_content_hub.application.administration.queries import GetSystemStatusQuery
from cloud_content_hub.application.administration.validators.administration_validator import (
    require_admin_read,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.core.errors import DependencyUnavailableError


class GetSystemStatusHandler:
    """Retrieves operational system status."""

    def __init__(self, *, system_status_port: ISystemStatusPort) -> None:
        self._system_status_port = system_status_port

    async def handle(
        self, actor: ActorContext, query: GetSystemStatusQuery
    ) -> SystemStatusResponse:
        _ = query
        require_admin_read(actor)
        try:
            status = await self._system_status_port.get_status()
        except Exception as exc:
            raise DependencyUnavailableError(
                detail="System status service is unavailable.",
            ) from exc
        return AdministrationMapper.to_system_status_dto(status)
