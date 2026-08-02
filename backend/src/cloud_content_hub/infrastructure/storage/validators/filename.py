"""Safe filename and blob path validation."""

import re
from pathlib import PurePosixPath

from cloud_content_hub.infrastructure.storage.exceptions import StorageValidationError

_SAFE_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,254}$")


def validate_filename(filename: str) -> str:
    normalized = PurePosixPath(filename.replace("\\", "/")).name
    if normalized != filename or not _SAFE_SEGMENT.fullmatch(normalized):
        raise StorageValidationError("Filename contains unsupported characters or path segments")
    return normalized


def validate_blob_name(blob_name: str) -> str:
    if not blob_name or len(blob_name) > 1024 or blob_name.startswith("/"):
        raise StorageValidationError("Blob name is empty or too long")
    segments = blob_name.split("/")
    unsafe = any(
        segment in {"", ".", ".."} or not _SAFE_SEGMENT.fullmatch(segment)
        for segment in segments
    )
    if unsafe:
        raise StorageValidationError("Blob name contains an unsafe path segment")
    return blob_name
