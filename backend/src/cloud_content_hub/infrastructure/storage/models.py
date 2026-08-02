"""Provider-neutral storage value objects."""

from collections.abc import AsyncIterable, Awaitable, Callable, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum

type ByteStream = AsyncIterable[bytes]
type ProgressCallback = Callable[[int, int | None], Awaitable[None]]


class BlobType(StrEnum):
    POSTER = "posters"
    ARTICLE = "articles"
    VIDEO = "videos"
    THUMBNAIL = "thumbnails"
    GENERATED_CONTENT = "generated-content"
    TEMP = "temp"
    EXPORT = "exports"
    LOG = "logs"


class SasPermission(StrEnum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"


@dataclass(frozen=True, slots=True)
class StorageLocation:
    container: str
    blob_name: str


@dataclass(frozen=True, slots=True)
class UploadRequest:
    location: StorageLocation
    data: bytes | ByteStream
    content_type: str
    content_length: int | None = None
    filename: str | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)
    tags: Mapping[str, str] = field(default_factory=dict)
    content_disposition: str | None = None
    content_encoding: str | None = None
    cache_control: str | None = None
    checksum_sha256: str | None = None
    overwrite: bool = False
    expected_etag: str | None = None
    progress: ProgressCallback | None = None


@dataclass(frozen=True, slots=True)
class DownloadRequest:
    location: StorageLocation
    offset: int | None = None
    length: int | None = None
    expected_etag: str | None = None
    progress: ProgressCallback | None = None


@dataclass(frozen=True, slots=True)
class BlobMetadata:
    location: StorageLocation
    size: int
    content_type: str
    etag: str
    last_modified: datetime
    metadata: Mapping[str, str] = field(default_factory=dict)
    tags: Mapping[str, str] = field(default_factory=dict)
    checksum_sha256: str | None = None
    content_disposition: str | None = None
    content_encoding: str | None = None
    cache_control: str | None = None


@dataclass(frozen=True, slots=True)
class BlobPage:
    items: tuple[BlobMetadata, ...]
    continuation_token: str | None = None


@dataclass(frozen=True, slots=True)
class HealthStatus:
    healthy: bool
    latency_ms: int
    detail: str
