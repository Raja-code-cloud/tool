"""Worker security: retry abuse, DLQ safety, and privilege model tests."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from cloud_content_hub.core.errors import ValidationError
from cloud_content_hub.workers.base import WorkerTaskPayload, build_worker_actor
from cloud_content_hub.workers.config import WorkerRetryConfig
from cloud_content_hub.workers.exceptions import TransientWorkerError
from cloud_content_hub.workers.retry import DeadLetterQueue, WorkerRetryPolicy


def test_worker_actor_uses_wildcard_permissions_by_design() -> None:
    """Documents accepted risk R-004: workers trust queue isolation, not RBAC."""

    payload = WorkerTaskPayload(workspace_id=uuid4(), actor_id=uuid4())
    actor = build_worker_actor(payload)
    assert actor.permissions == frozenset({"*"})


def test_permanent_errors_are_not_retried_indefinitely() -> None:
    policy = WorkerRetryPolicy(WorkerRetryConfig(max_retries=3))
    decision = policy.classify_failure(
        task_name="cloud_content_hub.tasks.upload_asset",
        attempt_count=0,
        last_error=None,
        error=ValidationError(detail="invalid payload"),
    )
    assert decision.retry is False


def test_transient_errors_allow_bounded_retry() -> None:
    policy = WorkerRetryPolicy(WorkerRetryConfig(max_retries=3))
    decision = policy.classify_failure(
        task_name="cloud_content_hub.tasks.upload_asset",
        attempt_count=0,
        last_error=None,
        error=TransientWorkerError(detail="redis unavailable"),
    )
    assert decision.retry is True
    assert decision.backoff_seconds is not None


def test_repeated_identical_errors_trigger_poison_detection() -> None:
    policy = WorkerRetryPolicy(
        WorkerRetryConfig(max_retries=5, poison_message_threshold=2),
    )
    error = TransientWorkerError(detail="same failure")
    decision = policy.classify_failure(
        task_name="cloud_content_hub.tasks.upload_asset",
        attempt_count=1,
        last_error="same failure",
        error=error,
    )
    assert decision.retry is False
    assert decision.reason_code == "poison_message"


@pytest.fixture
def redis() -> AsyncMock:
    store: dict[str, dict[str, str]] = {}

    async def hset(key: str, field: str, value: str) -> int:
        store.setdefault(key, {})[field] = value
        return 1

    async def hgetall(key: str) -> dict[str, str]:
        return dict(store.get(key, {}))

    client = AsyncMock()
    client.hset = AsyncMock(side_effect=hset)
    client.hgetall = AsyncMock(side_effect=hgetall)
    return client


@pytest.mark.asyncio
async def test_dead_letter_queue_isolates_failed_payloads(redis: AsyncMock) -> None:
    dlq = DeadLetterQueue(redis, WorkerRetryConfig())
    task_name = "cloud_content_hub.tasks.virus_scan"
    payload = {"workspace_id": str(uuid4())}
    await dlq.enqueue(
        task_name=task_name,
        payload=payload,
        reason_code="poison_message",
        reason_message="invalid payload",
    )
    entries = await dlq.list_entries(task_name)
    assert len(entries) == 1
    assert entries[0].payload == payload
