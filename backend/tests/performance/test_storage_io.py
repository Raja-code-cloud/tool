"""Azure Blob storage I/O performance validation (in-memory baseline)."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from cloud_content_hub.infrastructure.storage.models import BlobType, StorageLocation, UploadRequest
from cloud_content_hub.infrastructure.storage.testing.fake import InMemoryStorageProvider
from cloud_content_hub.infrastructure.storage.testing.fixtures import (
    SAMPLE_BYTES,
    sample_upload_request,
)
from cloud_content_hub.infrastructure.storage.utils import build_blob_name
from tests.performance.helpers.metrics import collect_latencies, run_concurrent
from tests.performance.helpers.targets import PERFORMANCE_TARGETS, assert_within_target

pytestmark = pytest.mark.performance

LARGE_PAYLOAD = SAMPLE_BYTES * 1024  # ~24 KB synthetic large file


@pytest.mark.asyncio
async def test_storage_upload_latency(storage_provider: InMemoryStorageProvider) -> None:
    counter = {"index": 0}

    async def upload_once() -> None:
        counter["index"] += 1
        current = counter["index"]
        location = StorageLocation(
            container="perf-upload",
            blob_name=build_blob_name(
                "tenant-perf",
                "user-perf",
                BlobType.ARTICLE,
                uuid4(),
                f"sample-{current}.txt",
                created_at=datetime.now(tz=UTC),
            ),
        )
        request = UploadRequest(
            location=location,
            data=SAMPLE_BYTES,
            content_type="text/plain",
            content_length=len(SAMPLE_BYTES),
            filename=f"sample-{current}.txt",
        )
        await storage_provider.upload(request)

    stats = await collect_latencies(
        label="InMemoryStorageProvider.upload",
        iterations=100,
        operation=upload_once,
    )
    assert_within_target(
        stats,
        p95_seconds=PERFORMANCE_TARGETS.storage_upload_p95_seconds,
        label="storage upload",
    )


@pytest.mark.asyncio
async def test_storage_download_latency(storage_provider: InMemoryStorageProvider) -> None:
    metadata = await storage_provider.upload(sample_upload_request())
    from cloud_content_hub.infrastructure.storage.models import DownloadRequest

    async def download_once() -> None:
        chunks = [
            chunk
            async for chunk in storage_provider.download(
                DownloadRequest(location=metadata.location)
            )
        ]
        assert b"".join(chunks) == SAMPLE_BYTES

    stats = await collect_latencies(
        label="InMemoryStorageProvider.download",
        iterations=100,
        operation=download_once,
    )
    assert_within_target(
        stats,
        p95_seconds=PERFORMANCE_TARGETS.storage_download_p95_seconds,
        label="storage download",
    )


@pytest.mark.asyncio
async def test_large_file_upload_latency(storage_provider: InMemoryStorageProvider) -> None:
    location = StorageLocation(
        container="perf-large",
        blob_name=build_blob_name(
            "tenant-perf",
            "user-perf",
            BlobType.VIDEO,
            uuid4(),
            "large.bin",
            created_at=datetime.now(tz=UTC),
        ),
    )
    request = UploadRequest(
        location=location,
        data=LARGE_PAYLOAD,
        content_type="application/octet-stream",
        content_length=len(LARGE_PAYLOAD),
        filename="large.bin",
    )

    async def upload_large() -> None:
        await storage_provider.upload(request)

    stats = await collect_latencies(
        label="large upload (24KB)",
        iterations=50,
        operation=upload_large,
    )
    assert_within_target(
        stats,
        p95_seconds=PERFORMANCE_TARGETS.storage_upload_p95_seconds,
        label="large storage upload",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("concurrency", [1, 10])
async def test_concurrent_upload_throughput(
    concurrency: int,
) -> None:
    provider = InMemoryStorageProvider()
    index = {"value": 0}
    lock = asyncio.Lock()

    async def upload_once() -> None:
        async with lock:
            index["value"] += 1
            current = index["value"]
        location = StorageLocation(
            container="perf-concurrent",
            blob_name=f"blob-{current}.bin",
        )
        request = UploadRequest(
            location=location,
            data=SAMPLE_BYTES,
            content_type="text/plain",
            content_length=len(SAMPLE_BYTES),
            filename=f"blob-{current}.txt",
        )
        await provider.upload(request)

    stats = await run_concurrent(
        concurrency=concurrency,
        per_worker=5,
        operation=upload_once,
    )
    assert stats.count == concurrency * 5
    assert_within_target(
        stats,
        p95_seconds=PERFORMANCE_TARGETS.storage_upload_p95_seconds * 2,
        label=f"concurrent upload x{concurrency}",
    )
