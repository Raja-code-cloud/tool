# Service Level Objectives

SLOs for Cloud Content Hub AI backend. SLIs are computed from Prometheus recording rules
in `backend/monitoring/prometheus/recording_rules.yml`.

## Availability

| SLI | Target | Window | Measurement |
| --- | ------ | ------ | ----------- |
| API availability | 99.9% | 30 days | `cch:api_availability:ratio5m` |
| Worker success rate | 99.0% | 30 days | `cch:worker_success:ratio5m` |
| Publish success rate | 99.0% | 30 days | `cch:publish_success:ratio5m` |

**Error budget (availability):** 0.1% = ~43 minutes downtime per 30 days.

Burn-rate alert: `CchApiAvailabilitySLOBurn` (14.4× fast burn over 1 hour).

## Latency

| SLI | Target | Window | Measurement |
| --- | ------ | ------ | ----------- |
| API p95 latency | < 500ms | 30 days | `cch:api_latency:p95_5m` |
| API p99 latency | < 1s | 30 days | `cch:api_latency:p99_5m` |
| Queue processing p95 | < 60s | 7 days | `cch:queue_latency:p95_5m` |

Alert: `CchApiHighLatency` when p95 > 500ms for 10 minutes.

## Publish success rate

Scheduled and outbox-driven publishes must succeed at ≥ 99% over 30 days.

- SLI: `cch:publish_success:ratio5m`
- Alert: `CchPublishSuccessRateLow`
- Runbook: RUNBOOKS.md#outbox-backlog

## Queue processing time

Background jobs (media, ai, notification, maintenance) should complete within SLO:

| Queue | p95 target |
| ----- | ---------- |
| media | 120s |
| ai | 300s |
| notification | 30s |
| maintenance | 60s |

SLI: `cch:queue_latency:p95_5m` by queue label.

## Worker success rate

Celery task terminal success rate ≥ 99% over 30 days.

- SLI: `cch:worker_success:ratio5m`
- Alert: `CchWorkerSuccessRateLow`
- Excludes expected retries; measures terminal outcomes only.

## Recovery objectives

| Objective | Target | Scope |
| --------- | ------ | ----- |
| RTO (API) | 30 min | Full API restoration after regional failure |
| RPO (database) | 5 min | PostgreSQL PITR granularity |
| RTO (workers) | 15 min | Worker fleet scaled or restarted |
| RTO (outbox) | 60 min | Backlog drained after dispatch recovery |

DR procedures: `docs/backend/devops/RUNBOOK.md` (Backup and DR section).

## SLO review cadence

- Weekly: review burn rates and near-misses in Grafana analytics dashboard.
- Monthly: adjust targets if consistently over/under provisioned.
- Post-incident: recalculate error budget consumption.

## Related

- `ALERTS.md` — SLO-linked alerts
- `MONITORING.md` — SLI recording rules
- `INCIDENT_RESPONSE.md` — escalation during SLO breach
