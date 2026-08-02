# Rollback Guide

Operational rollback procedures for Cloud Content Hub backend. Infrastructure rollback is revision-based on Azure Container Apps. Database rollback is forward-only unless a dedicated repair playbook applies.

## Decision matrix

| Symptom                                      | Roll back app | Roll back DB | Notes                          |
| -------------------------------------------- | ------------- | ------------ | ------------------------------ |
| Readiness 503 after deploy                   | Yes           | No           | Prior revision likely healthy  |
| Elevated 5xx / failed smoke tests            | Yes           | No           | Correlate with deploy time     |
| Migration job failure                        | No*           | Repair       | Do not roll forward blindly    |
| Schema incompatible with old app             | Yes           | Expand/contract | Requires migration playbook |
| Security incident (compromised secret)       | Redeploy      | No           | Rotate secrets, redeploy all   |

\*Fix migration or restore from PITR before resuming deploy.

## Application rollback (Azure Container Apps)

### 1. Identify revisions

```bash
az containerapp revision list \
  --name ca-cch-api-<env> \
  --resource-group rg-cch-<env> \
  --query "[].{name:name, active:properties.active, created:properties.createdTime, traffic:properties.trafficWeight}" \
  -o table
```

Record:

- Failed revision name and image tag
- Target rollback revision name and image tag

### 2. Activate prior revision

```bash
deployment/scripts/rollback.sh <env> <revision-name>
```

Or via GitHub Actions `backend-cd.yml` with `rollback_revision` input (skips image build).

### 3. Roll back worker and beat

Deploy the same image tag/digest used by the rollback API revision:

```bash
# Update worker and beat container apps to prior image tag
az containerapp update \
  --name ca-cch-worker-<env> \
  --resource-group rg-cch-<env> \
  --image <acr>/<image>:<prior-sha>

az containerapp update \
  --name ca-cch-beat-<env> \
  --resource-group rg-cch-<env> \
  --image <acr>/<image>:<prior-sha>
```

### 4. Verify health

```bash
deployment/scripts/verify-health.sh <env>
```

Confirm:

- Liveness probe returns 200
- Readiness probe returns 200
- Error rate and queue depth normalize within 15 minutes

Run smoke tests:

```bash
export SMOKE_BASE_URL=https://<api-fqdn>
pytest tests/smoke -m "smoke and external" -v
```

## Database rollback strategy

Alembic migrations are **forward-only** by default. Automated schema rollback is not supported.

### Safe approaches

1. **No migration deployed:** App rollback alone is sufficient.
2. **Expand/contract migration:** Old app runs against expanded schema until contract phase completes. Roll back app only; do not downgrade schema until contract migration runs.
3. **Failed migration mid-flight:** Stop deploy, repair migration script, restore from PITR if data corruption occurred, re-run `deployment/scripts/migrate.sh <env>` after fix.
4. **Point-in-time restore:** Use PostgreSQL PITR to a timestamp before failed deploy. Requires application downtime and coordinated secret/config validation.

### Never

- Run `alembic downgrade` in production without explicit playbook approval
- Roll forward application while migration job failed
- Delete failed revision before capturing logs and image tag

## Container rollback

| Component | Method                                      |
| --------- | ------------------------------------------- |
| API       | ACA revision activation (traffic shift)     |
| Worker    | Prior image tag/digest on worker container  |
| Beat      | Prior image tag/digest on beat container    |
| Migrate   | Re-run job with fixed migration or prior image |

Docker Compose local rollback:

```bash
export IMAGE_TAG=<prior-sha>
docker compose -f docker/docker-compose.yml pull api worker
docker compose -f docker/docker-compose.yml up -d api worker
```

## Configuration rollback

- ACA environment variables and Key Vault secret **versions** are revision-scoped for image but secrets are shared.
- To rollback configuration: restore prior Key Vault secret version, then restart/redeploy containers.
- Document all config changes in the change ticket.

## Rollback verification checklist

- [ ] API liveness and readiness return 200
- [ ] Worker processing resumes; queue depth decreases
- [ ] No new migration errors in logs
- [ ] Smoke tests pass against rolled-back environment
- [ ] Incident ticket updated with recovery time and root cause hypothesis

## Rollback records

Capture in the incident ticket:

| Field                 | Value |
| --------------------- | ----- |
| Environment           |       |
| Failed revision       |       |
| Failed image tag      |       |
| Rollback revision     |       |
| Rollback image tag    |       |
| Migration job status  |       |
| Time to recovery      |       |
| Customer impact       |       |

## Prevention

- Promote identical image digests dev → qa → prod
- Run migration job before increasing API traffic
- Keep at least one prior active revision during deploy windows
- Run `pytest tests/deployment -m deployment` in CI before promotion

## Related documents

- `docs/backend/devops/ROLLBACK.md`
- `docs/backend/devops/RUNBOOK.md`
- `docs/backend/database/MIGRATION_GUIDE.md`
- `KNOWN_ISSUES.md`
