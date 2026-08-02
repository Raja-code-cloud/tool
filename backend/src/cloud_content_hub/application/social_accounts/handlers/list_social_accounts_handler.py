"""List social accounts query handler."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.dto.base import PagedResultDto, PageInfoDto
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.application.social_accounts.dto.responses import SocialAccountDto
from cloud_content_hub.application.social_accounts.interfaces.social_account_repository import (
    ISocialAccountRepository,
    SocialAccountListCriteria,
)
from cloud_content_hub.application.social_accounts.mappers.social_account_mapper import (
    SocialAccountMapper,
)


class ListSocialAccountsHandler:
    """Lists connected social accounts for the current workspace."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        social_account_repository_factory: Callable[[IUnitOfWork], ISocialAccountRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._social_account_repository_factory = social_account_repository_factory

    async def handle(
        self, actor: ActorContext, query: dict[str, Any]
    ) -> PagedResultDto[SocialAccountDto]:
        require_permission(actor, "publishing:read")

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._social_account_repository_factory(unit_of_work)
            page = await repository.list_accounts(
                SocialAccountListCriteria(
                    workspace_id=actor.workspace_id,
                    cursor=query.get("cursor"),
                    limit=int(query.get("limit", 25)),
                    sort=str(query.get("sort", "-updated_at")),
                )
            )

        items = tuple(SocialAccountMapper.to_dto(record) for record in page.items)
        return PagedResultDto(
            items=items,
            page=PageInfoDto(
                next_cursor=page.next_cursor,
                has_more=page.has_more,
                limit=int(query.get("limit", 25)),
            ),
        )
