"""Concurrency-safe in-process usage accounting."""

import asyncio
from collections import defaultdict

from cloud_content_hub.infrastructure.ai.models import TokenUsage


class UsageLedger:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._usage: defaultdict[str, TokenUsage] = defaultdict(
            lambda: TokenUsage(input_tokens=0, output_tokens=0)
        )

    async def record(self, provider: str, usage: TokenUsage) -> None:
        async with self._lock:
            old = self._usage[provider]
            self._usage[provider] = TokenUsage(
                input_tokens=old.input_tokens + usage.input_tokens,
                output_tokens=old.output_tokens + usage.output_tokens,
            )

    async def get(self, provider: str) -> TokenUsage:
        async with self._lock:
            return self._usage[provider]
