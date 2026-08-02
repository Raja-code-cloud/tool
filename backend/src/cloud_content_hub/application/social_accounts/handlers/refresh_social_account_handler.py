"""Refresh social account connection handler."""

from __future__ import annotations

from collections.abc import Callable
from uuid import UUID

from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.application.social_accounts.dto.responses import SocialAccountDto
from cloud_content_hub.application.social_accounts.exceptions.social_account_errors import (
    SocialAccountNotFoundError,
)
from cloud_content_hub.application.social_accounts.interfaces.social_account_repository import (
    ISocialAccountRepository,
)
from cloud_content_hub.application.social_accounts.mappers.social_account_mapper import (
    SocialAccountMapper,
)


class RefreshSocialAccountHandler:
    """Refreshes token and sync metadata for a connected social account."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        social_account_repository_factory: Callable[[IUnitOfWork], ISocialAccountRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._social_account_repository_factory = social_account_repository_factory

    async def handle(self, actor: ActorContext, account_id: UUID) -> SocialAccountDto:
        require_permission(actor, "publishing:write")

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._social_account_repository_factory(unit_of_work)
            existing = await repository.get_by_id(
                workspace_id=actor.workspace_id,
                account_id=account_id,
            )
            if existing is None:
                raise SocialAccountNotFoundError(parameters={"accountId": str(account_id)})

            record = await repository.refresh_account(
                workspace_id=actor.workspace_id,
                account_id=account_id,
                updated_by=actor.user_id,
            )
            await unit_of_work.flush()

        return SocialAccountMapper.to_dto(record)
