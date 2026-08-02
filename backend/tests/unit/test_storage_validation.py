from datetime import datetime, timezone
from collections.abc import Callable
from uuid import UUID

import pytest

from cloud_content_hub.infrastructure.storage.config import (
    AzureCredentialMode,
    AzureStorageConfig,
)
from cloud_content_hub.infrastructure.storage.exceptions import (
    ChecksumMismatchError,
    StorageValidationError,
)
from cloud_content_hub.infrastructure.storage.models import BlobType
from cloud_content_hub.infrastructure.storage.utils import build_blob_name, sanitize_metadata
from cloud_content_hub.infrastructure.storage.validators.checksum import verify_checksum
from cloud_content_hub.infrastructure.storage.validators.filename import validate_blob_name
from cloud_content_hub.infrastructure.storage.validators.extension import validate_extension
from cloud_content_hub.infrastructure.storage.validators.mime import validate_mime_type
from cloud_content_hub.infrastructure.storage.validators.size import validate_not_empty, validate_size


def test_extension_whitelist_rejects_unknown_suffix() -> None:
    with pytest.raises(StorageValidationError):
        validate_extension("report.exe", ["pdf", "txt"])


def test_empty_file_is_rejected() -> None:
    with pytest.raises(StorageValidationError):
        validate_not_empty(0)


def test_blob_name_is_deterministic_and_partitioned() -> None:
    result = build_blob_name(
        "tenant-a",
        "user-a",
        BlobType.VIDEO,
        UUID("00000000-0000-4000-8000-000000000001"),
        "clip.mp4",
        created_at=datetime(2025, 2, 3, tzinfo=timezone.utc),
    )
    assert result == (
        "tenant-a/user-a/2025/02/03/videos/00000000000040008000000000000001/clip.mp4"
    )


@pytest.mark.parametrize(
    "operation",
    [
        lambda: validate_blob_name("../secret"),
        lambda: validate_mime_type("chemical/x-example"),
        lambda: sanitize_metadata({"bad-key": "value"}),
    ],
)
def test_untrusted_values_are_rejected(operation: Callable[[], object]) -> None:
    with pytest.raises(StorageValidationError):
        operation()


def test_checksum_mismatch_is_rejected() -> None:
    with pytest.raises(ChecksumMismatchError):
        verify_checksum(b"actual", "0" * 64)


def test_service_principal_config_requires_complete_credentials() -> None:
    with pytest.raises(StorageValidationError):
        AzureStorageConfig(
            account_url="https://example.blob.core.windows.net",
            credential_mode=AzureCredentialMode.SERVICE_PRINCIPAL,
            tenant_id="tenant",
        )
