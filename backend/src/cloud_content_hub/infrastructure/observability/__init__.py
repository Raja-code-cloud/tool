"""Vendor-neutral observability building blocks."""

from .config import ObservabilityConfig
from .exceptions import (
    ExporterError,
    HealthCheckError,
    MetricRegistrationError,
    ObservabilityError,
    TelemetryConfigurationError,
)
from .factory import ObservabilityBundle, create_observability_bundle, create_registry
from .health import (
    AggregateHealth,
    ApplicationHealthCheck,
    HealthCheck,
    HealthChecker,
    HealthResult,
    HealthStatus,
    PingHealthCheck,
    create_ping_health_check,
)
from .logging import log_async_performance, log_performance, observability_processors
from .metrics import ObservabilityMetrics, PrometheusMetricFactory
from .middleware import ObservabilityMiddleware
from .prometheus import PrometheusASGIApp, create_prometheus_app
from .telemetry import InstrumentationHooks, ProcessSnapshot, ProcessTelemetry
from .tracing import (
    attach_context,
    background_span,
    client_span,
    current_trace_ids,
    detach_context,
    extract_context,
    get_tracer,
    http_span,
    inject_context,
    traced_operation,
)

__all__ = [
    "AggregateHealth",
    "ApplicationHealthCheck",
    "ExporterError",
    "HealthCheck",
    "HealthCheckError",
    "HealthChecker",
    "HealthResult",
    "HealthStatus",
    "InstrumentationHooks",
    "MetricRegistrationError",
    "ObservabilityBundle",
    "ObservabilityConfig",
    "ObservabilityError",
    "ObservabilityMetrics",
    "ObservabilityMiddleware",
    "PingHealthCheck",
    "ProcessSnapshot",
    "ProcessTelemetry",
    "PrometheusASGIApp",
    "PrometheusMetricFactory",
    "TelemetryConfigurationError",
    "attach_context",
    "background_span",
    "client_span",
    "create_observability_bundle",
    "create_ping_health_check",
    "create_prometheus_app",
    "create_registry",
    "current_trace_ids",
    "detach_context",
    "extract_context",
    "get_tracer",
    "http_span",
    "inject_context",
    "log_async_performance",
    "log_performance",
    "observability_processors",
    "traced_operation",
]
