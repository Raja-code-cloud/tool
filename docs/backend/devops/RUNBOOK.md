# Runbook

Operational procedures for Cloud Content Hub backend infrastructure.

## Service overview

| Service       | Identifier              | Port / access       |
| ------------- | ----------------------- | ------------------- |
| API           | `ca-cch-api-<env>`      | HTTPS ingress :8000 |
| Worker        | `ca-cch-worker-<env>`   | Internal            |
| Beat          | `ca-cch-beat-<env>`     | Internal            |
| Migration job | `caj-cch-migrate-<env>` | Manual trigger      |

## Health endpoints

| Endpoint            | Expected       | Action if failing                      |
| ------------------- | -------------- | -------------------------------------- |
| `GET /health/live`  | 200            | Restart container / rollback revision  |
| `GET /health/ready` | 200, checks ok | Inspect PostgreSQL, Redis connectivity |
| `GET /health`       | 200            | Informational only                     |

Legacy aliases `GET /live` and `GET /ready` remain available with identical responses.

## Common operations

### Local stack restart

```bash
docker compose -f docker/docker-compose.yml down
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up --build
```

### Run migrations

```bash
deployment/scripts/migrate.sh local
deployment/scripts/migrate.sh dev
```

### Verify deployment

```bash
deployment/scripts/verify-health.sh dev
```

### Scale API (ACA)

```bash
az containerapp update \
  --name ca-cch-api-prod \
  --resource-group rg-cch-prod \
  --min-replicas 2 \
  --max-replicas 20
```

## Incident triage

### API readiness 503

1. Check ACA revision status and recent deploy.
2. Verify PostgreSQL and Redis availability.
3. Inspect structured logs in Log Analytics (`service`, `environment`, `request_id`).
4. Roll back if failure correlates with latest revision.

### Worker backlog growth

1. Check Redis connectivity and Celery worker replica count.
2. Scale worker max replicas.
3. Inspect dead-letter / retry metrics (application observability).

### Migration job failure

1. Retrieve job execution logs from ACA.
2. Do not roll forward blindly on prod.
3. Fix migration or restore from PITR per database runbook.
4. Re-run `deployment/scripts/migrate.sh <env>` after fix.

## Logs

- Application emits JSON logs to stdout.
- Azure Log Analytics collects ACA app logs.
- Do not enable file-based logging in containers.

## Security incidents

- Rotate affected Key Vault secrets.
- Redeploy containers to pick up new secret versions.
- Run `security-scan.yml` or local `pip-audit` / Trivy before re-promotion.

## Backup and DR

- PostgreSQL: PITR enabled, quarterly restore drills.
- Redis: operational cache/queue; rebuild from retries where safe.
- Blob storage: geo-redundant storage per storage ops guide.
- DR environment: `parameters/dr.bicepparam`, fail over DNS to DR API FQDN.

## Contacts and escalation

Define on-call rotation and escalation paths in your team operations wiki. This runbook covers infrastructure actions only.

## Related documents

- `DEPLOYMENT_GUIDE.md`
- `DOCKER.md`
- `CI_CD.md`
- `AZURE_CONTAINER_APPS.md`
- `ENVIRONMENTS.md`
- `ROLLBACK.md`
