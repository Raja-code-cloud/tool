"""Composition helpers for dependency injection."""

from dataclasses import dataclass

from opentelemetry.trace import Tracer
from prometheus_client import CollectorRegistry

from .config import ObservabilityConfig
from .metrics import ObservabilityMetrics, PrometheusMetricFactory
from .telemetry import InstrumentationHooks, ProcessTelemetry
from .tracing import get_tracer


@dataclass(frozen=True, slots=True)
class ObservabilityBundle:
    """Caller-owned observability components suitable for bootstrap wiring."""

    config: ObservabilityConfig
    registry: CollectorRegistry
    metrics: ObservabilityMetrics
    process_telemetry: ProcessTelemetry
    hooks: InstrumentationHooks
    metric_factory: PrometheusMetricFactory
    tracer: Tracer


def create_registry(*, include_default_collectors: bool = False) -> CollectorRegistry:
    """Create an explicitly owned registry suitable for tests and DI."""
    return CollectorRegistry(auto_describe=include_default_collectors)


def create_observability_bundle(config: ObservabilityConfig) -> ObservabilityBundle:
    """Construct the standard observability stack without global side effects."""
    registry = create_registry()
    metrics = ObservabilityMetrics.create(registry, config.metrics_namespace)
    process_telemetry = ProcessTelemetry(registry, config.metrics_namespace)
    return ObservabilityBundle(
        config=config,
        registry=registry,
        metrics=metrics,
        process_telemetry=process_telemetry,
        hooks=InstrumentationHooks(metrics),
        metric_factory=PrometheusMetricFactory(registry, config.metrics_namespace),
        tracer=get_tracer(config.service_name, config.service_version),
    )
