"""Search content query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.content.dto.responses import ContentDto
from cloud_content_hub.application.content.interfaces.content_repository import (
    ContentSearchCriteria,
    IContentRepository,
)
from cloud_content_hub.application.content.mappers.content_mapper import ContentMapper
from cloud_content_hub.application.content.queries import ListContentQuery, SearchContentQuery
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.dto.base import PagedResultDto, PageInfoDto
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class SearchContentHandler:
    """Searches content with optional full-text query."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        content_repository_factory: Callable[[IUnitOfWork], IContentRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._content_repository_factory = content_repository_factory

    async def handle(
        self, actor: ActorContext, query: SearchContentQuery
    ) -> PagedResultDto[ContentDto]:
        require_permission(actor, "content:read")

        async with self._unit_of_work_factory() as unit_of_work:
            content_repository = self._content_repository_factory(unit_of_work)
            page = await content_repository.search(
                ContentSearchCriteria(
                    workspace_id=actor.workspace_id,
                    query=query.query,
                    lifecycle_statuses=query.lifecycle_statuses,
                    origins=query.origins,
                    cursor=query.cursor,
                    limit=query.limit,
                    sort=query.sort,
                )
            )

        items = tuple(ContentMapper.to_dto(record) for record in page.items)
        return PagedResultDto(
            items=items,
            page=PageInfoDto(
                next_cursor=page.next_cursor, has_more=page.has_more, limit=query.limit
            ),
        )


class ListContentHandler:
    """Lists content with structured filters."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        content_repository_factory: Callable[[IUnitOfWork], IContentRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._content_repository_factory = content_repository_factory

    async def handle(
        self, actor: ActorContext, query: ListContentQuery
    ) -> PagedResultDto[ContentDto]:
        require_permission(actor, "content:read")

        async with self._unit_of_work_factory() as unit_of_work:
            content_repository = self._content_repository_factory(unit_of_work)
            page = await content_repository.list_content(
                workspace_id=actor.workspace_id,
                lifecycle_statuses=query.lifecycle_statuses,
                origins=query.origins,
                cursor=query.cursor,
                limit=query.limit,
                sort=query.sort,
            )

        items = tuple(ContentMapper.to_dto(record) for record in page.items)
        return PagedResultDto(
            items=items,
            page=PageInfoDto(
                next_cursor=page.next_cursor, has_more=page.has_more, limit=query.limit
            ),
        )
