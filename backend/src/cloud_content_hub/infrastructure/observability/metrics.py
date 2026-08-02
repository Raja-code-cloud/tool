"""Reusable bounded-cardinality Prometheus metrics."""

from collections.abc import Mapping
from dataclasses import dataclass

from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram

from .interfaces import CounterMetric, GaugeMetric, HistogramMetric, MetricFactory

LATENCY_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10)


@dataclass(frozen=True, slots=True)
class ObservabilityMetrics:
    http_requests: Counter
    http_in_flight: Gauge
    http_duration: Histogram
    errors: Counter
    worker_jobs: Counter
    worker_duration: Histogram
    queue_depth: Gauge
    queue_latency: Histogram
    blob_operations: Counter
    blob_bytes: Counter
    ai_requests: Counter
    ai_duration: Histogram
    ai_tokens: Counter
    auth_events: Counter
    scheduler_jobs: Counter
    scheduler_lag: Gauge
    cache_operations: Counter
    database_operations: Counter
    database_duration: Histogram
    database_pool: Gauge
    retries: Counter

    @classmethod
    def create(
        cls,
        registry: CollectorRegistry,
        namespace: str = "cloud_content_hub",
    ) -> "ObservabilityMetrics":
        def counter(name: str, text: str, labels: tuple[str, ...]) -> Counter:
            return Counter(name, text, labels, namespace=namespace, registry=registry)

        def gauge(name: str, text: str, labels: tuple[str, ...]) -> Gauge:
            return Gauge(name, text, labels, namespace=namespace, registry=registry)

        def histogram(name: str, text: str, labels: tuple[str, ...]) -> Histogram:
            return Histogram(
                name, text, labels, namespace=namespace, registry=registry, buckets=LATENCY_BUCKETS
            )

        return cls(
            http_requests=counter(
                "http_requests_total", "HTTP requests", ("method", "route", "status_class")
            ),
            http_in_flight=gauge(
                "http_requests_in_flight", "In-flight HTTP requests", ("method",)
            ),
            http_duration=histogram(
                "http_request_duration_seconds", "HTTP request latency", ("method", "route")
            ),
            errors=counter("errors_total", "Errors by boundary and code", ("boundary", "code")),
            worker_jobs=counter(
                "worker_jobs_total",
                "Worker outcomes",
                ("worker", "job", "outcome"),
            ),
            worker_duration=histogram(
                "worker_job_duration_seconds", "Worker job latency", ("worker", "job")
            ),
            queue_depth=gauge("queue_depth", "Queue depth", ("queue",)),
            queue_latency=histogram("queue_latency_seconds", "Queue latency", ("queue",)),
            blob_operations=counter(
                "blob_operations_total",
                "Blob operation outcomes",
                ("provider", "operation", "outcome"),
            ),
            blob_bytes=counter(
                "blob_bytes_total", "Blob bytes transferred", ("provider", "direction")
            ),
            ai_requests=counter(
                "ai_requests_total",
                "AI request outcomes",
                ("provider", "model", "operation", "outcome"),
            ),
            ai_duration=histogram(
                "ai_request_duration_seconds",
                "AI request latency",
                ("provider", "model", "operation"),
            ),
            ai_tokens=counter(
                "ai_tokens_total", "AI tokens consumed", ("provider", "model", "direction")
            ),
            auth_events=counter(
                "auth_events_total", "Authentication outcomes", ("method", "outcome")
            ),
            scheduler_jobs=counter(
                "scheduler_jobs_total", "Scheduler outcomes", ("job", "outcome")
            ),
            scheduler_lag=gauge("scheduler_lag_seconds", "Scheduler lag", ("job",)),
            cache_operations=counter(
                "cache_operations_total",
                "Cache operation outcomes",
                ("backend", "operation", "outcome"),
            ),
            database_operations=counter(
                "database_operations_total",
                "Database outcomes",
                ("database", "operation", "outcome"),
            ),
            database_duration=histogram(
                "database_operation_duration_seconds",
                "Database operation latency",
                ("database", "operation"),
            ),
            database_pool=gauge(
                "database_pool_connections", "Database pool state", ("pool", "state")
            ),
            retries=counter(
                "retries_total", "Retry attempts", ("component", "operation", "reason")
            ),
        )


class PrometheusMetricFactory(MetricFactory):
    """DI-friendly custom metric factory using a caller-owned registry."""

    def __init__(self, registry: CollectorRegistry, namespace: str) -> None:
        self._registry = registry
        self._namespace = namespace

    def counter(self, name: str, description: str, labels: tuple[str, ...] = ()) -> CounterMetric:
        return _CounterAdapter(
            Counter(name, description, labels, namespace=self._namespace, registry=self._registry)
        )

    def gauge(self, name: str, description: str, labels: tuple[str, ...] = ()) -> GaugeMetric:
        return _GaugeAdapter(
            Gauge(name, description, labels, namespace=self._namespace, registry=self._registry)
        )

    def histogram(
        self, name: str, description: str, labels: tuple[str, ...] = ()
    ) -> HistogramMetric:
        return _HistogramAdapter(
            Histogram(name, description, labels, namespace=self._namespace, registry=self._registry)
        )


class _CounterAdapter:
    def __init__(self, metric: Counter) -> None:
        self._metric = metric

    def increment(self, amount: float = 1.0, labels: Mapping[str, str] | None = None) -> None:
        (self._metric.labels(**labels) if labels else self._metric).inc(amount)


class _GaugeAdapter:
    def __init__(self, metric: Gauge) -> None:
        self._metric = metric

    def set(self, value: float, labels: Mapping[str, str] | None = None) -> None:
        (self._metric.labels(**labels) if labels else self._metric).set(value)


class _HistogramAdapter:
    def __init__(self, metric: Histogram) -> None:
        self._metric = metric

    def observe(self, value: float, labels: Mapping[str, str] | None = None) -> None:
        (self._metric.labels(**labels) if labels else self._metric).observe(value)
