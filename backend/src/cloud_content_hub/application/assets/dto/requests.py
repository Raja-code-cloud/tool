"""Asset request DTOs."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import Field

from cloud_content_hub.application.shared.dto.base import ApplicationDto


class AssetTypeDto(StrEnum):
    ARTICLE = "article"
    VIDEO = "video"
    POSTER = "poster"
    THUMBNAIL = "thumbnail"


class UploadAssetRequestDto(ApplicationDto):
    """Request payload for uploading a new asset."""

    asset_type: AssetTypeDto
    title: str = Field(min_length=1, max_length=300)
    summary: str | None = None
    project_id: UUID | None = None
    folder_id: UUID | None = None
    checksum_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    filename: str = Field(min_length=1, max_length=255)
    content_type: str
    content_length: int = Field(ge=1)
    file_data: bytes


class ReplaceAssetRequestDto(ApplicationDto):
    """Request payload for replacing an asset source file."""

    checksum_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    filename: str = Field(min_length=1, max_length=255)
    content_type: str
    content_length: int = Field(ge=1)
    file_data: bytes


class TagAssetRequestDto(ApplicationDto):
    """Request payload for replacing an asset tag set."""

    tag_ids: tuple[UUID, ...] = Field(default_factory=tuple)


class MoveAssetRequestDto(ApplicationDto):
    """Request payload for moving an asset within a workspace."""

    project_id: UUID | None = None
    folder_id: UUID | None = None


class CopyAssetRequestDto(ApplicationDto):
    """Request payload for copying an asset."""

    title: str = Field(min_length=1, max_length=300)
    project_id: UUID | None = None
    folder_id: UUID | None = None
