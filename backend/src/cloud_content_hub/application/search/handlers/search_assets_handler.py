"""Asset search query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.assets.interfaces.asset_repository import (
    AssetSearchCriteria,
    IAssetRepository,
)
from cloud_content_hub.application.search.dto.requests import SearchEntityTypeDto, SearchFiltersDto
from cloud_content_hub.application.search.dto.responses import SearchResponse
from cloud_content_hub.application.search.interfaces.suggestion_repository import SearchEntityType
from cloud_content_hub.application.search.mappers.search_mapper import SearchMapper
from cloud_content_hub.application.search.queries import SearchAssetsQuery
from cloud_content_hub.application.search.services.search_history_service import (
    SearchHistoryService,
)
from cloud_content_hub.application.search.validators.search_validator import (
    filters_to_spec,
    normalize_search_query,
    validate_asset_sort,
    validate_page_size,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class SearchAssetsHandler:
    """Searches assets and returns unified search results."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        asset_repository_factory: Callable[[IUnitOfWork], IAssetRepository],
        search_history_service: SearchHistoryService,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._asset_repository_factory = asset_repository_factory
        self._search_history_service = search_history_service

    async def handle(self, actor: ActorContext, query: SearchAssetsQuery) -> SearchResponse:
        require_permission(actor, "assets:read")
        normalized = normalize_search_query(query.query)
        validate_page_size(query.limit)
        validate_asset_sort(query.sort)

        async with self._unit_of_work_factory() as unit_of_work:
            asset_repository = self._asset_repository_factory(unit_of_work)
            page = await asset_repository.search(
                AssetSearchCriteria(
                    workspace_id=actor.workspace_id,
                    query=normalized,
                    asset_types=query.asset_types,
                    lifecycle_statuses=query.lifecycle_statuses,
                    owner_id=query.owner_id,
                    project_id=query.project_id,
                    folder_id=query.folder_id,
                    cursor=query.cursor,
                    limit=query.limit,
                    sort=query.sort,
                )
            )

        items = tuple(SearchMapper.from_asset(record) for record in page.items)
        filters = SearchFiltersDto(
            entity_types=frozenset({SearchEntityTypeDto.ASSET}),
            asset_types=frozenset(asset_type.value for asset_type in query.asset_types),
            lifecycle_statuses=frozenset(status.value for status in query.lifecycle_statuses),
            owner_id=query.owner_id,
            project_id=query.project_id,
            folder_id=query.folder_id,
        )
        filter_spec = filters_to_spec(
            entity_types=frozenset({SearchEntityType.ASSET.value}),
            asset_types=filters.asset_types,
            lifecycle_statuses=filters.lifecycle_statuses,
            owner_id=str(query.owner_id) if query.owner_id else None,
            project_id=str(query.project_id) if query.project_id else None,
            folder_id=str(query.folder_id) if query.folder_id else None,
        )
        await self._search_history_service.record(
            actor,
            query=normalized,
            entity_types=frozenset({SearchEntityType.ASSET}),
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
