"""Performance targets validated by the performance test suite."""

from __future__ import annotations

from dataclasses import dataclass

from tests.performance.helpers.metrics import LatencyStats


@dataclass(frozen=True, slots=True)
class PerformanceTargets:
    """Documented SLO thresholds for Cloud Content Hub backend."""

    api_crud_p95_seconds: float = 0.300
    api_search_p95_seconds: float = 0.500
    api_auth_p95_seconds: float = 0.200
    scheduler_dispatch_p95_seconds: float = 5.0
    outbox_batch_p95_seconds: float = 1.0
    worker_success_rate: float = 0.99
    storage_upload_p95_seconds: float = 2.0
    storage_download_p95_seconds: float = 1.0
    db_crud_p95_seconds: float = 0.100
    db_search_p95_seconds: float = 0.300
    provider_retry_p95_seconds: float = 2.0


PERFORMANCE_TARGETS = PerformanceTargets()


def assert_within_target(
    stats: LatencyStats,
    *,
    p95_seconds: float,
    label: str | None = None,
) -> None:
    """Assert P95 latency is within the documented target."""

    target_label = label or stats.label
    assert stats.p95 <= p95_seconds, (
        f"{target_label}: P95 {stats.p95 * 1000:.2f}ms exceeds target "
        f"{p95_seconds * 1000:.2f}ms"
    )
