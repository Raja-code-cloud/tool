"""Asset domain events raised by command handlers."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

if TYPE_CHECKING:
    from cloud_content_hub.application.assets.interfaces.asset_repository import AssetType


@dataclass(frozen=True, slots=True)
class AssetUploaded:
    """Raised when a new asset is created and media ingestion is queued."""

    workspace_id: UUID
    asset_id: UUID
    asset_type: AssetType
    actor_id: UUID
    checksum_sha256: str
    byte_size: int
    filename: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class AssetDeleted:
    """Raised when an asset is soft-deleted."""

    workspace_id: UUID
    asset_id: UUID
    actor_id: UUID
    version: int
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class AssetReplaced:
    """Raised when an asset source file replacement is queued."""

    workspace_id: UUID
    asset_id: UUID
    actor_id: UUID
    version: int
    checksum_sha256: str
    byte_size: int
    filename: str
    occurred_at: datetime


@dataclass(frozen=True, slots=True)
class AssetRestored:
    """Raised when a soft-deleted asset is restored."""

    workspace_id: UUID
    asset_id: UUID
    actor_id: UUID
    version: int
    occurred_at: datetime


AssetDomainEvent = AssetUploaded | AssetDeleted | AssetReplaced | AssetRestored

__all__ = [
    "AssetDeleted",
    "AssetDomainEvent",
    "AssetReplaced",
    "AssetRestored",
    "AssetUploaded",
]
