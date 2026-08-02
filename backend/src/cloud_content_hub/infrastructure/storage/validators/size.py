"""Blob size validation."""

from cloud_content_hub.infrastructure.storage.exceptions import (
    FileTooLargeError,
    StorageValidationError,
)


def validate_size(size: int, max_size_bytes: int) -> int:
    if size < 0:
        raise StorageValidationError("Content size cannot be negative")
    if size > max_size_bytes:
        raise FileTooLargeError("Content exceeds the configured maximum size")
    return size


def validate_not_empty(size: int) -> int:
    if size == 0:
        raise StorageValidationError("Empty files are not allowed")
    return size
