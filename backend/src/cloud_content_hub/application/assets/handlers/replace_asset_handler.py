"""Replace asset command handler."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

from cloud_content_hub.application.assets.commands import ReplaceAssetCommand
from cloud_content_hub.application.assets.events import AssetReplaced
from cloud_content_hub.application.assets.exceptions.asset_errors import (
    AssetDuplicateError,
    AssetNotFoundError,
)
from cloud_content_hub.application.assets.interfaces.asset_repository import (
    AssetMediaRecord,
    IAssetRepository,
    ScanStatus,
)
from cloud_content_hub.application.assets.interfaces.event_publisher import IAssetEventPublisher
from cloud_content_hub.application.assets.interfaces.virus_scan_hook import (
    IVirusScanHook,
    VirusScanRequest,
)
from cloud_content_hub.application.assets.services.asset_metadata_service import (
    AssetMetadataService,
)
from cloud_content_hub.application.assets.services.duplicate_detection_service import (
    DuplicateDetectionService,
)
from cloud_content_hub.application.assets.validators.asset_validator import validate_replace_request
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.dto.base import OperationDto
from cloud_content_hub.application.shared.interfaces.job_queue import (
    IBackgroundJobRepository,
    JobQueueName,
    NewBackgroundJob,
)
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.application.shared.mappers.operation_mapper import map_upload_operation
from cloud_content_hub.core.errors import IdempotencyConflictError, VersionConflictError


class ReplaceAssetHandler:
    """Orchestrates asset file replacement."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        asset_repository_factory: Callable[[IUnitOfWork], IAssetRepository],
        job_repository_factory: Callable[[IUnitOfWork], IBackgroundJobRepository],
        event_publisher: IAssetEventPublisher | None = None,
        metadata_service: AssetMetadataService | None = None,
        duplicate_detection: DuplicateDetectionService | None = None,
        virus_scan_hook: IVirusScanHook | None = None,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._asset_repository_factory = asset_repository_factory
        self._job_repository_factory = job_repository_factory
        self._event_publisher = event_publisher
        self._metadata_service = metadata_service or AssetMetadataService()
        self._duplicate_detection = duplicate_detection or DuplicateDetectionService()
        self._virus_scan_hook = virus_scan_hook

    async def handle(self, actor: ActorContext, command: ReplaceAssetCommand) -> OperationDto:
        require_permission(actor, "assets:write")

        async with self._unit_of_work_factory() as unit_of_work:
            job_repository = self._job_repository_factory(unit_of_work)
            existing = await job_repository.get_by_idempotency_key(
                workspace_id=actor.workspace_id,
                job_type="asset_replace",
                idempotency_key=command.idempotency_key,
            )
            if existing is not None:
                if existing.resource_id != command.asset_id:
                    raise IdempotencyConflictError(
                        detail="Idempotency key was reused with a different replace request.",
                    )
                return map_upload_operation(existing)

            asset_repository = self._asset_repository_factory(unit_of_work)
            asset = await asset_repository.get_by_id(
                workspace_id=actor.workspace_id,
                asset_id=command.asset_id,
            )
            if asset is None:
                raise AssetNotFoundError(
                    parameters={"assetId": str(command.asset_id)},
                )
            if asset.version != command.expected_version:
                raise VersionConflictError(
                    parameters={
                        "assetId": str(command.asset_id),
                        "expectedVersion": command.expected_version,
                    },
                )

            validate_replace_request(asset, command.request)
            extracted = self._metadata_service.extract(
                asset_type=asset.asset_type,
                filename=command.request.filename,
                content_type=command.request.content_type,
                file_data=command.request.file_data,
                checksum_sha256=command.request.checksum_sha256,
            )

            duplicate = await self._duplicate_detection.find_checksum_duplicate(
                asset_repository,
                workspace_id=actor.workspace_id,
                checksum_sha256=extracted.checksum_sha256,
                byte_size=command.request.content_length,
                exclude_asset_id=asset.id,
            )
            if duplicate is not None:
                raise AssetDuplicateError(
                    detail="Another asset with identical content already exists in this workspace.",
                    parameters={"existingAssetId": str(duplicate.id)},
                )

            if self._virus_scan_hook is not None:
                await self._virus_scan_hook.validate_acceptance(
                    VirusScanRequest(
                        workspace_id=actor.workspace_id,
                        asset_id=asset.id,
                        filename=command.request.filename,
                        content_type=command.request.content_type,
                        byte_size=command.request.content_length,
                        checksum_sha256=extracted.checksum_sha256,
                    )
                )

            updated = await asset_repository.attach_media(
                workspace_id=actor.workspace_id,
                asset_id=asset.id,
                media=AssetMediaRecord(
                    mime_type=command.request.content_type,
                    byte_size=command.request.content_length,
                    checksum_sha256=extracted.checksum_sha256,
                    scan_status=ScanStatus.PENDING,
                    filename=command.request.filename,
                    extracted_metadata=extracted.values,
                ),
                expected_version=command.expected_version,
                updated_by=actor.user_id,
            )

            job = await job_repository.create(
                NewBackgroundJob(
                    workspace_id=actor.workspace_id,
                    job_type="asset_replace",
                    queue_name=JobQueueName.MEDIA,
                    resource_type="asset",
                    resource_id=updated.id,
                    idempotency_key=command.idempotency_key,
                    created_by=actor.user_id,
                )
            )

            if self._event_publisher is not None:
                await self._event_publisher.publish(
                    AssetReplaced(
                        workspace_id=actor.workspace_id,
                        asset_id=updated.id,
                        actor_id=actor.user_id,
                        version=updated.version,
                        checksum_sha256=extracted.checksum_sha256,
                        byte_size=command.request.content_length,
                        filename=command.request.filename,
                        occurred_at=datetime.now(tz=UTC),
                    ),
                    unit_of_work=unit_of_work,
                )

            await unit_of_work.flush()

        return map_upload_operation(job)
