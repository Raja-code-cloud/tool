"""Duplicate asset detection orchestration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from cloud_content_hub.application.assets.exceptions.asset_errors import AssetDuplicateError
from cloud_content_hub.application.assets.interfaces.asset_repository import (
    AssetRecord,
    AssetType,
    IAssetRepository,
)


class DuplicatePolicy(StrEnum):
    """Workspace duplicate handling policy."""

    REJECT_CHECKSUM = "reject_checksum"
    REJECT_FILENAME = "reject_filename"


@dataclass(frozen=True, slots=True)
class DuplicateDetectionService:
    """Detects duplicate uploads within a workspace."""

    policy: DuplicatePolicy = DuplicatePolicy.REJECT_CHECKSUM

    async def ensure_unique_upload(
        self,
        repository: IAssetRepository,
        *,
        workspace_id: UUID,
        asset_type: AssetType,
        filename: str,
        checksum_sha256: str,
        byte_size: int,
    ) -> None:
        """Reject uploads that violate the configured duplicate policy."""

        if self.policy == DuplicatePolicy.REJECT_CHECKSUM:
            duplicate = await repository.find_by_checksum(
                workspace_id=workspace_id,
                checksum_sha256=checksum_sha256,
                byte_size=byte_size,
            )
            if duplicate is not None:
                raise AssetDuplicateError(
                    detail="An asset with identical content already exists in this workspace.",
                    parameters={"existingAssetId": str(duplicate.id)},
                )
            return

        duplicate = await repository.find_by_filename(
            workspace_id=workspace_id,
            filename=filename,
            asset_type=asset_type,
        )
        if duplicate is not None:
            raise AssetDuplicateError(
                detail="An asset with the same filename already exists in this workspace.",
                parameters={"existingAssetId": str(duplicate.id)},
            )

    async def find_checksum_duplicate(
        self,
        repository: IAssetRepository,
        *,
        workspace_id: UUID,
        checksum_sha256: str,
        byte_size: int,
        exclude_asset_id: UUID | None = None,
    ) -> AssetRecord | None:
        """Return a duplicate asset by checksum, optionally excluding one asset."""

        duplicate = await repository.find_by_checksum(
            workspace_id=workspace_id,
            checksum_sha256=checksum_sha256,
            byte_size=byte_size,
        )
        if duplicate is None:
            return None
        if exclude_asset_id is not None and duplicate.id == exclude_asset_id:
            return None
        return duplicate
