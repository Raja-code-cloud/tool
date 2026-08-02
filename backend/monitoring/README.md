# Cloud Content Hub AI — monitoring configuration.

Prometheus scrape configs, SLI recording rules, and Grafana dashboard definitions
for production observability.

## Layout

```
monitoring/
├── prometheus/
│   ├── prometheus.yml       # Scrape targets and rule file references
│   └── recording_rules.yml  # SLI / SLO burn recording rules
└── grafana/
    ├── provisioning/        # Datasource and dashboard provider config
    └── dashboards/          # Dashboard JSON definitions
```

## Metric namespace

All application metrics use the `cloud_content_hub_` prefix. See
`docs/backend/observability/METRICS.md` for the full catalog.

## Local stack

Start Prometheus, Alertmanager, and Grafana:

```bash
docker compose -f backend/operations/compose/monitoring-stack.yml up -d
```

- Prometheus: http://localhost:9090
- Alertmanager: http://localhost:9093
- Grafana: http://localhost:3001 (admin / admin)

## Dashboards

| Dashboard      | File                                     | Focus                               |
| -------------- | ---------------------------------------- | ----------------------------------- |
| API            | `grafana/dashboards/api.json`            | HTTP rate, latency, 5xx, in-flight  |
| Workers        | `grafana/dashboards/workers.json`        | Job outcomes, duration, queue depth |
| Scheduler      | `grafana/dashboards/scheduler.json`      | Scheduler lag and job outcomes      |
| Publishing     | `grafana/dashboards/publishing.json`     | Outbox retries, publish success     |
| Storage        | `grafana/dashboards/storage.json`        | Blob operations and transfer bytes  |
| Authentication | `grafana/dashboards/authentication.json` | Auth events by method/outcome       |
| Analytics      | `grafana/dashboards/analytics.json`      | Cross-cutting SLI overview          |
| Infrastructure | `grafana/dashboards/infrastructure.json` | DB pool, cache, process telemetry   |

Import dashboards into Grafana via provisioning or UI import.

## Production deployment

1. Deploy Prometheus (Azure Monitor managed Prometheus, self-hosted, or Grafana Cloud).
2. Configure scrape targets for each ACA API revision and worker metrics endpoint.
3. Load recording rules and alert rules from `backend/monitoring/prometheus/` and
   `backend/alerts/prometheus/`.
4. Restrict `/metrics` to internal network only.

## Related

- `docs/backend/sre/MONITORING.md`
- `docs/backend/observability/PROMETHEUS.md`
- `backend/alerts/README.md`
