# Operations Guide

Day-to-day operational procedures for Cloud Content Hub AI backend.

## Service topology

| Unit | Identifier | Scaling | Health |
| ---- | ---------- | ------- | ------ |
| API | `ca-cch-api-<env>` | HTTP concurrency | `/health/live`, `/health/ready` |
| Worker | `ca-cch-worker-<env>` | CPU utilization | Celery inspect + exec probe |
| Beat | `ca-cch-beat-<env>` | Fixed 1 replica | Schedule file + inspect |
| Migrate | `caj-cch-migrate-<env>` | Manual job | N/A |

## Health probe validation

```bash
# Local
./backend/operations/scripts/validate_health.sh

# Remote (replace FQDN)
./backend/operations/scripts/validate_health.sh https://ca-cch-api-dev.example.com
```

Probe definitions: `backend/operations/probes.yaml`.

### Probe paths

Canonical probe routes:

| Probe | Path | Notes |
| ----- | ---- | ----- |
| Liveness | `GET /health/live` | Process alive; no dependency checks |
| Readiness | `GET /health/ready` | PostgreSQL + Redis must respond |
| Summary | `GET /health` | Version metadata |

Legacy compatibility aliases `GET /live` and `GET /ready` remain available and return
identical responses. They are excluded from OpenAPI. New integrations must use the
canonical `/health/*` paths.

## Monitoring stack

### Local development

```bash
docker compose -f backend/operations/compose/monitoring-stack.yml up -d
```

Access Grafana at http://localhost:3001 (admin/admin).

### Production

1. Deploy Prometheus with rules from `backend/monitoring/` and `backend/alerts/`.
2. Configure scrape targets for all API replicas.
3. Import Grafana dashboards from `backend/monitoring/grafana/dashboards/`.
4. Wire Alertmanager receivers (PagerDuty, Slack).

See `MONITORING.md` for full strategy.

## Capacity

Reference: `backend/operations/capacity.yaml`.

### Connection pools

- Default pool size: 5 per process (`CCH_DATABASE_POOL_SIZE`, max 50).
- Total connections ≈ `(api_replicas + worker_replicas) × pool_size`.
- Monitor `cloud_content_hub_database_pool_connections`.
- Alert: `CchDatabasePoolExhaustion` at 90% utilization.

### Worker scaling

| Environment | Min | Max | Concurrency |
| ----------- | --- | --- | ----------- |
| dev | 1 | 3 | 2 (local) / 4 (ACA) |
| prod | 2 | 30 | 4 |

Scale when `CchQueueDepthHigh` or queue latency SLO burns.

### API scaling

| Environment | Min | Max | Trigger |
| ----------- | --- | --- | ------- |
| dev | 1 | 3 | HTTP concurrency 100 |
| prod | 2 | 20 | HTTP concurrency 100 |

```bash
az containerapp update --name ca-cch-api-prod --resource-group rg-cch-prod \
  --min-replicas 2 --max-replicas 20
```

### Queue sizing

Queues: `media`, `ai`, `notification`, `maintenance`.

- Outbox dispatch uses `maintenance` queue.
- DLQ prefix: `cloud_content_hub:dlq:{task_name}`
- Outbox batch size: 100; lag warning: 60s.

### Redis sizing

| Environment | Memory |
| ----------- | ------ |
| dev | 256Mi |
| qa | 512Mi |
| prod | 2Gi |

Monitor memory usage and evictions. Redis holds broker, results, DLQ, and cache.

### Database sizing

Size PostgreSQL `max_connections` for total app pool budget plus 20% headroom.
Example prod: 10 API + 15 worker replicas × 5 pool = 125 → recommend 200 max.

## Deployment verification

```bash
deployment/scripts/migrate.sh <env>
deployment/scripts/verify-health.sh <env>
```

Align `verify-health.sh` probe paths with implemented routes before use.

## Observability wiring checklist

Before declaring production-ready:

- [ ] `/metrics` exposed on API (internal only)
- [ ] HTTP middleware recording request metrics
- [ ] Process telemetry collected periodically
- [ ] DB pool metrics populated
- [ ] Prometheus scraping all replicas
- [ ] Alert rules loaded and validated
- [ ] Grafana dashboards imported
- [ ] Alertmanager receivers configured
- [ ] Health probes aligned with implemented routes

## Related

- `RUNBOOKS.md` — incident procedures
- `SLOS.md` — service level objectives
- `docs/backend/devops/DEPLOYMENT_GUIDE.md` — deployment process
