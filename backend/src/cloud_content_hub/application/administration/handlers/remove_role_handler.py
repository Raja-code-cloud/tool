"""Remove role command handler."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from cloud_content_hub.application.administration.commands import RemoveRoleCommand
from cloud_content_hub.application.administration.events import RoleRemoved
from cloud_content_hub.application.administration.exceptions.administration_errors import (
    MembershipNotFoundError,
    RoleNotFoundError,
)
from cloud_content_hub.application.administration.interfaces.administration_repository import (
    IAdministrationRepository,
    RoleRemoval,
)
from cloud_content_hub.application.administration.interfaces.event_publisher import (
    IAdministrationEventPublisher,
)
from cloud_content_hub.application.administration.services.audit_service import AuditService
from cloud_content_hub.application.administration.validators.administration_validator import (
    is_global_admin,
    require_admin_write,
    validate_role_hierarchy,
    validate_role_workspace_scope,
    validate_workspace_admin_scope,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class RemoveRoleHandler:
    """Removes a role from a workspace membership."""

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

    async def handle(self, actor: ActorContext, command: RemoveRoleCommand) -> None:
        require_admin_write(actor)
        workspace_id = command.request.workspace_id
        validate_workspace_admin_scope(actor, workspace_id=workspace_id)

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._administration_repository_factory(unit_of_work)

            membership = await repository.get_membership(
                workspace_id=workspace_id,
                membership_id=command.request.membership_id,
            )
            if membership is None:
                raise MembershipNotFoundError(
                    parameters={"membershipId": str(command.request.membership_id)},
                )

            role = await repository.get_role(
                role_id=command.request.role_id,
                workspace_id=workspace_id,
            )
            if role is None:
                raise RoleNotFoundError(parameters={"roleId": str(command.request.role_id)})

            validate_role_workspace_scope(role=role, workspace_id=workspace_id)
            actor_roles = await repository.list_actor_roles(
                workspace_id=workspace_id,
                user_id=actor.user_id,
            )
            validate_role_hierarchy(
                actor_roles=actor_roles,
                target_role=role,
                bypass=is_global_admin(actor),
            )

            await repository.remove_role(
                RoleRemoval(
                    workspace_id=workspace_id,
                    membership_id=command.request.membership_id,
                    role_id=command.request.role_id,
                    removed_by=actor.user_id,
                )
            )

            await self._audit_service.record_success(
                unit_of_work=unit_of_work,
                actor_user_id=actor.user_id,
                action="role.remove",
                target_type="membership_role",
                target_id=command.request.membership_id,
                workspace_id=workspace_id,
                safe_diff={"roleId": str(command.request.role_id)},
            )

            if self._event_publisher is not None:
                await self._event_publisher.publish(
                    RoleRemoved(
                        workspace_id=workspace_id,
                        membership_id=command.request.membership_id,
                        role_id=command.request.role_id,
                        actor_id=actor.user_id,
                        occurred_at=datetime.now(tz=UTC),
                    ),
                    unit_of_work=unit_of_work,
                )

            await unit_of_work.flush()
