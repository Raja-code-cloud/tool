# Rollback

Backend rollback is revision-based on Azure Container Apps. Images are immutable; rollback activates a previously healthy revision rather than rebuilding.

## When to rollback

- Readiness failures after deploy (`/health/ready` returns 503)
- Elevated error rate or failed smoke checks
- Migration job failure blocking safe operation

## Azure Container Apps rollback

List revisions:

```bash
az containerapp revision list \
  --name ca-cch-api-<env> \
  --resource-group rg-cch-<env> \
  --query "[].{name:name, active:properties.active, created:properties.createdTime}" \
  -o table
```

Activate prior revision:

```bash
deployment/scripts/rollback.sh <env> <revision-name>
```

Or via GitHub Actions `backend-cd.yml` with `rollback_revision` input (skips image build).

## Rollback scope

| Component | Rollback method                                        |
| --------- | ------------------------------------------------------ |
| API       | Revision activation (traffic shift)                    |
| Worker    | Deploy prior worker image tag/digest                   |
| Beat      | Deploy prior worker image tag/digest                   |
| Database  | Forward-only migrations; use migration repair playbook |

Database schema rollback is not automated. Follow `MIGRATION_STRATEGY.md` for expand/contract reversals.

## Verification after rollback

```bash
deployment/scripts/verify-health.sh <env>
```

Confirm:

- `/health/live` returns 200
- `/health/ready` returns 200 with database and redis checks ok
- Error budget and queue depth normalize

## Rollback records

Capture in the incident ticket:

- Environment
- Failed revision and image tag
- Activated rollback revision
- Migration job status
- Time to recovery

## Prevention

- Promote identical image tags dev → qa → prod
- Run migration job before API traffic increase
- Keep at least one prior active revision during deploy windows
