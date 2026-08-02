"""Asynchronous retry with exponential backoff and jitter."""

import asyncio
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import TypeVar

from cloud_content_hub.infrastructure.ai.exceptions import (
    AIRateLimitError,
    AITimeoutError,
    AIUnavailableError,
)

T = TypeVar("T")
TRANSIENT_ERRORS = (AIRateLimitError, AITimeoutError, AIUnavailableError)


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    attempts: int = 3
    base_delay: float = 0.25
    max_delay: float = 8
    jitter: float = 0.2


async def retry_async(operation: Callable[[], Awaitable[T]], policy: RetryPolicy) -> T:
    last_error: Exception | None = None
    for attempt in range(policy.attempts + 1):
        try:
            return await operation()
        except TRANSIENT_ERRORS as exc:
            last_error = exc
            if attempt >= policy.attempts:
                raise
            delay = min(policy.max_delay, policy.base_delay * 2**attempt)
            await asyncio.sleep(max(0, delay + random.uniform(-policy.jitter, policy.jitter)))
    if last_error:
        raise last_error
    raise AssertionError("unreachable")
