"""Object storage port for application orchestration."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Protocol


@dataclass(frozen=True, slots=True)
class StorageLocationRecord:
    """Provider-neutral blob location."""

    container: str
    blob_name: str


@dataclass(frozen=True, slots=True)
class UploadPayload:
    """Upload payload passed to the storage port."""

    location: StorageLocationRecord
    data: bytes
    content_type: str
    content_length: int
    filename: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)
    checksum_sha256: str | None = None
    overwrite: bool = False


@dataclass(frozen=True, slots=True)
class BlobMetadataRecord:
    """Stored blob metadata returned by the storage port."""

    location: StorageLocationRecord
    size: int
    content_type: str
    etag: str
    last_modified: datetime
    checksum_sha256: str | None = None


class IObjectStoragePort(Protocol):
    """Capability-oriented storage port consumed by application handlers."""

    async def upload(self, payload: UploadPayload) -> BlobMetadataRecord:
        """Upload bytes to the configured object store."""

    async def delete(
        self, location: StorageLocationRecord, *, expected_etag: str | None = None
    ) -> None:
        """Delete a blob from the object store."""

    async def generate_download_url(
        self,
        location: StorageLocationRecord,
        *,
        expires_in: timedelta,
    ) -> str:
        """Return a short-lived download URL for a blob."""

    async def exists(self, location: StorageLocationRecord) -> bool:
        """Return whether a blob exists at the given location."""
