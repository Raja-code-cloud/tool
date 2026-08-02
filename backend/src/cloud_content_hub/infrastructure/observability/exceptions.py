"""Observability-specific failures."""


class ObservabilityError(Exception):
    """Base observability failure."""


class TelemetryConfigurationError(ObservabilityError):
    """Raised when telemetry cannot be configured safely."""


class HealthCheckError(ObservabilityError):
    """Raised by a health dependency when it cannot report normally."""


class MetricRegistrationError(ObservabilityError):
    """Raised for an invalid custom metric registration."""


class ExporterError(ObservabilityError):
    """Raised when an exporter cannot be initialized."""
