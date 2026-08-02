"""Asset record to DTO mappers."""

from __future__ import annotations

from datetime import timedelta

from cloud_content_hub.application.assets.dto.responses import (
    AssetDetailsDto,
    AssetDto,
    AssetLifecycleStatusDto,
    AssetMediaDto,
    AssetTypeDto,
    AssetUsageDto,
    ScanStatusDto,
)
from cloud_content_hub.application.assets.interfaces.asset_repository import (
    AssetDetailsRecord,
    AssetRecord,
    AssetUsageRecord,
    ScanStatus,
)
from cloud_content_hub.application.shared.interfaces.object_storage import (
    IObjectStoragePort,
    StorageLocationRecord,
)


class AssetMapper:
    """Maps asset read models to response DTOs."""

    def __init__(self, storage: IObjectStoragePort | None = None) -> None:
        self._storage = storage

    async def to_dto(self, record: AssetRecord) -> AssetDto:
        """Map an asset record to a response DTO."""

        media_dto = await self._map_media(record)
        return AssetDto(
            id=record.id,
            version=record.version,
            created_at=record.created_at,
            updated_at=record.updated_at,
            asset_type=AssetTypeDto(record.asset_type.value),
            title=record.title,
            summary=record.summary,
            lifecycle_status=AssetLifecycleStatusDto(record.lifecycle_status.value),
            owner_id=record.owner_id,
            project_id=record.project_id,
            folder_id=record.folder_id,
            is_favorite=record.is_favorite,
            tag_ids=tuple(sorted(record.tag_ids)),
            media=media_dto,
        )

    async def to_details_dto(self, record: AssetDetailsRecord) -> AssetDetailsDto:
        """Map an extended asset record to a response DTO."""

        base = await self.to_dto(record.asset)
        return AssetDetailsDto(
            **base.model_dump(),
            version_count=record.version_count,
            publication_count=record.publication_count,
            collection_count=record.collection_count,
            comment_count=record.comment_count,
        )

    def to_usage_dto(self, record: AssetUsageRecord) -> AssetUsageDto:
        """Map an asset usage record to a response DTO."""

        return AssetUsageDto(
            asset_id=record.asset_id,
            publication_count=record.publication_count,
            collection_count=record.collection_count,
            relation_count=record.relation_count,
            can_delete=record.can_delete,
            blocking_reasons=record.blocking_reasons,
        )

    async def _map_media(self, record: AssetRecord) -> AssetMediaDto | None:
        if record.media is None:
            return None

        download_url: str | None = None
        if (
            self._storage is not None
            and record.media.scan_status == ScanStatus.CLEAN
            and record.media.storage_container
            and record.media.storage_blob_name
        ):
            download_url = await self._storage.generate_download_url(
                StorageLocationRecord(
                    container=record.media.storage_container,
                    blob_name=record.media.storage_blob_name,
                ),
                expires_in=timedelta(minutes=15),
            )
        return AssetMediaDto(
            id=record.id,
            version=record.version,
            created_at=record.created_at,
            updated_at=record.updated_at,
            mime_type=record.media.mime_type,
            byte_size=record.media.byte_size,
            checksum_sha256=record.media.checksum_sha256,
            scan_status=ScanStatusDto(record.media.scan_status.value),
            filename=record.media.filename,
            extracted_metadata=dict(record.media.extracted_metadata),
            download_url=download_url,
        )
