# Cloud Content Hub AI — alerting configuration.

Prometheus alert rules and Alertmanager routing for production operations.

## Layout

```
alerts/
├── prometheus/
│   └── alert_rules.yml    # All alert definitions
├── alertmanager/
│   └── alertmanager.yml   # Routing, receivers, inhibition
└── routing/
    └── severity_matrix.yaml
```

## Alert catalog

| Alert                       | Severity | Component  | Runbook                          |
| --------------------------- | -------- | ---------- | -------------------------------- |
| `CchApiUnavailable`         | critical | api        | RUNBOOKS.md#api-unavailable      |
| `CchApiHighErrorRate`       | critical | api        | RUNBOOKS.md#api-unavailable      |
| `CchApiHighLatency`         | warning  | api        | RUNBOOKS.md#high-latency         |
| `CchApiAvailabilitySLOBurn` | critical | api        | SLOS.md#availability             |
| `CchWorkerHighFailureRate`  | critical | worker     | RUNBOOKS.md#worker-crash         |
| `CchWorkerSuccessRateLow`   | warning  | worker     | SLOS.md#worker-success-rate      |
| `CchQueueDepthHigh`         | warning  | worker     | RUNBOOKS.md#worker-crash         |
| `CchOutboxBacklog`          | warning  | outbox     | RUNBOOKS.md#outbox-backlog       |
| `CchSchedulerLag`           | critical | scheduler  | RUNBOOKS.md#scheduler-failure    |
| `CchPublishSuccessRateLow`  | warning  | publishing | SLOS.md#publish-success-rate     |
| `CchDatabaseErrors`         | critical | database   | RUNBOOKS.md#database-unavailable |
| `CchCacheErrors`            | critical | redis      | RUNBOOKS.md#redis-unavailable    |
| `CchDatabasePoolExhaustion` | warning  | database   | OPERATIONS_GUIDE.md#capacity     |
| `CchStorageFailures`        | critical | storage    | RUNBOOKS.md#blob-storage-failure |
| `CchAiProviderFailures`     | warning  | ai         | RUNBOOKS.md#provider-outage      |
| `CchSocialProviderFailures` | warning  | social     | RUNBOOKS.md#provider-outage      |
| `CchAuthFailureSpike`       | warning  | auth       | RUNBOOKS.md#provider-outage      |

## Validation

```bash
python backend/operations/scripts/validate_alerts.py
```

## Recovery conditions

Each alert auto-resolves when its `expr` evaluates to false for the configured `for`
duration. Confirm recovery in Grafana dashboards before closing incidents.

## Related

- `docs/backend/sre/ALERTS.md`
- `docs/backend/observability/ALERTING.md`
- `backend/monitoring/prometheus/recording_rules.yml`
