"""Process telemetry and explicit instrumentation hooks."""

import os
import time
from dataclasses import dataclass

import psutil
from prometheus_client import CollectorRegistry, Gauge

from .metrics import ObservabilityMetrics


@dataclass(frozen=True, slots=True)
class ProcessSnapshot:
    cpu_percent: float
    resident_memory_bytes: int
    uptime_seconds: float
    thread_count: int


class ProcessTelemetry:
    def __init__(self, registry: CollectorRegistry, namespace: str) -> None:
        self._cpu = Gauge(
            "process_cpu_percent", "Process CPU utilization", namespace=namespace, registry=registry
        )
        self._memory = Gauge(
            "process_resident_memory_bytes",
            "Resident process memory",
            namespace=namespace,
            registry=registry,
        )
        self._uptime = Gauge(
            "process_uptime_seconds", "Process uptime", namespace=namespace, registry=registry
        )
        self._threads = Gauge(
            "process_threads", "Process thread count", namespace=namespace, registry=registry
        )
        self._process = psutil.Process(os.getpid())
        self._started = time.monotonic()

    def collect(self) -> ProcessSnapshot:
        """Collect local process data; safe to call from a periodic async task."""
        snapshot = ProcessSnapshot(
            cpu_percent=self._process.cpu_percent(),
            resident_memory_bytes=self._process.memory_info().rss,
            uptime_seconds=time.monotonic() - self._started,
            thread_count=self._process.num_threads(),
        )
        self._cpu.set(snapshot.cpu_percent)
        self._memory.set(snapshot.resident_memory_bytes)
        self._uptime.set(snapshot.uptime_seconds)
        self._threads.set(snapshot.thread_count)
        return snapshot


class InstrumentationHooks:
    """Narrow hooks for HTTP, workers, queues, pools, errors, and retries."""

    def __init__(self, metrics: ObservabilityMetrics) -> None:
        self._metrics = metrics

    def worker_job(
        self, worker: str, job: str, outcome: str, duration_seconds: float
    ) -> None:
        labels = {"worker": worker, "job": job, "outcome": outcome}
        self._metrics.worker_jobs.labels(**labels).inc()
        self._metrics.worker_duration.labels(worker=worker, job=job).observe(duration_seconds)

    def queue_depth(self, queue: str, depth: int) -> None:
        self._metrics.queue_depth.labels(queue=queue).set(depth)

    def queue_latency(self, queue: str, latency_seconds: float) -> None:
        self._metrics.queue_latency.labels(queue=queue).observe(latency_seconds)

    def blob_operation(
        self, provider: str, operation: str, outcome: str, *, bytes_transferred: int = 0
    ) -> None:
        self._metrics.blob_operations.labels(
            provider=provider, operation=operation, outcome=outcome
        ).inc()
        if bytes_transferred > 0:
            direction = "upload" if operation == "upload" else "download"
            self._metrics.blob_bytes.labels(provider=provider, direction=direction).inc(
                bytes_transferred
            )

    def ai_request(
        self,
        provider: str,
        model: str,
        operation: str,
        outcome: str,
        *,
        duration_seconds: float,
        input_tokens: int = 0,
        output_tokens: int = 0,
    ) -> None:
        labels = {
            "provider": provider,
            "model": model,
            "operation": operation,
            "outcome": outcome,
        }
        self._metrics.ai_requests.labels(**labels).inc()
        self._metrics.ai_duration.labels(
            provider=provider, model=model, operation=operation
        ).observe(duration_seconds)
        if input_tokens > 0:
            self._metrics.ai_tokens.labels(
                provider=provider, model=model, direction="input"
            ).inc(input_tokens)
        if output_tokens > 0:
            self._metrics.ai_tokens.labels(
                provider=provider, model=model, direction="output"
            ).inc(output_tokens)

    def auth_event(self, method: str, outcome: str) -> None:
        self._metrics.auth_events.labels(method=method, outcome=outcome).inc()

    def scheduler_job(self, job: str, outcome: str, *, lag_seconds: float | None = None) -> None:
        self._metrics.scheduler_jobs.labels(job=job, outcome=outcome).inc()
        if lag_seconds is not None:
            self._metrics.scheduler_lag.labels(job=job).set(lag_seconds)

    def cache_operation(self, backend: str, operation: str, outcome: str) -> None:
        self._metrics.cache_operations.labels(
            backend=backend, operation=operation, outcome=outcome
        ).inc()

    def database_operation(
        self,
        database: str,
        operation: str,
        outcome: str,
        *,
        duration_seconds: float,
    ) -> None:
        self._metrics.database_operations.labels(
            database=database, operation=operation, outcome=outcome
        ).inc()
        self._metrics.database_duration.labels(database=database, operation=operation).observe(
            duration_seconds
        )

    def pool_connections(self, pool: str, state: str, count: int) -> None:
        self._metrics.database_pool.labels(pool=pool, state=state).set(count)

    def error(self, boundary: str, code: str) -> None:
        self._metrics.errors.labels(boundary=boundary, code=code).inc()

    def retry(self, component: str, operation: str, reason: str) -> None:
        self._metrics.retries.labels(
            component=component, operation=operation, reason=reason
        ).inc()
