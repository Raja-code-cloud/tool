"""Refresh provider health command handler."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from cloud_content_hub.application.administration.commands import RefreshProviderHealthCommand
from cloud_content_hub.application.administration.dto.responses import ProviderHealthResponse
from cloud_content_hub.application.administration.events import ProviderHealthChecked
from cloud_content_hub.application.administration.interfaces.administration_repository import (
    IAdministrationRepository,
)
from cloud_content_hub.application.administration.interfaces.event_publisher import (
    IAdministrationEventPublisher,
)
from cloud_content_hub.application.administration.interfaces.provider_health_port import (
    IProviderHealthPort,
)
from cloud_content_hub.application.administration.mappers.administration_mapper import (
    AdministrationMapper,
)
from cloud_content_hub.application.administration.services.audit_service import AuditService
from cloud_content_hub.application.administration.validators.administration_validator import (
    is_global_admin,
    require_admin_write,
    validate_provider_types,
    validate_workspace_admin_scope,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class RefreshProviderHealthHandler:
    """Refreshes provider health checks."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        provider_health_port: IProviderHealthPort,
        event_publisher: IAdministrationEventPublisher | None = None,
        audit_service: AuditService | None = None,
        administration_repository_factory: Callable[[IUnitOfWork], IAdministrationRepository]
        | None = None,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._provider_health_port = provider_health_port
        self._event_publisher = event_publisher
        self._audit_service: AuditService | None
        if audit_service is not None:
            self._audit_service = audit_service
        elif administration_repository_factory is not None:
            self._audit_service = AuditService(
                administration_repository_factory=administration_repository_factory,
            )
        else:
            self._audit_service = None

    async def handle(
        self,
        actor: ActorContext,
        command: RefreshProviderHealthCommand,
    ) -> tuple[ProviderHealthResponse, ...]:
        require_admin_write(actor)
        workspace_id = command.workspace_id
        if workspace_id is not None:
            validate_workspace_admin_scope(actor, workspace_id=workspace_id)
        elif not is_global_admin(actor):
            workspace_id = actor.workspace_id

        provider_types = validate_provider_types(command.request.provider_types)
        providers = await self._provider_health_port.refresh_health(
            workspace_id=workspace_id,
            provider_types=provider_types,
            refreshed_by=actor.user_id,
        )

        async with self._unit_of_work_factory() as unit_of_work:
            if self._audit_service is not None:
                await self._audit_service.record_success(
                    unit_of_work=unit_of_work,
                    actor_user_id=actor.user_id,
                    action="provider.health.refresh",
                    target_type="provider",
                    target_id=None,
                    workspace_id=workspace_id,
                    safe_diff={
                        "providerTypes": [provider_type.value for provider_type in provider_types]
                    },
                )

            if self._event_publisher is not None:
                occurred_at = datetime.now(tz=UTC)
                for provider in providers:
                    await self._event_publisher.publish(
                        ProviderHealthChecked(
                            provider_type=provider.provider_type,
                            provider_code=provider.code,
                            actor_id=actor.user_id,
                            occurred_at=occurred_at,
                        ),
                        unit_of_work=unit_of_work,
                    )

            await unit_of_work.flush()

        return tuple(
            AdministrationMapper.to_provider_health_dto(provider) for provider in providers
        )
