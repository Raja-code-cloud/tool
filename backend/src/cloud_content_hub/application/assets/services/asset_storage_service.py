"""Storage orchestration for asset media."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import PurePosixPath
from uuid import UUID

from cloud_content_hub.application.assets.interfaces.asset_repository import AssetType
from cloud_content_hub.application.shared.interfaces.object_storage import StorageLocationRecord

_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
_SAFE_FILENAME = re.compile(r"^[A-Za-z0-9._-]{1,255}$")

_CONTAINER_BY_TYPE: dict[AssetType, str] = {
    AssetType.POSTER: "posters",
    AssetType.ARTICLE: "articles",
    AssetType.VIDEO: "videos",
    AssetType.THUMBNAIL: "thumbnails",
}


@dataclass(frozen=True, slots=True)
class StorageTarget:
    """Resolved storage destination for an asset upload."""

    location: StorageLocationRecord
    blob_name: str
    container: str


class AssetStorageService:
    """Builds provider-neutral storage locations for asset media."""

    def resolve_upload_target(
        self,
        *,
        workspace_id: UUID,
        actor_id: UUID,
        asset_type: AssetType,
        asset_id: UUID,
        filename: str,
        created_at: datetime | None = None,
    ) -> StorageTarget:
        """Resolve the container and blob path for a new asset upload."""

        container = _CONTAINER_BY_TYPE[asset_type]
        safe_filename = _sanitize_filename(filename)
        blob_name = _build_blob_name(
            tenant_id=_workspace_slug(workspace_id),
            user_id=_workspace_slug(actor_id),
            asset_type=asset_type,
            object_id=asset_id,
            filename=safe_filename,
            created_at=created_at or datetime.now(tz=UTC),
        )
        return StorageTarget(
            location=StorageLocationRecord(container=container, blob_name=blob_name),
            blob_name=blob_name,
            container=container,
        )


def _workspace_slug(value: UUID) -> str:
    slug = value.hex[:32]
    if not _IDENTIFIER.fullmatch(slug):
        msg = "Unable to derive a storage tenant identifier."
        raise ValueError(msg)
    return slug


def _sanitize_filename(filename: str) -> str:
    normalized = PurePosixPath(filename.replace("\\", "/")).name
    if not normalized or normalized != filename or not _SAFE_FILENAME.fullmatch(normalized):
        msg = "Filename contains unsafe characters or path segments."
        raise ValueError(msg)
    return normalized


def _build_blob_name(
    *,
    tenant_id: str,
    user_id: str,
    asset_type: AssetType,
    object_id: UUID,
    filename: str,
    created_at: datetime,
) -> str:
    instant = created_at.astimezone(UTC)
    return f"{tenant_id}/{user_id}/{instant:%Y/%m/%d}/{asset_type.value}/{object_id.hex}/{filename}"
