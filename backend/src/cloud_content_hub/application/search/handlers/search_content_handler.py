"""Content search query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.content.interfaces.content_repository import (
    ContentSearchCriteria,
    IContentRepository,
)
from cloud_content_hub.application.search.dto.requests import SearchEntityTypeDto, SearchFiltersDto
from cloud_content_hub.application.search.dto.responses import SearchResponse
from cloud_content_hub.application.search.interfaces.suggestion_repository import SearchEntityType
from cloud_content_hub.application.search.mappers.search_mapper import SearchMapper
from cloud_content_hub.application.search.queries import SearchContentQuery
from cloud_content_hub.application.search.services.search_history_service import (
    SearchHistoryService,
)
from cloud_content_hub.application.search.validators.search_validator import (
    filters_to_spec,
    normalize_search_query,
    validate_content_sort,
    validate_page_size,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class SearchContentHandler:
    """Searches content and returns unified search results."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        content_repository_factory: Callable[[IUnitOfWork], IContentRepository],
        search_history_service: SearchHistoryService,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._content_repository_factory = content_repository_factory
        self._search_history_service = search_history_service

    async def handle(self, actor: ActorContext, query: SearchContentQuery) -> SearchResponse:
        require_permission(actor, "content:read")
        normalized = normalize_search_query(query.query)
        validate_page_size(query.limit)
        validate_content_sort(query.sort)

        async with self._unit_of_work_factory() as unit_of_work:
            content_repository = self._content_repository_factory(unit_of_work)
            page = await content_repository.search(
                ContentSearchCriteria(
                    workspace_id=actor.workspace_id,
                    query=normalized,
                    lifecycle_statuses=query.lifecycle_statuses,
                    origins=query.origins,
                    cursor=query.cursor,
                    limit=query.limit,
                    sort=query.sort,
                )
            )

        items = tuple(SearchMapper.from_content(record) for record in page.items)
        filters = SearchFiltersDto(
            entity_types=frozenset({SearchEntityTypeDto.CONTENT}),
            lifecycle_statuses=frozenset(status.value for status in query.lifecycle_statuses),
            content_origins=frozenset(origin.value for origin in query.origins),
        )
        filter_spec = filters_to_spec(
            entity_types=frozenset({SearchEntityType.CONTENT.value}),
            lifecycle_statuses=filters.lifecycle_statuses,
            content_origins=filters.content_origins,
        )
        await self._search_history_service.record(
            actor,
            query=normalized,
            entity_types=frozenset({SearchEntityType.CONTENT}),
            filter_spec=filter_spec,
            result_count=len(items),
        )
        return SearchResponse(
            items=items,
            query=normalized,
            filters=filters,
            page_next_cursor=page.next_cursor,
            page_has_more=page.has_more,
            page_limit=query.limit,
        )
