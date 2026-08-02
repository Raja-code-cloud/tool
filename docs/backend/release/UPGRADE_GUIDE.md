# Upgrade Guide

Procedures for upgrading Cloud Content Hub backend between releases with minimal downtime and safe schema evolution.

## Upgrade principles

1. **Immutable images** — Build once, promote the same digest through environments.
2. **Migrations first** — Run Alembic upgrade before shifting API traffic to a new revision.
3. **Expand/contract** — Destructive schema changes use multi-phase migrations for zero-downtime.
4. **Backward compatibility** — New application versions must run against the current schema until migration completes; old versions may run against expanded schema during rollout windows.

## Environment promotion path

```text
local → dev → qa → prod
                  ↘ dr (same image as prod, independent infra)
```

Same Git SHA tag promoted at each stage. Do not rebuild for production with different source.

## Standard upgrade sequence

### 1. Pre-upgrade validation

- [ ] Review release notes and `KNOWN_ISSUES.md`
- [ ] Confirm CI green on target commit
- [ ] Run `pytest tests/release tests/deployment tests/smoke` locally or in CI
- [ ] Identify current Alembic head and target head revision

### 2. Build and push

```bash
deployment/scripts/build-images.sh <env> <git-sha>
```

### 3. Deploy infrastructure (if Bicep changed)

```bash
az deployment group create \
  --resource-group rg-cch-<env> \
  --template-file infra/container-apps/bicep/main.bicep \
  --parameters infra/container-apps/bicep/parameters/<env>.bicepparam \
  --parameters imageTag=<git-sha>
```

### 4. Run migrations

```bash
deployment/scripts/migrate.sh <env>
```

Wait for Container Apps Job success. Do not proceed if migration fails.

### 5. Rolling application update

Order:

1. Worker replicas (tolerate brief mixed versions if handlers are backward compatible)
2. Beat (single replica; brief scheduler pause acceptable)
3. API (keep prior revision active; shift traffic after health verification)

```bash
deployment/scripts/deploy.sh <env> <git-sha>
deployment/scripts/verify-health.sh <env>
```

### 6. Post-upgrade verification

```bash
export SMOKE_BASE_URL=https://<fqdn>
pytest tests/smoke -m "smoke and external" -v
```

Monitor for 30 minutes: 5xx rate, latency, queue depth, outbox lag.

## Zero-downtime deployment

Azure Container Apps supports multiple active revisions:

- Deploy new revision with 0% traffic
- Verify `/health/live` and `/health/ready` on the new revision (direct revision FQDN if available)
- Shift traffic incrementally (10% → 50% → 100%) or activate revision after smoke pass
- Deactivate failed revision on success

Requirements:

- Migrations are backward compatible with **previous** app version during rollout, OR
- Traffic is held at 0% on new revision until migration completes and only new app is deployed

## Migration compatibility

| Change type         | Strategy                                              |
| ------------------- | ----------------------------------------------------- |
| Add nullable column | Single migration; safe for old app                    |
| Add non-null column | Default value or multi-phase expand/contract          |
| Rename column       | Add new column → backfill → switch app → drop old     |
| Index addition      | Use `CREATE INDEX CONCURRENTLY` in production         |
| Table drop          | Contract phase after all app instances use new schema |

Test upgrades:

```bash
# Empty to head
alembic upgrade head

# From previous production revision (when migration tests exist)
pytest tests/ -m migration -v
```

## Configuration compatibility

- New settings must have safe defaults or be optional until configured
- Removing settings requires deprecation period across at least one release
- Feature flags live in database settings, not environment variables
- Production never loads `.env` files

When adding `CCH_*` variables:

1. Add to `backend/.env.example`
2. Document in `docs/backend/devops/ENVIRONMENTS.md`
3. Update Bicep env blocks if required at deploy time
4. Add validation in release test suite

## Backward compatibility

API contract:

- OpenAPI `/api/v1` paths remain stable within major version
- Additive response fields allowed; removing fields requires version bump
- Error codes documented in `docs/backend/api/ERROR_CODES.md`

Events:

- New event types require registry update
- `event_version` increments for breaking payload changes

Workers:

- Task names and routing keys must remain stable or use dual-registration during transition

## Rollback during upgrade

If upgrade fails after migration:

- **Backward-compatible migration:** Roll back application revision only (`ROLLBACK_GUIDE.md`)
- **Breaking migration:** Do not roll back app without schema repair; use PITR or forward-fix migration

## Version matrix template

Record for each release:

| Release | Git SHA | Alembic revision | Min compatible revision | Notes               |
| ------- | ------- | ---------------- | ----------------------- | ------------------- |
| 0.1.0   |         | bd3726e86063     | bd3726e86063            | Initial GA baseline |

## Local upgrade test

```bash
docker compose -f docker/docker-compose.yml down
git checkout <new-tag>
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up --build -d
docker compose --profile tools run --rm migrate
curl -fsS http://localhost:8000/health/live
curl -fsS http://localhost:8000/health/ready
pytest tests/smoke -m "smoke and not external" -q
```

## Related documents

- `docs/backend/database/MIGRATION_GUIDE.md`
- `docs/backend/devops/DEPLOYMENT_GUIDE.md`
- `ROLLBACK_GUIDE.md`
- `RC_CHECKLIST.md`
