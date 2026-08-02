"""Storage provider micro-benchmarks."""

from __future__ import annotations

from typing import Any

import pytest

from cloud_content_hub.infrastructure.storage.models import DownloadRequest
from cloud_content_hub.infrastructure.storage.testing.fake import InMemoryStorageProvider
from cloud_content_hub.infrastructure.storage.testing.fixtures import (
    SAMPLE_BYTES,
    sample_upload_request,
)

pytestmark = pytest.mark.benchmark


@pytest.fixture
def seeded_storage() -> InMemoryStorageProvider:
    return InMemoryStorageProvider()


@pytest.mark.asyncio
async def test_benchmark_storage_upload(benchmark: Any, seeded_storage: InMemoryStorageProvider) -> None:
    async def run() -> None:
        await seeded_storage.upload(sample_upload_request())

    await benchmark.pedantic(run, rounds=20, iterations=1)


@pytest.mark.asyncio
async def test_benchmark_storage_download(
    benchmark: Any,
    seeded_storage: InMemoryStorageProvider,
) -> None:
    metadata = await seeded_storage.upload(sample_upload_request())

    async def run() -> None:
        chunks = [
            chunk
            async for chunk in seeded_storage.download(
                DownloadRequest(location=metadata.location)
            )
        ]
        assert b"".join(chunks) == SAMPLE_BYTES

    await benchmark.pedantic(run, rounds=20, iterations=1)
