"""Upload and storage security validation tests."""

from __future__ import annotations

from collections.abc import Callable

import pytest

from cloud_content_hub.infrastructure.storage.exceptions import (
    FileTooLargeError,
    InvalidMimeTypeError,
    StorageValidationError,
)
from cloud_content_hub.infrastructure.storage.utils import sanitize_metadata
from cloud_content_hub.infrastructure.storage.validators.extension import validate_extension
from cloud_content_hub.infrastructure.storage.validators.filename import validate_blob_name, validate_filename
from cloud_content_hub.infrastructure.storage.validators.mime import validate_mime_type
from cloud_content_hub.infrastructure.storage.validators.size import validate_not_empty, validate_size


@pytest.mark.parametrize(
    "path",
    [
        "../secret",
        "../../etc/passwd",
        "tenant/../other/file.pdf",
        "/absolute/path.pdf",
        "segment/../escape/file.pdf",
    ],
)
def test_path_traversal_in_blob_names_is_rejected(path: str) -> None:
    with pytest.raises(StorageValidationError):
        validate_blob_name(path)


@pytest.mark.parametrize(
    "filename",
    [
        "../report.pdf",
        "..\\report.pdf",
        "bad name.pdf",
        ".hidden",
        "",
    ],
)
def test_unsafe_filenames_are_rejected(filename: str) -> None:
    with pytest.raises(StorageValidationError):
        validate_filename(filename)


def test_extension_allowlist_rejects_executables() -> None:
    with pytest.raises(StorageValidationError):
        validate_extension("payload.exe", ["pdf", "png", "mp4"])


def test_mime_allowlist_rejects_unknown_types() -> None:
    with pytest.raises(InvalidMimeTypeError):
        validate_mime_type("chemical/x-example")


def test_empty_upload_is_rejected() -> None:
    with pytest.raises(StorageValidationError):
        validate_not_empty(0)


def test_oversized_upload_is_rejected() -> None:
    with pytest.raises(FileTooLargeError):
        validate_size(101 * 1024 * 1024, 100 * 1024 * 1024)


@pytest.mark.parametrize(
    "operation",
    [
        lambda: sanitize_metadata({"bad-key": "value"}),
        lambda: validate_mime_type("text/plain\r\nX-Injected: true"),
    ],
)
def test_metadata_and_mime_injection_vectors_are_rejected(operation: Callable[[], object]) -> None:
    with pytest.raises((StorageValidationError, InvalidMimeTypeError)):
        operation()
