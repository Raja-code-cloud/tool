"""Simulate API readiness probe behavior without importing the HTTP delivery layer."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReadinessResult:
    """Outcome of a readiness probe matching API /ready semantics."""

    ready: bool
    checks: dict[str, str]


async def probe_readiness(
    *,
    check_database: Callable[[], Awaitable[None]],
    check_redis: Callable[[], Awaitable[None]],
    database_timeout_seconds: float,
    redis_timeout_seconds: float,
) -> ReadinessResult:
    """Mirror readiness logic from api/routers/v1/health.py."""

    checks: dict[str, str] = {}
    dependencies: tuple[tuple[str, Callable[[], Awaitable[None]], float], ...] = (
        ("database", check_database, database_timeout_seconds),
        ("redis", check_redis, redis_timeout_seconds),
    )
    for name, check, timeout_seconds in dependencies:
        try:
            async with asyncio.timeout(timeout_seconds):
                await check()
            checks[name] = "ok"
        except Exception:
            checks[name] = "unavailable"

    ready = all(status == "ok" for status in checks.values())
    return ReadinessResult(ready=ready, checks=checks)
