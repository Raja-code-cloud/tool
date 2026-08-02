"""Application-owned asynchronous storage port."""

from collections.abc import AsyncIterator, Mapping, Sequence
from datetime import timedelta
from typing import Protocol

from cloud_content_hub.infrastructure.storage.models import (
    BlobMetadata,
    BlobPage,
    DownloadRequest,
    HealthStatus,
    SasPermission,
    StorageLocation,
    UploadRequest,
)


class StorageProvider(Protocol):
    async def upload(self, request: UploadRequest) -> BlobMetadata: ...

    def download(self, request: DownloadRequest) -> AsyncIterator[bytes]: ...

    async def delete(
        self, location: StorageLocation, *, expected_etag: str | None = None
    ) -> None: ...

    async def exists(self, location: StorageLocation) -> bool: ...

    async def copy(
        self,
        source: StorageLocation,
        destination: StorageLocation,
        *,
        overwrite: bool = False,
    ) -> BlobMetadata: ...

    async def move(
        self,
        source: StorageLocation,
        destination: StorageLocation,
        *,
        overwrite: bool = False,
    ) -> BlobMetadata: ...

    async def list(
        self,
        container: str,
        *,
        prefix: str = "",
        limit: int = 100,
        continuation_token: str | None = None,
    ) -> BlobPage: ...

    async def generate_sas_url(
        self,
        location: StorageLocation,
        permissions: Sequence[SasPermission],
        *,
        expires_in: timedelta,
    ) -> str: ...

    async def get_metadata(self, location: StorageLocation) -> BlobMetadata: ...

    async def set_metadata(
        self,
        location: StorageLocation,
        metadata: Mapping[str, str],
        *,
        expected_etag: str | None = None,
    ) -> BlobMetadata: ...

    def get_url(self, location: StorageLocation) -> str: ...

    async def health_check(self) -> HealthStatus: ...

    async def close(self) -> None: ...
