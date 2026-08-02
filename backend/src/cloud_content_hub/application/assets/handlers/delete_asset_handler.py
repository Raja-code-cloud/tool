"""Delete asset command handler."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from cloud_content_hub.application.assets.commands import DeleteAssetCommand
from cloud_content_hub.application.assets.events import AssetDeleted
from cloud_content_hub.application.assets.exceptions.asset_errors import AssetNotFoundError
from cloud_content_hub.application.assets.interfaces.asset_repository import IAssetRepository
from cloud_content_hub.application.assets.interfaces.event_publisher import IAssetEventPublisher
from cloud_content_hub.application.assets.validators.asset_validator import validate_deletion
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.core.errors import VersionConflictError


class DeleteAssetHandler:
    """Orchestrates asset soft-deletion."""

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

    async def handle(self, actor: ActorContext, command: DeleteAssetCommand) -> None:
        require_permission(actor, "assets:delete")

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

            validate_deletion(asset)
            await asset_repository.soft_delete(
                workspace_id=actor.workspace_id,
                asset_id=command.asset_id,
                expected_version=command.expected_version,
                updated_by=actor.user_id,
            )

            if self._event_publisher is not None:
                await self._event_publisher.publish(
                    AssetDeleted(
                        workspace_id=actor.workspace_id,
                        asset_id=command.asset_id,
                        actor_id=actor.user_id,
                        version=command.expected_version,
                        occurred_at=datetime.now(tz=UTC),
                    ),
                    unit_of_work=unit_of_work,
                )

            await unit_of_work.flush()
