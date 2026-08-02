"""Asset command definitions."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from cloud_content_hub.application.assets.dto.requests import (
    CopyAssetRequestDto,
    MoveAssetRequestDto,
    ReplaceAssetRequestDto,
    TagAssetRequestDto,
    UploadAssetRequestDto,
)


@dataclass(frozen=True, slots=True)
class UploadAssetCommand:
    """Command to upload a new asset."""

    request: UploadAssetRequestDto
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class ReplaceAssetCommand:
    """Command to replace an asset source file."""

    asset_id: UUID
    expected_version: int
    request: ReplaceAssetRequestDto
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class DeleteAssetCommand:
    """Command to soft-delete an asset."""

    asset_id: UUID
    expected_version: int


@dataclass(frozen=True, slots=True)
class RestoreAssetCommand:
    """Command to restore a soft-deleted asset."""

    asset_id: UUID
    expected_version: int


@dataclass(frozen=True, slots=True)
class ArchiveAssetCommand:
    """Command to archive an asset."""

    asset_id: UUID
    expected_version: int


@dataclass(frozen=True, slots=True)
class TagAssetCommand:
    """Command to replace an asset tag set."""

    asset_id: UUID
    expected_version: int
    request: TagAssetRequestDto


@dataclass(frozen=True, slots=True)
class MoveAssetCommand:
    """Command to move an asset within a workspace."""

    asset_id: UUID
    expected_version: int
    request: MoveAssetRequestDto


@dataclass(frozen=True, slots=True)
class CopyAssetCommand:
    """Command to copy an asset."""

    asset_id: UUID
    request: CopyAssetRequestDto
