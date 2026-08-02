"""Latency sampling and percentile aggregation for performance tests."""

from __future__ import annotations

import asyncio
import statistics
import time
from collections.abc import Awaitable, Callable, Sequence
from dataclasses import dataclass


def percentile(sorted_values: Sequence[float], p: float) -> float:
    """Return the p-th percentile (0-100) from a pre-sorted sequence."""

    if not sorted_values:
        msg = "Cannot compute percentile of an empty sample."
        raise ValueError(msg)
    if p <= 0:
        return sorted_values[0]
    if p >= 100:
        return sorted_values[-1]
    rank = (len(sorted_values) - 1) * (p / 100.0)
    lower = int(rank)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = rank - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


@dataclass(frozen=True, slots=True)
class LatencyStats:
    """Aggregated latency measurements for one scenario."""

    samples: tuple[float, ...]
    label: str

    @property
    def count(self) -> int:
        return len(self.samples)

    @property
    def mean(self) -> float:
        return statistics.fmean(self.samples) if self.samples else 0.0

    @property
    def p50(self) -> float:
        return percentile(sorted(self.samples), 50)

    @property
    def p95(self) -> float:
        return percentile(sorted(self.samples), 95)

    @property
    def p99(self) -> float:
        return percentile(sorted(self.samples), 99)

    @property
    def min(self) -> float:
        return min(self.samples) if self.samples else 0.0

    @property
    def max(self) -> float:
        return max(self.samples) if self.samples else 0.0

    def requests_per_second(self, *, wall_seconds: float) -> float:
        if wall_seconds <= 0:
            return 0.0
        return self.count / wall_seconds

    def to_dict(self) -> dict[str, float | int | str]:
        return {
            "label": self.label,
            "count": self.count,
            "mean_ms": round(self.mean * 1000, 3),
            "p50_ms": round(self.p50 * 1000, 3),
            "p95_ms": round(self.p95 * 1000, 3),
            "p99_ms": round(self.p99 * 1000, 3),
            "min_ms": round(self.min * 1000, 3),
            "max_ms": round(self.max * 1000, 3),
        }


async def collect_latencies(
    *,
    label: str,
    iterations: int,
    operation: Callable[[], Awaitable[None]],
    warmup: int = 0,
) -> LatencyStats:
    """Run an async operation repeatedly and collect wall-clock latencies."""

    for _ in range(warmup):
        await operation()

    samples: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        await operation()
        samples.append(time.perf_counter() - start)
    return LatencyStats(samples=tuple(samples), label=label)


def collect_latencies_sync(
    *,
    label: str,
    iterations: int,
    operation: Callable[[], None],
) -> LatencyStats:
    """Run a sync operation repeatedly and collect wall-clock latencies."""

    samples: list[float] = []
    for _ in range(iterations):
        start = time.perf_counter()
        operation()
        samples.append(time.perf_counter() - start)
    return LatencyStats(samples=tuple(samples), label=label)


async def run_concurrent(
    *,
    concurrency: int,
    per_worker: int,
    operation: Callable[[], Awaitable[None]],
    warmup: int = 0,
) -> LatencyStats:
    """Execute an async operation across concurrent workers."""

    for _ in range(warmup):
        await operation()

    samples: list[float] = []

    async def worker() -> None:
        for _ in range(per_worker):
            start = time.perf_counter()
            await operation()
            samples.append(time.perf_counter() - start)

    await asyncio.gather(*(worker() for _ in range(concurrency)))
    return LatencyStats(samples=tuple(samples), label=f"concurrency={concurrency}")
