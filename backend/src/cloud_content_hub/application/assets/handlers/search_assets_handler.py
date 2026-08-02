"""Search assets query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.assets.dto.responses import AssetDto
from cloud_content_hub.application.assets.interfaces.asset_repository import (
    AssetSearchCriteria,
    IAssetRepository,
)
from cloud_content_hub.application.assets.mappers.asset_mapper import AssetMapper
from cloud_content_hub.application.assets.queries import ListAssetsQuery, SearchAssetsQuery
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.dto.base import PagedResultDto, PageInfoDto
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.core.errors import ValidationError


class SearchAssetsHandler:
    """Searches assets with full-text and structured filters."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        asset_repository_factory: Callable[[IUnitOfWork], IAssetRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._asset_repository_factory = asset_repository_factory
        self._mapper = AssetMapper()

    async def handle(
        self,
        actor: ActorContext,
        query: SearchAssetsQuery,
    ) -> PagedResultDto[AssetDto]:
        require_permission(actor, "assets:read")
        normalized = query.query.strip()
        if len(normalized) < 2 or len(normalized) > 200:
            raise ValidationError(detail="Search query must be between 2 and 200 characters.")

        async with self._unit_of_work_factory() as unit_of_work:
            asset_repository = self._asset_repository_factory(unit_of_work)
            page = await asset_repository.search(
                AssetSearchCriteria(
                    workspace_id=actor.workspace_id,
                    query=normalized,
                    asset_types=query.asset_types,
                    lifecycle_statuses=query.lifecycle_statuses,
                    cursor=query.cursor,
                    limit=query.limit,
                    sort=query.sort,
                )
            )

        items = tuple([await self._mapper.to_dto(record) for record in page.items])
        return PagedResultDto(
            items=items,
            page=PageInfoDto(
                next_cursor=page.next_cursor,
                has_more=page.has_more,
                limit=query.limit,
            ),
        )


class ListAssetsHandler:
    """Lists assets with structured filters."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        asset_repository_factory: Callable[[IUnitOfWork], IAssetRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._asset_repository_factory = asset_repository_factory
        self._mapper = AssetMapper()

    async def handle(self, actor: ActorContext, query: ListAssetsQuery) -> PagedResultDto[AssetDto]:
        require_permission(actor, "assets:read")

        async with self._unit_of_work_factory() as unit_of_work:
            asset_repository = self._asset_repository_factory(unit_of_work)
            page = await asset_repository.list_assets(
                workspace_id=actor.workspace_id,
                asset_types=query.asset_types,
                lifecycle_statuses=query.lifecycle_statuses,
                owner_id=query.owner_id,
                project_id=query.project_id,
                folder_id=query.folder_id,
                cursor=query.cursor,
                limit=query.limit,
                sort=query.sort,
            )

        items = tuple([await self._mapper.to_dto(record) for record in page.items])
        return PagedResultDto(
            items=items,
            page=PageInfoDto(
                next_cursor=page.next_cursor,
                has_more=page.has_more,
                limit=query.limit,
            ),
        )
