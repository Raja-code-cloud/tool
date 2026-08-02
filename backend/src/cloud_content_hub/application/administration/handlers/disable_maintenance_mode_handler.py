"""Disable maintenance mode command handler."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from cloud_content_hub.application.administration.commands import DisableMaintenanceModeCommand
from cloud_content_hub.application.administration.dto.responses import MaintenanceModeStateResponse
from cloud_content_hub.application.administration.events import MaintenanceModeDisabled
from cloud_content_hub.application.administration.interfaces.administration_repository import (
    IAdministrationRepository,
    MaintenanceModeUpdate,
)
from cloud_content_hub.application.administration.interfaces.event_publisher import (
    IAdministrationEventPublisher,
)
from cloud_content_hub.application.administration.mappers.administration_mapper import (
    AdministrationMapper,
)
from cloud_content_hub.application.administration.services.audit_service import AuditService
from cloud_content_hub.application.administration.validators.administration_validator import (
    require_global_admin,
    validate_maintenance_transition,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class DisableMaintenanceModeHandler:
    """Disables global maintenance mode."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        administration_repository_factory: Callable[[IUnitOfWork], IAdministrationRepository],
        event_publisher: IAdministrationEventPublisher | None = None,
        audit_service: AuditService | None = None,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._administration_repository_factory = administration_repository_factory
        self._event_publisher = event_publisher
        self._audit_service = audit_service or AuditService(
            administration_repository_factory=administration_repository_factory,
        )

    async def handle(
        self,
        actor: ActorContext,
        command: DisableMaintenanceModeCommand,
    ) -> MaintenanceModeStateResponse:
        _ = command
        require_global_admin(actor)

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._administration_repository_factory(unit_of_work)
            current = await repository.get_maintenance_mode()
            validate_maintenance_transition(
                current_enabled=current.enabled, requested_enabled=False
            )

            state = await repository.set_maintenance_mode(
                MaintenanceModeUpdate(
                    enabled=False,
                    message=None,
                    updated_by=actor.user_id,
                )
            )

            await self._audit_service.record_success(
                unit_of_work=unit_of_work,
                actor_user_id=actor.user_id,
                action="maintenance.disable",
                target_type="system",
                target_id=None,
                source="administration",
                safe_diff={"enabled": False},
            )

            if self._event_publisher is not None:
                await self._event_publisher.publish(
                    MaintenanceModeDisabled(
                        actor_id=actor.user_id,
                        occurred_at=datetime.now(tz=UTC),
                    ),
                    unit_of_work=unit_of_work,
                )

            await unit_of_work.flush()

        return AdministrationMapper.to_maintenance_mode_dto(state)
