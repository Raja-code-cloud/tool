"""Azure implementation of the asynchronous storage port."""

import time
from collections.abc import AsyncIterator, Awaitable, Callable, Mapping, Sequence
from datetime import timedelta
from urllib.parse import quote

import structlog
from azure.core import MatchConditions
from azure.core.async_paging import AsyncPageIterator
from azure.storage.blob import BlobProperties, ContentSettings
from azure.storage.blob.aio import BlobClient, BlobServiceClient

from cloud_content_hub.infrastructure.storage.azure.blob_service import (
    to_metadata,
    translate_azure_error,
)
from cloud_content_hub.infrastructure.storage.azure.client import create_blob_service_client
from cloud_content_hub.infrastructure.storage.azure.containers import (
    ensure_private_containers,
    validate_container_name,
)
from cloud_content_hub.infrastructure.storage.azure.sas import generate_user_delegation_sas
from cloud_content_hub.infrastructure.storage.azure.streaming import (
    iter_download,
    validated_upload_stream,
)
from cloud_content_hub.infrastructure.storage.config import AzureStorageConfig
from cloud_content_hub.infrastructure.storage.exceptions import (
    BlobAlreadyExistsError,
    SASGenerationFailedError,
    StorageValidationError,
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
from cloud_content_hub.infrastructure.storage.utils import sanitize_metadata
from cloud_content_hub.infrastructure.storage.validators.checksum import (
    sha256_hex,
    validate_checksum,
)
from cloud_content_hub.infrastructure.storage.validators.filename import validate_blob_name
from cloud_content_hub.infrastructure.storage.validators.mime import validate_mime_type
from cloud_content_hub.infrastructure.storage.validators.size import (
    validate_not_empty,
    validate_size,
)

CircuitBreakerHook = Callable[[str, bool], Awaitable[None]]


class AzureBlobStorageProvider:
    def __init__(
        self,
        config: AzureStorageConfig,
        *,
        client: BlobServiceClient | None = None,
        circuit_breaker_hook: CircuitBreakerHook | None = None,
    ) -> None:
        self._config = config
        self._client = client or create_blob_service_client(config)
        self._circuit_breaker_hook = circuit_breaker_hook
        self._logger = structlog.get_logger(__name__)

    async def initialize(self) -> None:
        if self._config.auto_create_containers:
            await ensure_private_containers(self._client, self._config.containers)

    async def upload(self, request: UploadRequest) -> BlobMetadata:
        started = time.perf_counter()
        self._validate_location(request.location)
        content_type = validate_mime_type(request.content_type)
        metadata = sanitize_metadata(request.metadata)
        if request.content_length is not None:
            validate_size(request.content_length, self._config.max_size_bytes)
            validate_not_empty(request.content_length)
        checksum = validate_checksum(request.checksum_sha256) if request.checksum_sha256 else None
        if isinstance(request.data, bytes):
            validate_size(len(request.data), self._config.max_size_bytes)
            validate_not_empty(len(request.data))
            checksum = checksum or sha256_hex(request.data)
            data: bytes | AsyncIterator[bytes] = request.data
        else:
            data = validated_upload_stream(
                request.data,
                max_size_bytes=self._config.max_size_bytes,
                expected_checksum=checksum,
                progress=request.progress,
                total=request.content_length,
            )
        metadata["checksum_sha256"] = checksum or ""
        content_settings = ContentSettings(
            content_type=content_type,
            content_disposition=request.content_disposition,
            content_encoding=request.content_encoding,
            cache_control=request.cache_control,
        )
        blob = self._blob(request.location)
        try:
            if request.expected_etag:
                await blob.upload_blob(
                    data,
                    overwrite=request.overwrite,
                    metadata=metadata,
                    tags=dict(request.tags),
                    content_settings=content_settings,
                    max_concurrency=1,
                    length=request.content_length,
                    etag=request.expected_etag,
                    match_condition=MatchConditions.IfNotModified,
                )
            else:
                await blob.upload_blob(
                    data,
                    overwrite=request.overwrite,
                    metadata=metadata,
                    tags=dict(request.tags),
                    content_settings=content_settings,
                    max_concurrency=1,
                    length=request.content_length,
                )
            result = to_metadata(request.location, await blob.get_blob_properties())
            await self._log_operation(
                "upload", request.location, result.size, started, success=True
            )
            return result
        except Exception as error:
            await self._log_operation("upload", request.location, None, started, success=False)
            raise translate_azure_error(error, request.location, operation="upload") from error

    async def download(self, request: DownloadRequest) -> AsyncIterator[bytes]:
        started = time.perf_counter()
        self._validate_location(request.location)
        blob = self._blob(request.location)
        try:
            if request.expected_etag:
                stream = await blob.download_blob(
                    offset=request.offset,
                    length=request.length,
                    etag=request.expected_etag,
                    match_condition=MatchConditions.IfNotModified,
                )
            else:
                stream = await blob.download_blob(
                    offset=request.offset,
                    length=request.length,
                )
        except Exception as error:
            await self._log_operation(
                "download", request.location, request.length, started, success=False
            )
            raise translate_azure_error(error, request.location, operation="download") from error

        try:
            async for chunk in iter_download(
                stream,
                progress=request.progress,
                total=request.length,
            ):
                yield chunk
        except Exception as error:
            await self._log_operation(
                "download", request.location, request.length, started, success=False
            )
            raise translate_azure_error(error, request.location, operation="download") from error
        await self._log_operation(
            "download", request.location, request.length, started, success=True
        )

    async def delete(self, location: StorageLocation, *, expected_etag: str | None = None) -> None:
        started = time.perf_counter()
        self._validate_location(location)
        blob = self._blob(location)
        try:
            if expected_etag:
                await blob.delete_blob(
                    delete_snapshots="include",
                    etag=expected_etag,
                    match_condition=MatchConditions.IfNotModified,
                )
            else:
                await blob.delete_blob(delete_snapshots="include")
            await self._log_operation("delete", location, None, started, success=True)
        except Exception as error:
            await self._log_operation("delete", location, None, started, success=False)
            raise translate_azure_error(error, location) from error

    async def exists(self, location: StorageLocation) -> bool:
        self._validate_location(location)
        try:
            return await self._blob(location).exists()
        except Exception as error:
            raise translate_azure_error(error, location) from error

    async def copy(
        self,
        source: StorageLocation,
        destination: StorageLocation,
        *,
        overwrite: bool = False,
    ) -> BlobMetadata:
        self._validate_location(source)
        self._validate_location(destination)
        target = self._blob(destination)
        if not overwrite and await target.exists():
            raise BlobAlreadyExistsError("Destination blob already exists")
        try:
            await target.start_copy_from_url(self.get_url(source), requires_sync=True)
            return to_metadata(destination, await target.get_blob_properties())
        except Exception as error:
            raise translate_azure_error(error, destination) from error

    async def move(
        self,
        source: StorageLocation,
        destination: StorageLocation,
        *,
        overwrite: bool = False,
    ) -> BlobMetadata:
        copied = await self.copy(source, destination, overwrite=overwrite)
        await self.delete(source)
        return copied

    async def list(
        self,
        container: str,
        *,
        prefix: str = "",
        limit: int = 100,
        continuation_token: str | None = None,
    ) -> BlobPage:
        self._validate_container(container)
        if not 1 <= limit <= 1000:
            raise StorageValidationError("List limit must be between 1 and 1000")
        page_iterator: AsyncPageIterator[BlobProperties] = (
            self._client.get_container_client(container)
            .list_blobs(name_starts_with=prefix, include=["metadata", "tags"])
            .by_page(continuation_token=continuation_token)
        )
        try:
            page = await page_iterator.__anext__()
        except StopAsyncIteration:
            return BlobPage(items=())
        items: list[BlobMetadata] = []
        async for item in page:
            items.append(to_metadata(StorageLocation(container, item.name), item))
            if len(items) >= limit:
                break
        return BlobPage(items=tuple(items), continuation_token=page_iterator.continuation_token)

    async def generate_sas_url(
        self,
        location: StorageLocation,
        permissions: Sequence[SasPermission],
        *,
        expires_in: timedelta,
    ) -> str:
        self._validate_location(location)
        if not permissions or expires_in <= timedelta(0) or expires_in > timedelta(hours=24):
            raise StorageValidationError("SAS permissions and expiry are invalid")
        account_name = self._client.account_name
        if account_name is None:
            raise SASGenerationFailedError("Azure account name is unavailable")
        token = await generate_user_delegation_sas(
            self._client,
            account_name,
            location,
            permissions,
            expires_in,
        )
        return f"{self.get_url(location)}?{token}"

    async def get_metadata(self, location: StorageLocation) -> BlobMetadata:
        self._validate_location(location)
        try:
            return to_metadata(location, await self._blob(location).get_blob_properties())
        except Exception as error:
            raise translate_azure_error(error, location) from error

    async def set_metadata(
        self,
        location: StorageLocation,
        metadata: Mapping[str, str],
        *,
        expected_etag: str | None = None,
    ) -> BlobMetadata:
        self._validate_location(location)
        blob = self._blob(location)
        try:
            if expected_etag:
                await blob.set_blob_metadata(
                    sanitize_metadata(metadata),
                    etag=expected_etag,
                    match_condition=MatchConditions.IfNotModified,
                )
            else:
                await blob.set_blob_metadata(sanitize_metadata(metadata))
            return to_metadata(location, await blob.get_blob_properties())
        except Exception as error:
            raise translate_azure_error(error, location) from error

    def get_url(self, location: StorageLocation) -> str:
        self._validate_location(location)
        return f"{self._config.base_url}/{location.container}/{quote(location.blob_name)}"

    async def health_check(self) -> HealthStatus:
        started = time.perf_counter()
        try:
            await self._client.get_account_information()
            for container in self._config.containers:
                container_client = self._client.get_container_client(container)
                properties = await container_client.get_container_properties()
                if properties.public_access is not None:
                    return HealthStatus(
                        healthy=False,
                        latency_ms=round((time.perf_counter() - started) * 1000),
                        detail=f"container {container} is not private",
                    )
            healthy, detail = True, "reachable"
        except Exception:
            healthy, detail = False, "unavailable"
        latency_ms = round((time.perf_counter() - started) * 1000)
        await self._record("health_check", healthy)
        return HealthStatus(healthy=healthy, latency_ms=latency_ms, detail=detail)

    async def close(self) -> None:
        await self._client.close()

    def _blob(self, location: StorageLocation) -> BlobClient:
        return self._client.get_blob_client(location.container, location.blob_name)

    def _validate_container(self, container: str) -> None:
        validate_container_name(container)
        if container not in self._config.containers:
            raise StorageValidationError("Container is not configured")

    def _validate_location(self, location: StorageLocation) -> None:
        self._validate_container(location.container)
        validate_blob_name(location.blob_name)

    async def _record(self, operation: str, success: bool) -> None:
        if self._circuit_breaker_hook is not None:
            await self._circuit_breaker_hook(operation, success)

    async def _log_operation(
        self,
        operation: str,
        location: StorageLocation,
        size: int | None,
        started: float,
        *,
        success: bool,
    ) -> None:
        duration_ms = round((time.perf_counter() - started) * 1000)
        self._logger.info(
            "storage.operation",
            provider="azure",
            operation=operation,
            container=location.container,
            blob_name=location.blob_name,
            size_bytes=size,
            duration_ms=duration_ms,
            success=success,
        )
        await self._record(operation, success)
