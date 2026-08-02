"""Restore asset command handler."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from cloud_content_hub.application.assets.commands import RestoreAssetCommand
from cloud_content_hub.application.assets.dto.responses import AssetDto
from cloud_content_hub.application.assets.events import AssetRestored
from cloud_content_hub.application.assets.exceptions.asset_errors import AssetNotFoundError
from cloud_content_hub.application.assets.interfaces.asset_repository import IAssetRepository
from cloud_content_hub.application.assets.interfaces.event_publisher import IAssetEventPublisher
from cloud_content_hub.application.assets.mappers.asset_mapper import AssetMapper
from cloud_content_hub.application.assets.validators.asset_validator import validate_restore
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.core.errors import VersionConflictError


class RestoreAssetHandler:
    """Orchestrates restoration of a soft-deleted asset."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        asset_repository_factory: Callable[[IUnitOfWork], IAssetRepository],
        event_publisher: IAssetEventPublisher | None = None,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._asset_repository_factory = asset_repository_factory
        self._event_publisher = event_publisher
        self._mapper = AssetMapper()

    async def handle(self, actor: ActorContext, command: RestoreAssetCommand) -> AssetDto:
        require_permission(actor, "assets:write")

        async with self._unit_of_work_factory() as unit_of_work:
            asset_repository = self._asset_repository_factory(unit_of_work)
            asset = await asset_repository.get_deleted_by_id(
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

            validate_restore(asset)
            restored = await asset_repository.restore(
                workspace_id=actor.workspace_id,
                asset_id=command.asset_id,
                expected_version=command.expected_version,
                updated_by=actor.user_id,
            )

            if self._event_publisher is not None:
                await self._event_publisher.publish(
                    AssetRestored(
                        workspace_id=actor.workspace_id,
                        asset_id=restored.id,
                        actor_id=actor.user_id,
                        version=restored.version,
                        occurred_at=datetime.now(tz=UTC),
                    ),
                    unit_of_work=unit_of_work,
                )

            await unit_of_work.flush()

        return await self._mapper.to_dto(restored)
