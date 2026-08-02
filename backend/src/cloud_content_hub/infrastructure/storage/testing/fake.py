"""Deterministic in-memory implementation for unit and contract tests."""

import hashlib
from collections.abc import AsyncIterator, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from urllib.parse import quote

from cloud_content_hub.infrastructure.storage.exceptions import (
    BlobAlreadyExistsError,
    BlobNotFoundError,
    StorageConditionError,
)
from cloud_content_hub.infrastructure.storage.models import (
    BlobMetadata,
    BlobPage,
    DownloadRequest,
    HealthStatus,
    SasPermission,
    StorageLocation,
    UploadRequest,
)


@dataclass(slots=True)
class _StoredBlob:
    data: bytes
    metadata: BlobMetadata


class InMemoryStorageProvider:
    def __init__(self, *, base_url: str = "https://storage.test") -> None:
        self._base_url = base_url.rstrip("/")
        self._blobs: dict[StorageLocation, _StoredBlob] = {}

    async def upload(self, request: UploadRequest) -> BlobMetadata:
        if request.location in self._blobs and not request.overwrite:
            raise BlobAlreadyExistsError("Blob already exists")
        if request.expected_etag is not None:
            self._require_etag(request.location, request.expected_etag)
        data = (
            request.data
            if isinstance(request.data, bytes)
            else b"".join([chunk async for chunk in request.data])
        )
        digest = hashlib.sha256(data).hexdigest()
        etag = f'"{digest}"'
        now = datetime(2025, 1, 1, tzinfo=UTC)
        metadata = BlobMetadata(
            location=request.location,
            size=len(data),
            content_type=request.content_type,
            etag=etag,
            last_modified=now,
            metadata=dict(request.metadata),
            tags=dict(request.tags),
            checksum_sha256=digest,
            content_disposition=request.content_disposition,
            content_encoding=request.content_encoding,
        )
        self._blobs[request.location] = _StoredBlob(data, metadata)
        if request.progress is not None:
            await request.progress(len(data), request.content_length)
        return metadata

    async def download(self, request: DownloadRequest) -> AsyncIterator[bytes]:
        stored = self._get(request.location)
        if request.expected_etag is not None:
            self._require_etag(request.location, request.expected_etag)
        start = request.offset or 0
        end = None if request.length is None else start + request.length
        data = stored.data[start:end]
        if request.progress is not None:
            await request.progress(len(data), request.length)
        yield data

    async def delete(self, location: StorageLocation, *, expected_etag: str | None = None) -> None:
        if expected_etag is not None:
            self._require_etag(location, expected_etag)
        self._get(location)
        del self._blobs[location]

    async def exists(self, location: StorageLocation) -> bool:
        return location in self._blobs

    async def copy(
        self,
        source: StorageLocation,
        destination: StorageLocation,
        *,
        overwrite: bool = False,
    ) -> BlobMetadata:
        stored = self._get(source)
        request = UploadRequest(
            location=destination,
            data=stored.data,
            content_type=stored.metadata.content_type,
            metadata=stored.metadata.metadata,
            tags=stored.metadata.tags,
            overwrite=overwrite,
        )
        return await self.upload(request)

    async def move(
        self,
        source: StorageLocation,
        destination: StorageLocation,
        *,
        overwrite: bool = False,
    ) -> BlobMetadata:
        result = await self.copy(source, destination, overwrite=overwrite)
        await self.delete(source)
        return result

    async def list(
        self,
        container: str,
        *,
        prefix: str = "",
        limit: int = 100,
        continuation_token: str | None = None,
    ) -> BlobPage:
        matching = sorted(
            (
                stored.metadata
                for location, stored in self._blobs.items()
                if location.container == container and location.blob_name.startswith(prefix)
            ),
            key=lambda item: item.location.blob_name,
        )
        offset = int(continuation_token or "0")
        items = tuple(matching[offset : offset + limit])
        next_offset = offset + len(items)
        token = str(next_offset) if next_offset < len(matching) else None
        return BlobPage(items, token)

    async def generate_sas_url(
        self,
        location: StorageLocation,
        permissions: Sequence[SasPermission],
        *,
        expires_in: timedelta,
    ) -> str:
        self._get(location)
        permission_text = ",".join(sorted(permission.value for permission in permissions))
        ttl = int(expires_in.total_seconds())
        return f"{self.get_url(location)}?permissions={permission_text}&ttl={ttl}"

    async def get_metadata(self, location: StorageLocation) -> BlobMetadata:
        return self._get(location).metadata

    async def set_metadata(
        self,
        location: StorageLocation,
        metadata: Mapping[str, str],
        *,
        expected_etag: str | None = None,
    ) -> BlobMetadata:
        stored = self._get(location)
        if expected_etag is not None:
            self._require_etag(location, expected_etag)
        updated = BlobMetadata(
            location=stored.metadata.location,
            size=stored.metadata.size,
            content_type=stored.metadata.content_type,
            etag=stored.metadata.etag,
            last_modified=stored.metadata.last_modified,
            metadata=dict(metadata),
            tags=stored.metadata.tags,
            checksum_sha256=stored.metadata.checksum_sha256,
            content_disposition=stored.metadata.content_disposition,
            content_encoding=stored.metadata.content_encoding,
        )
        stored.metadata = updated
        return updated

    def get_url(self, location: StorageLocation) -> str:
        return f"{self._base_url}/{location.container}/{quote(location.blob_name)}"

    async def health_check(self) -> HealthStatus:
        return HealthStatus(healthy=True, latency_ms=0, detail="in-memory")

    async def close(self) -> None:
        return None

    def _get(self, location: StorageLocation) -> _StoredBlob:
        try:
            return self._blobs[location]
        except KeyError as error:
            raise BlobNotFoundError("Blob was not found") from error

    def _require_etag(self, location: StorageLocation, expected: str) -> None:
        if self._get(location).metadata.etag != expected:
            raise StorageConditionError("Blob ETag condition failed")
