# Alerting

Alerts derive from sustained metric rates, latency distributions, saturation, dependency health,
and service-level-objective burn. Suggested signals include elevated 5xx/error rates, queue lag,
worker terminal failures, database pool exhaustion, scheduler lag, AI/provider failures, and
memory growth.

Every alert has an owner, severity, runbook, evaluation window, and recovery condition. Use
multi-window burn-rate alerts for availability and latency objectives. Avoid alerts on isolated log
lines, individual retries, expected 4xx responses, or transient provider errors.

`AlertSink` is the asynchronous extension protocol for exceptional low-volume notifications.
Built-in vendor-neutral stubs live in `exporters/alerting.py`:

- `NoOpAlertSink`
- `AzureMonitorAlertSink`
- `ApplicationInsightsAlertSink`
- `GrafanaAlertSink`
- `DatadogAlertSink`
- `NewRelicAlertSink`

Implementations must apply timeouts, redact attributes, and avoid recursive alerts when the sink
fails. Metrics remain the source of truth for paging.
