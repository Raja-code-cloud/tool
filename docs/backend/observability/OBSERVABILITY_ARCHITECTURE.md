# Observability Architecture

## Goals

The observability package is vendor-neutral, dependency-injected, and has no import-time
initialization. Bootstrap code owns lifecycle and wiring; this package only supplies components.
Metrics, traces, and logs correlate through stable request, correlation, trace, and span IDs.

## Components

- `config.py`: immutable runtime settings.
- `factory.py`: DI-friendly bundle construction.
- `metrics.py`: bounded Prometheus instruments and custom metric ports.
- `tracing.py`: W3C propagation and spans for inbound, background, and client operations.
- `logging.py`: structlog enrichment, redaction, exceptions, and performance helpers.
- `middleware.py`: ASGI request instrumentation.
- `health.py`: concurrent async dependency checks and aggregate status.
- `telemetry.py`: process collection and queue/pool/error/retry hooks.
- `prometheus.py`: standalone ASGI metrics exporter.
- `exporters/`: provider adapters; OTLP is the default trace transport.
- `interfaces/`: stable extension protocols for metrics, exporters, and alert sinks.

## Composition

Create a caller-owned `CollectorRegistry`, then construct `ObservabilityMetrics`,
`ProcessTelemetry`, exporter lifecycles, middleware, and the Prometheus app. Start and stop
exporters in the process lifespan. No global registry or SDK provider is mutated except when the
explicit OTLP exporter lifecycle is started.

## Cardinality and security

Route templates and allowlisted dimensions are used instead of raw paths, IDs, queries, prompts,
provider payloads, SQL, or URLs. Unknown routes are labeled `unmatched`. Logs are fail-closed
redacted before serialization.
