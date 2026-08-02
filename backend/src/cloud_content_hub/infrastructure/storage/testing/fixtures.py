"""Synthetic sample values shared by storage tests."""

from datetime import UTC, datetime
from uuid import UUID

from cloud_content_hub.infrastructure.storage.models import (
    BlobType,
    StorageLocation,
    UploadRequest,
)
from cloud_content_hub.infrastructure.storage.utils import build_blob_name

SAMPLE_BYTES = b"synthetic storage fixture"
SAMPLE_OBJECT_ID = UUID("00000000-0000-4000-8000-000000000001")
SAMPLE_CREATED_AT = datetime(2025, 1, 2, 3, 4, tzinfo=UTC)


def sample_location() -> StorageLocation:
    return StorageLocation(
        container="articles",
        blob_name=build_blob_name(
            "tenant-a",
            "user-a",
            BlobType.ARTICLE,
            SAMPLE_OBJECT_ID,
            "sample.txt",
            created_at=SAMPLE_CREATED_AT,
        ),
    )


def sample_upload_request() -> UploadRequest:
    return UploadRequest(
        location=sample_location(),
        data=SAMPLE_BYTES,
        content_type="text/plain",
        content_length=len(SAMPLE_BYTES),
        filename="sample.txt",
        metadata={"fixture": "true"},
    )
