"""Azure SDK response and error translation helpers."""

from datetime import UTC

from azure.core.exceptions import (
    ClientAuthenticationError,
    HttpResponseError,
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotFoundError,
    ServiceRequestError,
    ServiceResponseError,
)
from azure.storage.blob import BlobProperties

from cloud_content_hub.infrastructure.storage.exceptions import (
    BlobAlreadyExistsError,
    BlobNotFoundError,
    ContainerNotFoundError,
    DownloadFailed,
    StorageAuthenticationError,
    StorageConditionError,
    StorageError,
    StorageUnavailableError,
    UploadFailed,
)
from cloud_content_hub.infrastructure.storage.models import BlobMetadata, StorageLocation


def to_metadata(location: StorageLocation, properties: BlobProperties) -> BlobMetadata:
    content_settings = properties.content_settings
    return BlobMetadata(
        location=location,
        size=properties.size,
        content_type=content_settings.content_type or "application/octet-stream",
        etag=str(properties.etag),
        last_modified=properties.last_modified.astimezone(UTC),
        metadata=dict(properties.metadata or {}),
        tags=dict(properties.tags or {}),
        checksum_sha256=(properties.metadata or {}).get("checksum_sha256"),
        content_disposition=content_settings.content_disposition,
        content_encoding=content_settings.content_encoding,
        cache_control=content_settings.cache_control,
    )


def translate_azure_error(
    error: Exception,
    location: StorageLocation | None = None,
    *,
    operation: str | None = None,
) -> StorageError:
    suffix = "" if location is None else f" ({location.container}/{location.blob_name})"
    if isinstance(error, ResourceNotFoundError):
        if location is not None and location.blob_name == "":
            return ContainerNotFoundError(f"Container was not found{suffix}")
        return BlobNotFoundError(f"Blob was not found{suffix}")
    if isinstance(error, ResourceExistsError):
        return BlobAlreadyExistsError(f"Blob already exists{suffix}")
    if isinstance(error, ResourceModifiedError):
        return StorageConditionError(f"Blob condition failed{suffix}")
    if isinstance(error, ClientAuthenticationError):
        return StorageAuthenticationError("Azure Storage authentication failed")
    if isinstance(error, (ServiceRequestError, ServiceResponseError, HttpResponseError)):
        if operation == "upload":
            return UploadFailed("Azure Storage upload failed")
        if operation == "download":
            return DownloadFailed("Azure Storage download failed")
        return StorageUnavailableError("Azure Storage request failed")
    if operation == "upload":
        return UploadFailed("Unexpected Azure Storage upload failure")
    if operation == "download":
        return DownloadFailed("Unexpected Azure Storage download failure")
    return StorageUnavailableError("Unexpected Azure Storage failure")
