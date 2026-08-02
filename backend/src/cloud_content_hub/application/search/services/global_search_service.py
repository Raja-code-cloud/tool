"""Global multi-entity search orchestration service."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from cloud_content_hub.application.assets.interfaces.asset_repository import (
    AssetSearchCriteria,
    IAssetRepository,
)
from cloud_content_hub.application.content.interfaces.content_repository import (
    ContentSearchCriteria,
    IContentRepository,
)
from cloud_content_hub.application.search.dto.requests import SearchEntityTypeDto, SearchFiltersDto
from cloud_content_hub.application.search.dto.responses import SearchResult
from cloud_content_hub.application.search.exceptions.search_errors import SearchAccessDeniedError
from cloud_content_hub.application.search.interfaces.publication_search_repository import (
    IPublicationSearchRepository,
    PublicationSearchCriteria,
)
from cloud_content_hub.application.search.interfaces.suggestion_repository import SearchEntityType
from cloud_content_hub.application.search.mappers.search_mapper import SearchMapper
from cloud_content_hub.application.search.queries import SearchAllQuery
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


@dataclass(frozen=True, slots=True)
class GlobalSearchPage:
    """Merged global search page."""

    items: tuple[SearchResult, ...]
    next_cursor: str | None
    has_more: bool
    filters: SearchFiltersDto


class GlobalSearchService:
    """Orchestrates federated search across entity repositories."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        asset_repository_factory: Callable[[IUnitOfWork], IAssetRepository],
        content_repository_factory: Callable[[IUnitOfWork], IContentRepository],
        publication_search_repository_factory: Callable[
            [IUnitOfWork], IPublicationSearchRepository
        ],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._asset_repository_factory = asset_repository_factory
        self._content_repository_factory = content_repository_factory
        self._publication_search_repository_factory = publication_search_repository_factory

    async def search(self, actor: ActorContext, query: SearchAllQuery) -> GlobalSearchPage:
        """Search all entity types the actor can access and merge results."""

        entity_types = self._resolve_entity_types(query, actor)
        if not entity_types:
            raise SearchAccessDeniedError(
                detail="The actor lacks permission to search any resource type.",
            )

        per_type_limit = max(query.limit, 1)
        merged: list[SearchResult] = []

        async with self._unit_of_work_factory() as unit_of_work:
            if SearchEntityType.ASSET in entity_types:
                asset_repository = self._asset_repository_factory(unit_of_work)
                asset_page = await asset_repository.search(
                    AssetSearchCriteria(
                        workspace_id=actor.workspace_id,
                        query=query.query,
                        asset_types=query.asset_types,
                        lifecycle_statuses=query.lifecycle_statuses,
                        owner_id=query.owner_id,
                        project_id=query.project_id,
                        folder_id=query.folder_id,
                        cursor=query.cursor,
                        limit=per_type_limit,
                        sort=query.sort,
                    )
                )
                merged.extend(SearchMapper.from_asset(record) for record in asset_page.items)

            if SearchEntityType.CONTENT in entity_types:
                content_repository = self._content_repository_factory(unit_of_work)
                content_page = await content_repository.search(
                    ContentSearchCriteria(
                        workspace_id=actor.workspace_id,
                        query=query.query,
                        lifecycle_statuses=query.content_lifecycle_statuses,
                        origins=query.content_origins,
                        cursor=query.cursor,
                        limit=per_type_limit,
                        sort=query.sort,
                    )
                )
                merged.extend(SearchMapper.from_content(record) for record in content_page.items)

            if SearchEntityType.PUBLICATION in entity_types:
                publication_repository = self._publication_search_repository_factory(unit_of_work)
                publication_page = await publication_repository.search(
                    PublicationSearchCriteria(
                        workspace_id=actor.workspace_id,
                        query=query.query,
                        statuses=query.publication_statuses,
                        cursor=query.cursor,
                        limit=per_type_limit,
                        sort=query.sort,
                    )
                )
                merged.extend(
                    SearchMapper.from_publication(record) for record in publication_page.items
                )

        merged = self._apply_updated_range(
            merged,
            updated_after=query.updated_after,
            updated_before=query.updated_before,
        )
        merged.sort(key=_sort_key_for(query.sort), reverse=query.sort.startswith("-"))

        page_items = tuple(merged[: query.limit])
        has_more = len(merged) > query.limit
        next_cursor = query.cursor if has_more else None

        filters = SearchFiltersDto(
            entity_types=frozenset(SearchEntityTypeDto(entity.value) for entity in entity_types),
            asset_types=frozenset(asset_type.value for asset_type in query.asset_types),
            lifecycle_statuses=frozenset(status.value for status in query.lifecycle_statuses),
            content_origins=frozenset(origin.value for origin in query.content_origins),
            publication_statuses=frozenset(status.value for status in query.publication_statuses),
            owner_id=query.owner_id,
            project_id=query.project_id,
            folder_id=query.folder_id,
            updated_after=query.updated_after,
            updated_before=query.updated_before,
        )
        return GlobalSearchPage(
            items=page_items,
            next_cursor=next_cursor,
            has_more=has_more,
            filters=filters,
        )

    @staticmethod
    def _resolve_entity_types(
        query: SearchAllQuery,
        actor: ActorContext,
    ) -> frozenset[SearchEntityType]:
        requested = query.entity_types or frozenset(
            {
                SearchEntityType.ASSET,
                SearchEntityType.CONTENT,
                SearchEntityType.PUBLICATION,
            }
        )
        allowed: set[SearchEntityType] = set()
        if SearchEntityType.ASSET in requested and actor.has_permission("assets:read"):
            allowed.add(SearchEntityType.ASSET)
        if SearchEntityType.CONTENT in requested and actor.has_permission("content:read"):
            allowed.add(SearchEntityType.CONTENT)
        if SearchEntityType.PUBLICATION in requested and actor.has_permission("publishing:read"):
            allowed.add(SearchEntityType.PUBLICATION)
        return frozenset(allowed)

    @staticmethod
    def _apply_updated_range(
        items: list[SearchResult],
        *,
        updated_after: datetime | None,
        updated_before: datetime | None,
    ) -> list[SearchResult]:
        filtered = items
        if updated_after is not None:
            filtered = [item for item in filtered if item.updated_at >= updated_after]
        if updated_before is not None:
            filtered = [item for item in filtered if item.updated_at <= updated_before]
        return filtered


def _sort_key_for(sort: str) -> Callable[[SearchResult], datetime]:
    del sort
    return lambda item: item.updated_at
