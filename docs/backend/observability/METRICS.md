# Metrics

All names are prefixed by the configured namespace. A process owns its
`CollectorRegistry`; tests should create a fresh registry.

## Built-in families

- HTTP: request count, in-flight requests, and duration.
- Errors: boundary and stable error code.
- Workers and queues: outcomes, duration, depth, and queue latency.
- Blob: operations and transferred bytes.
- AI: outcomes, duration, and input/output tokens by approved provider/model.
- Authentication: method and outcome.
- Scheduler: job outcomes and lag.
- Cache: backend operation and outcome.
- Database: operation outcomes/duration and pool state.
- Retry: component, operation, and bounded reason.
- Process: CPU, resident memory, uptime, and threads.

Never use user, workspace, request, content, URL, exception message, SQL, or prompt values as
labels. Provider/model/job values must come from controlled configuration. `MetricFactory` allows
features to define custom counters, gauges, and histograms without importing Prometheus.
