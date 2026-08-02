"""Get asset details query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.assets.dto.responses import AssetDetailsDto
from cloud_content_hub.application.assets.exceptions.asset_errors import AssetNotFoundError
from cloud_content_hub.application.assets.interfaces.asset_repository import IAssetRepository
from cloud_content_hub.application.assets.mappers.asset_mapper import AssetMapper
from cloud_content_hub.application.assets.queries import GetAssetDetailsQuery
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.object_storage import IObjectStoragePort
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class GetAssetDetailsHandler:
    """Retrieves extended asset details."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        asset_repository_factory: Callable[[IUnitOfWork], IAssetRepository],
        storage: IObjectStoragePort | None = None,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._asset_repository_factory = asset_repository_factory
        self._mapper = AssetMapper(storage=storage)

    async def handle(self, actor: ActorContext, query: GetAssetDetailsQuery) -> AssetDetailsDto:
        require_permission(actor, "assets:read")

        async with self._unit_of_work_factory() as unit_of_work:
            asset_repository = self._asset_repository_factory(unit_of_work)
            details = await asset_repository.get_details(
                workspace_id=actor.workspace_id,
                asset_id=query.asset_id,
            )
            if details is None:
                raise AssetNotFoundError(parameters={"assetId": str(query.asset_id)})

        return await self._mapper.to_details_dto(details)
