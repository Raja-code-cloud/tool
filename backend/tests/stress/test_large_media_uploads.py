"""Large media upload stress validation."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from cloud_content_hub.infrastructure.storage.models import BlobType, StorageLocation, UploadRequest
from cloud_content_hub.infrastructure.storage.testing.fake import InMemoryStorageProvider
from cloud_content_hub.infrastructure.storage.testing.fixtures import SAMPLE_BYTES
from cloud_content_hub.infrastructure.storage.utils import build_blob_name
from tests.performance.helpers.metrics import run_concurrent

pytestmark = [pytest.mark.stress, pytest.mark.performance]

MEGA_PAYLOAD = SAMPLE_BYTES * 4096  # ~96 KB synthetic media chunk


@pytest.mark.asyncio
async def test_large_media_upload_stress() -> None:
    provider = InMemoryStorageProvider()
    lock = asyncio.Lock()
    counter = {"index": 0}

    async def upload_large() -> None:
        async with lock:
            counter["index"] += 1
            current = counter["index"]
        location = StorageLocation(
            container="stress-media",
            blob_name=build_blob_name(
                "tenant-stress",
                "user-stress",
                BlobType.MEDIA,
                uuid4(),
                f"media-{current}.bin",
                created_at=datetime.now(tz=UTC),
            ),
        )
        request = UploadRequest(
            location=location,
            data=MEGA_PAYLOAD,
            content_type="application/octet-stream",
            content_length=len(MEGA_PAYLOAD),
            filename=f"media-{current}.bin",
        )
        await provider.upload(request)

    stats = await run_concurrent(concurrency=20, per_worker=3, operation=upload_large)
    assert stats.count == 60
    assert stats.p99 < 5.0


@pytest.mark.asyncio
async def test_concurrent_large_upload_memory_stability() -> None:
    provider = InMemoryStorageProvider()

    async def upload_once() -> None:
        location = StorageLocation(
            container="stress-stable",
            blob_name=build_blob_name(
                "tenant-stress",
                "user-stress",
                BlobType.MEDIA,
                uuid4(),
                "stable.bin",
                created_at=datetime.now(tz=UTC),
            ),
        )
        await provider.upload(
            UploadRequest(
                location=location,
                data=MEGA_PAYLOAD,
                content_type="application/octet-stream",
                content_length=len(MEGA_PAYLOAD),
                filename="stable.bin",
            )
        )

    stats = await run_concurrent(concurrency=10, per_worker=5, operation=upload_once)
    assert stats.p95 < 3.0
