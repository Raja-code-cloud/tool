"""Streaming adapters with size limits, checksums, and progress."""

import hashlib
from collections.abc import AsyncIterable, AsyncIterator
from typing import Protocol

from cloud_content_hub.infrastructure.storage.exceptions import (
    ChecksumMismatchError,
    FileTooLargeError,
)
from cloud_content_hub.infrastructure.storage.models import ProgressCallback


class DownloadStream(Protocol):
    def chunks(self) -> AsyncIterator[bytes]: ...


async def validated_upload_stream(
    source: AsyncIterable[bytes],
    *,
    max_size_bytes: int,
    expected_checksum: str | None,
    progress: ProgressCallback | None,
    total: int | None,
) -> AsyncIterator[bytes]:
    transferred = 0
    digest = hashlib.sha256()
    async for chunk in source:
        if not chunk:
            continue
        transferred += len(chunk)
        if transferred > max_size_bytes:
            raise FileTooLargeError("Content exceeds the configured maximum size")
        digest.update(chunk)
        if progress is not None:
            await progress(transferred, total)
        yield chunk
    if expected_checksum is not None and digest.hexdigest() != expected_checksum.lower():
        raise ChecksumMismatchError("Content checksum does not match")


async def iter_download(
    downloader: DownloadStream,
    *,
    progress: ProgressCallback | None,
    total: int | None,
) -> AsyncIterator[bytes]:
    transferred = 0
    async for chunk in downloader.chunks():
        transferred += len(chunk)
        if progress is not None:
            await progress(transferred, total)
        yield chunk
