# Monitoring Strategy

Cloud Content Hub AI uses metrics-first observability. Prometheus is the source of truth
for alerting; logs and traces provide diagnostic context.

## Components monitored

| Component | Signals | Dashboard |
| --------- | ------- | --------- |
| FastAPI | HTTP rate, latency, 5xx, in-flight, errors | `backend/monitoring/grafana/dashboards/api.json` |
| Celery workers | Job outcomes, duration, queue depth/latency | `workers.json` |
| Outbox worker | Outbox retries, maintenance queue depth | `publishing.json` |
| Scheduler runtime | Scheduler lag, job outcomes | `scheduler.json` |
| Repository layer | Database operations, pool state, duration | `infrastructure.json` |
| Azure Blob | Operation outcomes, bytes transferred | `storage.json` |
| AI providers | Request outcomes, latency, tokens | `analytics.json` |
| Social providers | Error boundary metrics | `analytics.json` |
| Redis | Cache operation outcomes | `infrastructure.json` |
| PostgreSQL | Database errors, pool connections | `infrastructure.json` |
| Authentication | Auth events by method/outcome | `authentication.json` |

## Metric namespace

All application metrics use the `cloud_content_hub_` prefix. SLI recording rules
live in `backend/monitoring/prometheus/recording_rules.yml` with the `cch:` prefix.

## Scrape configuration

| Target | Path | Interval | Notes |
| ------ | ---- | -------- | ----- |
| API (ACA) | `/metrics` | 30s | Internal network only |
| Worker | `/metrics` | 30s | Optional sidecar on port 9100 |
| Prometheus self | `/metrics` | 30s | Self-monitoring |

See `backend/monitoring/prometheus/prometheus.yml` for target definitions.

## Health vs metrics

| Probe | Path | Purpose |
| ----- | ---- | ------- |
| Liveness | `/health/live` | Process alive |
| Readiness | `/health/ready` | PostgreSQL + Redis |
| Informational | `/health` | Version metadata |
| Admin aggregate | `/api/v1/admin/system` | Full dependency health (auth required) |

Legacy aliases `/live` and `/ready` remain available for backwards compatibility and
return identical responses. They are excluded from OpenAPI.

Probe definitions: `backend/operations/probes.yaml`.

## Logging and tracing

- Structured JSON logs to stdout → Azure Log Analytics.
- OpenTelemetry traces via OTLP when `CCH_OTLP_*` is configured.
- Correlate incidents using `request_id` in logs and trace context.

See `docs/backend/observability/` for logging and tracing details.

## Local monitoring stack

```bash
docker compose -f backend/operations/compose/monitoring-stack.yml up -d
```

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001
- Alertmanager: http://localhost:9093

## Wiring checklist

Before production, confirm:

1. `/metrics` mounted on API (see `create_prometheus_app` in observability layer).
2. `ObservabilityMiddleware` mounted for HTTP metrics.
3. `ProcessTelemetry.collect()` scheduled periodically.
4. `InstrumentationHooks.pool_connections()` called from DB session layer.
5. Scrape targets registered in Prometheus for all replicas.

## Related

- `ALERTS.md` — alert definitions and routing
- `SLOS.md` — service level objectives
- `docs/backend/observability/METRICS.md` — metric catalog
