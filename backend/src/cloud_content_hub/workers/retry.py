"""Retry classification and dead-letter handling for Celery workers."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from redis.asyncio import Redis

from cloud_content_hub.core.errors import (
    ApplicationError,
    ClientError,
    DependencyError,
    DependencyTimeoutError,
    DependencyUnavailableError,
    ProviderRateLimitError,
)
from cloud_content_hub.workers.config import WorkerRetryConfig
from cloud_content_hub.workers.exceptions import (
    PermanentWorkerError,
    PoisonMessageError,
    TransientWorkerError,
)


def is_transient_error(error: BaseException) -> bool:
    """Return whether an exception should be retried."""

    if isinstance(
        error,
        TransientWorkerError
        | DependencyError
        | DependencyUnavailableError
        | DependencyTimeoutError
        | ProviderRateLimitError,
    ):
        return True
    if isinstance(error, ClientError | PermanentWorkerError | PoisonMessageError):
        return False
    if isinstance(error, ApplicationError):
        return False
    return False


@dataclass(frozen=True, slots=True)
class WorkerRetryDecision:
    """Outcome of classifying a failed worker attempt."""

    retry: bool
    reason_code: str
    reason_message: str
    backoff_seconds: float | None = None


class WorkerRetryPolicy:
    """Bounded exponential backoff with poison-message detection."""

    def __init__(self, config: WorkerRetryConfig) -> None:
        self._config = config

    def classify_failure(
        self,
        *,
        task_name: str,
        attempt_count: int,
        last_error: str | None,
        error: BaseException,
    ) -> WorkerRetryDecision:
        """Classify a task failure and decide whether to retry."""

        _ = task_name
        message = str(error)[:2048]
        next_attempt = attempt_count + 1

        if isinstance(error, PoisonMessageError | PermanentWorkerError):
            return WorkerRetryDecision(
                retry=False,
                reason_code="poison_message",
                reason_message=message,
            )

        if not is_transient_error(error):
            return WorkerRetryDecision(
                retry=False,
                reason_code="permanent_failure",
                reason_message=message,
            )

        if last_error == message and next_attempt >= self._config.poison_message_threshold:
            return WorkerRetryDecision(
                retry=False,
                reason_code="poison_message",
                reason_message=f"Repeated failure: {message}",
            )

        if next_attempt > self._config.max_retries:
            return WorkerRetryDecision(
                retry=False,
                reason_code="retry_exhausted",
                reason_message=message,
            )

        delay = min(
            self._config.max_backoff_seconds,
            self._config.base_backoff_seconds
            * math.pow(self._config.backoff_multiplier, next_attempt - 1),
        )
        return WorkerRetryDecision(
            retry=True,
            reason_code="transient_failure",
            reason_message=message,
            backoff_seconds=delay,
        )

    def compute_backoff_seconds(self, attempt_count: int) -> float:
        """Return the backoff delay for a given attempt count."""

        return min(
            self._config.max_backoff_seconds,
            self._config.base_backoff_seconds
            * math.pow(self._config.backoff_multiplier, max(0, attempt_count - 1)),
        )


@dataclass(frozen=True, slots=True)
class DeadLetterEntry:
    """Serialized dead-letter queue record."""

    entry_id: str
    task_name: str
    payload: dict[str, Any]
    reason_code: str
    reason_message: str
    dead_lettered_at: datetime


class DeadLetterQueue:
    """Redis-backed dead-letter storage for worker tasks."""

    def __init__(self, redis: Redis, config: WorkerRetryConfig) -> None:
        self._redis = redis
        self._config = config

    def _queue_key(self, task_name: str) -> str:
        return f"{self._config.dead_letter_queue_prefix}:{task_name}"

    async def enqueue(
        self,
        *,
        task_name: str,
        payload: dict[str, Any],
        reason_code: str,
        reason_message: str,
        dead_lettered_at: datetime | None = None,
    ) -> DeadLetterEntry:
        """Persist one dead-lettered task payload."""

        entry_id = str(uuid4())
        effective_at = dead_lettered_at or datetime.now(tz=UTC)
        entry = DeadLetterEntry(
            entry_id=entry_id,
            task_name=task_name,
            payload=payload,
            reason_code=reason_code,
            reason_message=reason_message,
            dead_lettered_at=effective_at,
        )
        await self._redis.hset(
            self._queue_key(task_name),
            entry_id,
            json.dumps(
                {
                    "entry_id": entry_id,
                    "task_name": task_name,
                    "payload": payload,
                    "reason_code": reason_code,
                    "reason_message": reason_message,
                    "dead_lettered_at": effective_at.isoformat(),
                }
            ),
        )
        return entry

    async def list_entries(self, task_name: str) -> tuple[DeadLetterEntry, ...]:
        """Return all dead-letter entries for one task."""

        raw_entries = await self._redis.hgetall(self._queue_key(task_name))
        entries: list[DeadLetterEntry] = []
        for entry_id, raw_value in raw_entries.items():
            parsed = json.loads(raw_value)
            entries.append(
                DeadLetterEntry(
                    entry_id=str(entry_id),
                    task_name=task_name,
                    payload=dict(parsed["payload"]),
                    reason_code=str(parsed["reason_code"]),
                    reason_message=str(parsed["reason_message"]),
                    dead_lettered_at=datetime.fromisoformat(str(parsed["dead_lettered_at"])),
                )
            )
        return tuple(entries)

    async def remove(self, task_name: str, entry_id: str) -> bool:
        """Remove one dead-letter entry."""

        removed = await self._redis.hdel(self._queue_key(task_name), entry_id)
        return bool(removed)

    async def count(self, task_name: str) -> int:
        """Return the number of dead-letter entries for one task."""

        return int(await self._redis.hlen(self._queue_key(task_name)))


def parse_uuid(value: object) -> UUID | None:
    """Parse a UUID from worker payload fields."""

    if value is None:
        return None
    if isinstance(value, UUID):
        return value
    return UUID(str(value))
