"""Global search query handler."""

from __future__ import annotations

from cloud_content_hub.application.search.dto.responses import SearchResponse
from cloud_content_hub.application.search.interfaces.suggestion_repository import SearchEntityType
from cloud_content_hub.application.search.queries import SearchAllQuery
from cloud_content_hub.application.search.services.global_search_service import GlobalSearchService
from cloud_content_hub.application.search.services.search_history_service import (
    SearchHistoryService,
)
from cloud_content_hub.application.search.validators.search_validator import (
    filters_to_spec,
    normalize_search_query,
    validate_global_sort,
    validate_page_size,
    validate_updated_range,
)
from cloud_content_hub.application.shared.actor import ActorContext


class SearchAllHandler:
    """Searches across all entity types the actor can access."""

    def __init__(
        self,
        *,
        global_search_service: GlobalSearchService,
        search_history_service: SearchHistoryService,
    ) -> None:
        self._global_search_service = global_search_service
        self._search_history_service = search_history_service

    async def handle(self, actor: ActorContext, query: SearchAllQuery) -> SearchResponse:
        normalized = normalize_search_query(query.query)
        validate_page_size(query.limit)
        validate_global_sort(query.sort)
        validate_updated_range(
            updated_after=query.updated_after,
            updated_before=query.updated_before,
        )

        page = await self._global_search_service.search(
            actor,
            SearchAllQuery(
                query=normalized,
                entity_types=query.entity_types,
                asset_types=query.asset_types,
                lifecycle_statuses=query.lifecycle_statuses,
                content_lifecycle_statuses=query.content_lifecycle_statuses,
                content_origins=query.content_origins,
                publication_statuses=query.publication_statuses,
                owner_id=query.owner_id,
                project_id=query.project_id,
                folder_id=query.folder_id,
                updated_after=query.updated_after,
                updated_before=query.updated_before,
                cursor=query.cursor,
                limit=query.limit,
                sort=query.sort,
            ),
        )

        entity_types = frozenset(
            SearchEntityType(entity_type.value) for entity_type in page.filters.entity_types
        )
        filter_spec = filters_to_spec(
            entity_types=frozenset(entity_type.value for entity_type in entity_types),
            asset_types=page.filters.asset_types,
            lifecycle_statuses=page.filters.lifecycle_statuses,
            content_origins=page.filters.content_origins,
            publication_statuses=page.filters.publication_statuses,
            owner_id=str(page.filters.owner_id) if page.filters.owner_id else None,
            project_id=str(page.filters.project_id) if page.filters.project_id else None,
            folder_id=str(page.filters.folder_id) if page.filters.folder_id else None,
            updated_after=page.filters.updated_after,
            updated_before=page.filters.updated_before,
        )

        await self._search_history_service.record(
            actor,
            query=normalized,
            entity_types=entity_types,
            filter_spec=filter_spec,
            result_count=len(page.items),
        )

        return SearchResponse(
            items=page.items,
            query=normalized,
            filters=page.filters,
            page_next_cursor=page.next_cursor,
            page_has_more=page.has_more,
            page_limit=query.limit,
        )
