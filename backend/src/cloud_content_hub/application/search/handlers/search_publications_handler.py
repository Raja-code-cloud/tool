"""Publication search query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.search.dto.requests import SearchEntityTypeDto, SearchFiltersDto
from cloud_content_hub.application.search.dto.responses import SearchResponse
from cloud_content_hub.application.search.interfaces.publication_search_repository import (
    IPublicationSearchRepository,
    PublicationSearchCriteria,
)
from cloud_content_hub.application.search.interfaces.suggestion_repository import SearchEntityType
from cloud_content_hub.application.search.mappers.search_mapper import SearchMapper
from cloud_content_hub.application.search.queries import SearchPublicationsQuery
from cloud_content_hub.application.search.services.search_history_service import (
    SearchHistoryService,
)
from cloud_content_hub.application.search.validators.search_validator import (
    filters_to_spec,
    normalize_search_query,
    validate_page_size,
    validate_publication_sort,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class SearchPublicationsHandler:
    """Searches publications and returns unified search results."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        publication_search_repository_factory: Callable[
            [IUnitOfWork], IPublicationSearchRepository
        ],
        search_history_service: SearchHistoryService,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._publication_search_repository_factory = publication_search_repository_factory
        self._search_history_service = search_history_service

    async def handle(
        self,
        actor: ActorContext,
        query: SearchPublicationsQuery,
    ) -> SearchResponse:
        require_permission(actor, "publishing:read")
        normalized = normalize_search_query(query.query)
        validate_page_size(query.limit)
        validate_publication_sort(query.sort)

        async with self._unit_of_work_factory() as unit_of_work:
            publication_repository = self._publication_search_repository_factory(unit_of_work)
            page = await publication_repository.search(
                PublicationSearchCriteria(
                    workspace_id=actor.workspace_id,
                    query=normalized,
                    statuses=query.statuses,
                    cursor=query.cursor,
                    limit=query.limit,
                    sort=query.sort,
                )
            )

        items = tuple(SearchMapper.from_publication(record) for record in page.items)
        filters = SearchFiltersDto(
            entity_types=frozenset({SearchEntityTypeDto.PUBLICATION}),
            publication_statuses=frozenset(status.value for status in query.statuses),
        )
        filter_spec = filters_to_spec(
            entity_types=frozenset({SearchEntityType.PUBLICATION.value}),
            publication_statuses=filters.publication_statuses,
        )
        await self._search_history_service.record(
            actor,
            query=normalized,
            entity_types=frozenset({SearchEntityType.PUBLICATION}),
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
