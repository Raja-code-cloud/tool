"""Tag asset command handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.assets.commands import TagAssetCommand
from cloud_content_hub.application.assets.dto.responses import AssetDto
from cloud_content_hub.application.assets.exceptions.asset_errors import AssetNotFoundError
from cloud_content_hub.application.assets.interfaces.asset_repository import IAssetRepository
from cloud_content_hub.application.assets.mappers.asset_mapper import AssetMapper
from cloud_content_hub.application.assets.validators.asset_validator import validate_tagging
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.core.errors import VersionConflictError


class TagAssetHandler:
    """Orchestrates replacement of an asset tag set."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        asset_repository_factory: Callable[[IUnitOfWork], IAssetRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._asset_repository_factory = asset_repository_factory
        self._mapper = AssetMapper()

    async def handle(self, actor: ActorContext, command: TagAssetCommand) -> AssetDto:
        require_permission(actor, "assets:write")

        async with self._unit_of_work_factory() as unit_of_work:
            asset_repository = self._asset_repository_factory(unit_of_work)
            asset = await asset_repository.get_by_id(
                workspace_id=actor.workspace_id,
                asset_id=command.asset_id,
            )
            if asset is None:
                raise AssetNotFoundError(parameters={"assetId": str(command.asset_id)})
            if asset.version != command.expected_version:
                raise VersionConflictError(
                    parameters={
                        "assetId": str(command.asset_id),
                        "expectedVersion": command.expected_version,
                    },
                )

            validate_tagging(asset)
            tagged = await asset_repository.set_tags(
                workspace_id=actor.workspace_id,
                asset_id=command.asset_id,
                tag_ids=frozenset(command.request.tag_ids),
                expected_version=command.expected_version,
                updated_by=actor.user_id,
            )
            await unit_of_work.flush()

        return await self._mapper.to_dto(tagged)
