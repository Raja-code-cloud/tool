"""Asset response DTOs."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from pydantic import Field

from cloud_content_hub.application.shared.dto.base import ApplicationDto, ResourceBaseDto


class AssetTypeDto(StrEnum):
    ARTICLE = "article"
    VIDEO = "video"
    POSTER = "poster"
    THUMBNAIL = "thumbnail"


class AssetLifecycleStatusDto(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ScanStatusDto(StrEnum):
    PENDING = "pending"
    CLEAN = "clean"
    INFECTED = "infected"
    FAILED = "failed"


class AssetMediaDto(ResourceBaseDto):
    """Media metadata returned with an asset."""

    mime_type: str
    byte_size: int = Field(ge=0)
    checksum_sha256: str
    scan_status: ScanStatusDto
    filename: str | None = None
    extracted_metadata: dict[str, str] = Field(default_factory=dict)
    download_url: str | None = None


class AssetDto(ResourceBaseDto):
    """Asset projection returned by query handlers."""

    asset_type: AssetTypeDto
    title: str
    summary: str | None
    lifecycle_status: AssetLifecycleStatusDto
    owner_id: UUID | None
    project_id: UUID | None = None
    folder_id: UUID | None = None
    is_favorite: bool
    tag_ids: tuple[UUID, ...] = Field(default_factory=tuple)
    media: AssetMediaDto | None = None


class AssetDetailsDto(AssetDto):
    """Extended asset projection with aggregate statistics."""

    version_count: int = Field(ge=0)
    publication_count: int = Field(ge=0)
    collection_count: int = Field(ge=0)
    comment_count: int = Field(ge=0)


class AssetUsageDto(ApplicationDto):
    """Asset dependency and reference summary."""

    asset_id: UUID
    publication_count: int = Field(ge=0)
    collection_count: int = Field(ge=0)
    relation_count: int = Field(ge=0)
    can_delete: bool
    blocking_reasons: tuple[str, ...] = Field(default_factory=tuple)
