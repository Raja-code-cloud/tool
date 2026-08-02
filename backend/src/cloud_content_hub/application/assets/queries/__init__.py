"""Asset query definitions."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from cloud_content_hub.application.assets.interfaces.asset_repository import (
    AssetLifecycleStatus,
    AssetType,
)


@dataclass(frozen=True, slots=True)
class GetAssetQuery:
    """Query to retrieve one asset."""

    asset_id: UUID


@dataclass(frozen=True, slots=True)
class GetAssetDetailsQuery:
    """Query to retrieve extended asset details."""

    asset_id: UUID


@dataclass(frozen=True, slots=True)
class SearchAssetsQuery:
    """Query to search assets."""

    query: str
    asset_types: frozenset[AssetType] = frozenset()
    lifecycle_statuses: frozenset[AssetLifecycleStatus] = frozenset()
    cursor: str | None = None
    limit: int = 25
    sort: str = "relevance"


@dataclass(frozen=True, slots=True)
class ListAssetsQuery:
    """Query to list assets with structured filters."""

    asset_types: frozenset[AssetType] = frozenset()
    lifecycle_statuses: frozenset[AssetLifecycleStatus] = frozenset()
    owner_id: UUID | None = None
    project_id: UUID | None = None
    folder_id: UUID | None = None
    cursor: str | None = None
    limit: int = 25
    sort: str = "-updated_at"


@dataclass(frozen=True, slots=True)
class AssetUsageQuery:
    """Query to retrieve asset dependency summary."""

    asset_id: UUID
