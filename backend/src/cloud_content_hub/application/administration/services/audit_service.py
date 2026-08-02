"""Audit orchestration for administrative actions."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from uuid import UUID

from cloud_content_hub.application.administration.interfaces.administration_repository import (
    AuditActorType,
    AuditOutcome,
    IAdministrationRepository,
    NewAuditLog,
)
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class AuditService:
    """Appends audit evidence for administrative use cases."""

    def __init__(
        self,
        *,
        administration_repository_factory: Callable[[IUnitOfWork], IAdministrationRepository],
    ) -> None:
        self._administration_repository_factory = administration_repository_factory

    async def record_success(
        self,
        *,
        unit_of_work: IUnitOfWork,
        actor_user_id: UUID,
        action: str,
        target_type: str,
        target_id: UUID | None,
        workspace_id: UUID | None = None,
        organization_id: UUID | None = None,
        source: str = "administration",
        safe_diff: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> None:
        """Persist a successful administrative audit entry."""

        repository = self._administration_repository_factory(unit_of_work)
        await repository.append_audit(
            NewAuditLog(
                workspace_id=workspace_id,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                actor_type=AuditActorType.USER,
                action=action,
                target_type=target_type,
                target_id=target_id,
                outcome=AuditOutcome.SUCCESS,
                source=source,
                safe_diff=safe_diff,
                request_id=request_id,
            )
        )
