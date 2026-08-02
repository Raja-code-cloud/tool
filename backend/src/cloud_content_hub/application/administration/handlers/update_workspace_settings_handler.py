"""Update workspace settings command handler."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from cloud_content_hub.application.administration.commands import UpdateWorkspaceSettingsCommand
from cloud_content_hub.application.administration.dto.responses import WorkspaceSummaryResponse
from cloud_content_hub.application.administration.events import WorkspaceUpdated
from cloud_content_hub.application.administration.interfaces.administration_repository import (
    IAdministrationRepository,
    WorkspaceSettingsUpdate,
)
from cloud_content_hub.application.administration.interfaces.event_publisher import (
    IAdministrationEventPublisher,
)
from cloud_content_hub.application.administration.mappers.administration_mapper import (
    AdministrationMapper,
)
from cloud_content_hub.application.administration.services.audit_service import AuditService
from cloud_content_hub.application.administration.validators.administration_validator import (
    require_admin_write,
    validate_workspace_admin_scope,
    validate_workspace_exists,
    validate_workspace_settings_update,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.core.errors import VersionConflictError


class UpdateWorkspaceSettingsHandler:
    """Updates mutable workspace settings."""

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
        command: UpdateWorkspaceSettingsCommand,
    ) -> WorkspaceSummaryResponse:
        require_admin_write(actor)
        validate_workspace_admin_scope(actor, workspace_id=command.workspace_id)
        validate_workspace_settings_update(command.request)

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._administration_repository_factory(unit_of_work)
            existing = await repository.get_workspace(command.workspace_id)
            validate_workspace_exists(existing, workspace_id=command.workspace_id)
            assert existing is not None
            if existing.version != command.expected_version:
                raise VersionConflictError(
                    parameters={
                        "workspaceId": str(command.workspace_id),
                        "expectedVersion": command.expected_version,
                    },
                )

            workspace = await repository.update_workspace_settings(
                WorkspaceSettingsUpdate(
                    workspace_id=command.workspace_id,
                    expected_version=command.expected_version,
                    name=command.request.name,
                    time_zone=command.request.time_zone,
                    retention_policy_days=command.request.retention_policy_days,
                    updated_by=actor.user_id,
                )
            )

            await self._audit_service.record_success(
                unit_of_work=unit_of_work,
                actor_user_id=actor.user_id,
                action="workspace.update",
                target_type="workspace",
                target_id=command.workspace_id,
                workspace_id=command.workspace_id,
                safe_diff={
                    "name": command.request.name,
                    "timeZone": command.request.time_zone,
                    "retentionPolicyDays": command.request.retention_policy_days,
                },
            )

            if self._event_publisher is not None:
                await self._event_publisher.publish(
                    WorkspaceUpdated(
                        workspace_id=command.workspace_id,
                        actor_id=actor.user_id,
                        version=workspace.version,
                        occurred_at=datetime.now(tz=UTC),
                    ),
                    unit_of_work=unit_of_work,
                )

            await unit_of_work.flush()

        return AdministrationMapper.to_workspace_summary_dto(workspace)
