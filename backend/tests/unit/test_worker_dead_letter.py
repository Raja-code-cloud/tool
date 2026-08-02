"""Unit tests for worker dead-letter queue."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from cloud_content_hub.workers.config import WorkerRetryConfig
from cloud_content_hub.workers.retry import DeadLetterQueue


@pytest.fixture
def redis() -> AsyncMock:
    store: dict[str, dict[str, str]] = {}

    async def hset(key: str, field: str, value: str) -> int:
        store.setdefault(key, {})[field] = value
        return 1

    async def hgetall(key: str) -> dict[str, str]:
        return dict(store.get(key, {}))

    async def hdel(key: str, field: str) -> int:
        bucket = store.get(key, {})
        if field not in bucket:
            return 0
        del bucket[field]
        return 1

    async def hlen(key: str) -> int:
        return len(store.get(key, {}))

    client = AsyncMock()
    client.hset = AsyncMock(side_effect=hset)
    client.hgetall = AsyncMock(side_effect=hgetall)
    client.hdel = AsyncMock(side_effect=hdel)
    client.hlen = AsyncMock(side_effect=hlen)
    return client


@pytest.fixture
def dead_letter_queue(redis: AsyncMock) -> DeadLetterQueue:
    return DeadLetterQueue(
        redis,
        WorkerRetryConfig(dead_letter_queue_prefix="cloud_content_hub:test:dlq"),
    )


@pytest.mark.asyncio
async def test_dead_letter_queue_enqueue_and_list(
    dead_letter_queue: DeadLetterQueue,
) -> None:
    entry = await dead_letter_queue.enqueue(
        task_name="cloud_content_hub.tasks.upload_asset",
        payload={"job_id": "job-1"},
        reason_code="retry_exhausted",
        reason_message="failed permanently",
    )

    entries = await dead_letter_queue.list_entries("cloud_content_hub.tasks.upload_asset")

    assert entry.entry_id
    assert len(entries) == 1
    assert entries[0].reason_code == "retry_exhausted"
    assert entries[0].payload == {"job_id": "job-1"}


@pytest.mark.asyncio
async def test_dead_letter_queue_remove(dead_letter_queue: DeadLetterQueue) -> None:
    entry = await dead_letter_queue.enqueue(
        task_name="cloud_content_hub.tasks.upload_asset",
        payload={"job_id": "job-2"},
        reason_code="poison_message",
        reason_message="invalid payload",
    )

    removed = await dead_letter_queue.remove("cloud_content_hub.tasks.upload_asset", entry.entry_id)
    count = await dead_letter_queue.count("cloud_content_hub.tasks.upload_asset")

    assert removed is True
    assert count == 0
