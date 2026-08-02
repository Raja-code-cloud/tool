"""Asset usage query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.assets.dto.responses import AssetUsageDto
from cloud_content_hub.application.assets.exceptions.asset_errors import AssetNotFoundError
from cloud_content_hub.application.assets.interfaces.asset_repository import IAssetRepository
from cloud_content_hub.application.assets.mappers.asset_mapper import AssetMapper
from cloud_content_hub.application.assets.queries import AssetUsageQuery
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class AssetUsageHandler:
    """Retrieves asset dependency and reference summary."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        asset_repository_factory: Callable[[IUnitOfWork], IAssetRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._asset_repository_factory = asset_repository_factory
        self._mapper = AssetMapper()

    async def handle(self, actor: ActorContext, query: AssetUsageQuery) -> AssetUsageDto:
        require_permission(actor, "assets:read")

        async with self._unit_of_work_factory() as unit_of_work:
            asset_repository = self._asset_repository_factory(unit_of_work)
            usage = await asset_repository.get_usage(
                workspace_id=actor.workspace_id,
                asset_id=query.asset_id,
            )
            if usage is None:
                raise AssetNotFoundError(parameters={"assetId": str(query.asset_id)})

        return self._mapper.to_usage_dto(usage)
