"""List enabled social platforms query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.application.social_accounts.dto.responses import SocialPlatformDto
from cloud_content_hub.application.social_accounts.interfaces.social_account_repository import (
    ISocialAccountRepository,
)
from cloud_content_hub.application.social_accounts.mappers.social_account_mapper import (
    SocialAccountMapper,
)


class ListSocialPlatformsHandler:
    """Lists globally enabled social platforms."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        social_account_repository_factory: Callable[[IUnitOfWork], ISocialAccountRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._social_account_repository_factory = social_account_repository_factory

    async def handle(self, actor: ActorContext) -> tuple[SocialPlatformDto, ...]:
        require_permission(actor, "publishing:read")

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._social_account_repository_factory(unit_of_work)
            platforms = await repository.list_enabled_platforms()

        return tuple(SocialAccountMapper.to_platform_dto(record) for record in platforms)
