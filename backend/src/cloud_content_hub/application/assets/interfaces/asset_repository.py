"""Asset repository port and read models."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Protocol
from uuid import UUID


class AssetType(StrEnum):
    ARTICLE = "article"
    VIDEO = "video"
    POSTER = "poster"
    THUMBNAIL = "thumbnail"


class AssetLifecycleStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class ScanStatus(StrEnum):
    PENDING = "pending"
    CLEAN = "clean"
    INFECTED = "infected"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class AssetMediaRecord:
    """Media metadata associated with an asset."""

    mime_type: str
    byte_size: int
    checksum_sha256: str
    scan_status: ScanStatus
    storage_container: str | None = None
    storage_blob_name: str | None = None
    filename: str | None = None
    extracted_metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AssetRecord:
    """Asset aggregate read model."""

    id: UUID
    workspace_id: UUID
    version: int
    created_at: datetime
    updated_at: datetime
    asset_type: AssetType
    title: str
    summary: str | None
    lifecycle_status: AssetLifecycleStatus
    owner_id: UUID | None
    project_id: UUID | None
    folder_id: UUID | None
    is_favorite: bool
    media: AssetMediaRecord | None
    tag_ids: frozenset[UUID] = frozenset()
    is_deleted: bool = False


@dataclass(frozen=True, slots=True)
class AssetDetailsRecord:
    """Extended asset read model with aggregate statistics."""

    asset: AssetRecord
    version_count: int
    publication_count: int
    collection_count: int
    comment_count: int


@dataclass(frozen=True, slots=True)
class AssetUsageRecord:
    """Asset dependency and reference summary."""

    asset_id: UUID
    publication_count: int
    collection_count: int
    relation_count: int
    can_delete: bool
    blocking_reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NewAsset:
    """Input for creating an asset aggregate."""

    workspace_id: UUID
    asset_type: AssetType
    title: str
    summary: str | None
    owner_id: UUID | None
    project_id: UUID | None
    folder_id: UUID | None
    created_by: UUID


@dataclass(frozen=True, slots=True)
class AssetSearchCriteria:
    """Structured asset search criteria."""

    workspace_id: UUID
    query: str | None = None
    asset_types: frozenset[AssetType] = frozenset()
    lifecycle_statuses: frozenset[AssetLifecycleStatus] = frozenset()
    owner_id: UUID | None = None
    project_id: UUID | None = None
    folder_id: UUID | None = None
    cursor: str | None = None
    limit: int = 25
    sort: str = "-updated_at"


@dataclass(frozen=True, slots=True)
class AssetSearchPage:
    """Cursor-paged asset search results."""

    items: tuple[AssetRecord, ...]
    next_cursor: str | None
    has_more: bool


class IAssetRepository(Protocol):
    """Repository port for content assets."""

    async def get_by_id(self, *, workspace_id: UUID, asset_id: UUID) -> AssetRecord | None:
        """Return one active asset scoped to the workspace."""

    async def get_deleted_by_id(self, *, workspace_id: UUID, asset_id: UUID) -> AssetRecord | None:
        """Return one soft-deleted asset scoped to the workspace."""

    async def create(self, asset: NewAsset) -> AssetRecord:
        """Persist a new asset aggregate."""

    async def attach_media(
        self,
        *,
        workspace_id: UUID,
        asset_id: UUID,
        media: AssetMediaRecord,
        expected_version: int,
        updated_by: UUID,
    ) -> AssetRecord:
        """Attach or replace media metadata for an asset."""

    async def soft_delete(
        self,
        *,
        workspace_id: UUID,
        asset_id: UUID,
        expected_version: int,
        updated_by: UUID,
    ) -> None:
        """Soft-delete an asset aggregate."""

    async def restore(
        self,
        *,
        workspace_id: UUID,
        asset_id: UUID,
        expected_version: int,
        updated_by: UUID,
    ) -> AssetRecord:
        """Restore a soft-deleted asset aggregate."""

    async def update_lifecycle_status(
        self,
        *,
        workspace_id: UUID,
        asset_id: UUID,
        lifecycle_status: AssetLifecycleStatus,
        expected_version: int,
        updated_by: UUID,
    ) -> AssetRecord:
        """Transition an asset lifecycle status."""

    async def move(
        self,
        *,
        workspace_id: UUID,
        asset_id: UUID,
        project_id: UUID | None,
        folder_id: UUID | None,
        expected_version: int,
        updated_by: UUID,
    ) -> AssetRecord:
        """Move an asset to a different project or folder within the workspace."""

    async def copy(
        self,
        *,
        workspace_id: UUID,
        source_asset_id: UUID,
        title: str,
        project_id: UUID | None,
        folder_id: UUID | None,
        created_by: UUID,
    ) -> AssetRecord:
        """Create a new asset copied from an existing asset."""

    async def set_tags(
        self,
        *,
        workspace_id: UUID,
        asset_id: UUID,
        tag_ids: frozenset[UUID],
        expected_version: int,
        updated_by: UUID,
    ) -> AssetRecord:
        """Replace the tag set associated with an asset."""

    async def find_by_checksum(
        self,
        *,
        workspace_id: UUID,
        checksum_sha256: str,
        byte_size: int,
    ) -> AssetRecord | None:
        """Return an active asset with matching content checksum, if any."""

    async def find_by_filename(
        self,
        *,
        workspace_id: UUID,
        filename: str,
        asset_type: AssetType,
    ) -> AssetRecord | None:
        """Return an active asset with the same filename and type, if any."""

    async def get_details(self, *, workspace_id: UUID, asset_id: UUID) -> AssetDetailsRecord | None:
        """Return extended asset details including usage statistics."""

    async def get_usage(self, *, workspace_id: UUID, asset_id: UUID) -> AssetUsageRecord | None:
        """Return asset dependency and reference summary."""

    async def search(self, criteria: AssetSearchCriteria) -> AssetSearchPage:
        """Search assets using structured filters and optional full-text query."""

    async def list_assets(
        self,
        *,
        workspace_id: UUID,
        asset_types: frozenset[AssetType],
        lifecycle_statuses: frozenset[AssetLifecycleStatus],
        owner_id: UUID | None,
        project_id: UUID | None,
        folder_id: UUID | None,
        cursor: str | None,
        limit: int,
        sort: str,
    ) -> AssetSearchPage:
        """List assets with structured filters."""
