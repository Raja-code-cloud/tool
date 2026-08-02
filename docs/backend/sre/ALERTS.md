# Alerts

Alert definitions for Cloud Content Hub AI backend. All alerts derive from sustained
metric rates or SLO burn — not individual log lines or transient retries.

## Alert principles

1. Every alert has an **owner**, **severity**, **runbook**, **evaluation window**, and
   **recovery condition**.
2. Use multi-window burn-rate alerts for availability and latency SLOs.
3. Do not alert on expected 4xx responses, individual retries, or transient provider blips.
4. Metrics are the source of truth for paging; `AlertSink` is for low-volume notifications only.

## Severity levels

| Severity | Page | Response SLA | Channel           |
| -------- | ---- | ------------ | ----------------- |
| critical | Yes  | 15 min       | PagerDuty + Slack |
| warning  | No   | 60 min       | Slack platform    |

Routing matrix: `backend/alerts/routing/severity_matrix.yaml`.

## Alert catalog

### API

| Alert                       | Condition          | For | Runbook                             |
| --------------------------- | ------------------ | --- | ----------------------------------- |
| `CchApiUnavailable`         | Scrape target down | 2m  | [API unavailable](#api-unavailable) |
| `CchApiHighErrorRate`       | 5xx > 1%           | 5m  | [API unavailable](#api-unavailable) |
| `CchApiHighLatency`         | p95 > 500ms        | 10m | [High latency](#high-latency)       |
| `CchApiAvailabilitySLOBurn` | Fast burn > 14.4×  | 5m  | SLOS.md                             |

### Workers

| Alert                      | Condition        | For | Runbook                       |
| -------------------------- | ---------------- | --- | ----------------------------- |
| `CchWorkerHighFailureRate` | Failures > 0.1/s | 5m  | [Worker crash](#worker-crash) |
| `CchWorkerSuccessRateLow`  | Success < 95%    | 10m | SLOS.md                       |
| `CchQueueDepthHigh`        | Depth > 1000     | 10m | [Worker crash](#worker-crash) |

### Publishing & scheduler

| Alert                      | Condition            | For | Runbook                                 |
| -------------------------- | -------------------- | --- | --------------------------------------- |
| `CchOutboxBacklog`         | Outbox retries > 1/s | 5m  | [Outbox backlog](#outbox-backlog)       |
| `CchSchedulerLag`          | Lag > 300s           | 5m  | [Scheduler failure](#scheduler-failure) |
| `CchPublishSuccessRateLow` | Success < 95%        | 10m | SLOS.md                                 |

### Dependencies

| Alert                       | Condition            | For | Runbook                                       |
| --------------------------- | -------------------- | --- | --------------------------------------------- |
| `CchDatabaseErrors`         | DB errors > 0.5/s    | 3m  | [Database unavailable](#database-unavailable) |
| `CchCacheErrors`            | Cache errors > 0.5/s | 3m  | [Redis unavailable](#redis-unavailable)       |
| `CchDatabasePoolExhaustion` | Pool > 90%           | 5m  | OPERATIONS_GUIDE.md                           |

### Providers

| Alert                       | Condition              | For | Runbook                                       |
| --------------------------- | ---------------------- | --- | --------------------------------------------- |
| `CchStorageFailures`        | Blob errors > 0.1/s    | 5m  | [Blob storage failure](#blob-storage-failure) |
| `CchAiProviderFailures`     | AI errors > 0.1/s      | 5m  | [Provider outage](#provider-outage)           |
| `CchSocialProviderFailures` | Social errors > 0.05/s | 5m  | [Provider outage](#provider-outage)           |
| `CchAuthFailureSpike`       | Auth failures > 1/s    | 5m  | [Provider outage](#provider-outage)           |

## Configuration files

- Rules: `backend/alerts/prometheus/alert_rules.yml`
- Alertmanager: `backend/alerts/alertmanager/alertmanager.yml`
- Recording rules: `backend/monitoring/prometheus/recording_rules.yml`

## Validation

```bash
python backend/operations/scripts/validate_alerts.py
```

## Testing alerts

1. Start local monitoring stack (`backend/operations/compose/monitoring-stack.yml`).
2. Inject fault (stop Redis, generate 5xx) in dev environment.
3. Confirm alert fires in Prometheus → Alertmanager within evaluation window.
4. Restore service; confirm alert resolves automatically.

## Related

- `RUNBOOKS.md` — response procedures
- `docs/backend/observability/ALERTING.md` — AlertSink protocol
