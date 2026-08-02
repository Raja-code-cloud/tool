"""List publication history query handler."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from cloud_content_hub.api.schemas.transport import PublicationHistoryItemDto
from cloud_content_hub.application.publishing.interfaces.publication_repository import (
    IPublicationRepository,
    PublicationHistoryCriteria,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.dto.base import PagedResultDto, PageInfoDto
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class ListPublicationHistoryHandler:
    """Lists publication status history for the current workspace."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        publication_repository_factory: Callable[[IUnitOfWork], IPublicationRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._publication_repository_factory = publication_repository_factory

    async def handle(
        self, actor: ActorContext, query: dict[str, Any]
    ) -> PagedResultDto[PublicationHistoryItemDto]:
        require_permission(actor, "publishing:read")

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._publication_repository_factory(unit_of_work)
            page = await repository.list_publication_history(
                PublicationHistoryCriteria(
                    workspace_id=actor.workspace_id,
                    cursor=query.get("cursor"),
                    limit=int(query.get("limit", 25)),
                    occurred_after=query.get("occurred_after"),
                    occurred_before=query.get("occurred_before"),
                    states=query.get("states", frozenset()),
                    content_id=query.get("content_id"),
                    platform_id=query.get("platform_id"),
                    social_account_id=query.get("social_account_id"),
                    sort=str(query.get("sort", "-occurred_at")),
                )
            )

        items = tuple(
            PublicationHistoryItemDto(
                id=record.id,
                publication_id=record.publication_id,
                target_id=record.target_id,
                state_type=record.state_type,
                from_state=record.from_state,
                to_state=record.to_state,
                reason_code=record.reason_code,
                occurred_at=record.occurred_at,
            )
            for record in page.items
        )
        return PagedResultDto(
            items=items,
            page=PageInfoDto(
                next_cursor=page.next_cursor,
                has_more=page.has_more,
                limit=int(query.get("limit", 25)),
            ),
        )
