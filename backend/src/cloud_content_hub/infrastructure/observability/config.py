"""Typed, provider-neutral observability configuration."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ObservabilityConfig:
    service_name: str
    service_version: str
    environment: str
    metrics_namespace: str = "cloud_content_hub"
    tracing_enabled: bool = True
    metrics_enabled: bool = True
    process_metrics_enabled: bool = True
    otlp_endpoint: str | None = None
    otlp_insecure: bool = False
    trace_sample_ratio: float = 1.0
    slow_request_seconds: float = 1.0
    health_timeout_seconds: float = 5.0
    excluded_http_paths: frozenset[str] = field(
        default_factory=lambda: frozenset({"/health", "/health/live", "/metrics"})
    )

    def __post_init__(self) -> None:
        if not 0.0 <= self.trace_sample_ratio <= 1.0:
            raise ValueError("trace_sample_ratio must be between zero and one")
        if self.slow_request_seconds <= 0 or self.health_timeout_seconds <= 0:
            raise ValueError("timeouts and thresholds must be positive")
