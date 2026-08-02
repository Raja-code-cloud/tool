"""Storage provider micro-benchmarks."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest

from cloud_content_hub.infrastructure.storage.models import (
    BlobType,
    DownloadRequest,
    StorageLocation,
    UploadRequest,
)
from cloud_content_hub.infrastructure.storage.testing.fake import InMemoryStorageProvider
from cloud_content_hub.infrastructure.storage.testing.fixtures import SAMPLE_BYTES
from cloud_content_hub.infrastructure.storage.utils import build_blob_name

pytestmark = pytest.mark.benchmark


@pytest.fixture
def seeded_storage() -> InMemoryStorageProvider:
    return InMemoryStorageProvider()


@pytest.mark.asyncio
async def test_benchmark_storage_upload(
    benchmark: Any,
    seeded_storage: InMemoryStorageProvider,
) -> None:
    counter = {"index": 0}

    async def run() -> None:
        counter["index"] += 1
        current = counter["index"]
        location = StorageLocation(
            container="bench-upload",
            blob_name=build_blob_name(
                "tenant-bench",
                "user-bench",
                BlobType.ARTICLE,
                uuid4(),
                f"sample-{current}.txt",
                created_at=datetime.now(tz=UTC),
            ),
        )
        await seeded_storage.upload(
            UploadRequest(
                location=location,
                data=SAMPLE_BYTES,
                content_type="text/plain",
                content_length=len(SAMPLE_BYTES),
                filename=f"sample-{current}.txt",
            )
        )

    await benchmark.pedantic(run, rounds=20, iterations=1)


@pytest.mark.asyncio
async def test_benchmark_storage_download(
    benchmark: Any,
    seeded_storage: InMemoryStorageProvider,
) -> None:
    metadata = await seeded_storage.upload(
        UploadRequest(
            location=StorageLocation(
                container="bench-download",
                blob_name=build_blob_name(
                    "tenant-bench",
                    "user-bench",
                    BlobType.ARTICLE,
                    uuid4(),
                    "download.txt",
                    created_at=datetime.now(tz=UTC),
                ),
            ),
            data=SAMPLE_BYTES,
            content_type="text/plain",
            content_length=len(SAMPLE_BYTES),
            filename="download.txt",
        )
    )

    async def run() -> None:
        chunks = [
            chunk
            async for chunk in seeded_storage.download(
                DownloadRequest(location=metadata.location)
            )
        ]
        assert b"".join(chunks) == SAMPLE_BYTES

    await benchmark.pedantic(run, rounds=20, iterations=1)
