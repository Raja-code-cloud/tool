# Restore Guide

Step-by-step procedures to restore Cloud Content Hub backend dependencies after data loss, corruption, or regional failure.

**Prerequisites:** Incident commander assigned, change freeze on production deploys, communication channel open.

## Decision tree

```text
Data loss scope?
├── Single dependency (DB / Redis / Blob / Secrets)
│   └── Follow component restore below
├── Application regression (bad deploy)
│   └── ROLLBACK.md — ACA revision activation
└── Regional outage (eastus unavailable)
    └── FAILOVER_PLAN.md — DR environment activation
```

## 1. PostgreSQL restore

### Point-in-time recovery (preferred)

Use when data corruption or accidental deletion occurred within the PITR window.

```bash
# Identify restore target timestamp (UTC)
RESTORE_TIME="2026-08-02T14:30:00Z"
SOURCE_SERVER="psql-cch-prod"
TARGET_SERVER="psql-cch-prod-restored"
RESOURCE_GROUP="rg-cch-prod"

az postgres flexible-server restore \
  --resource-group "$RESOURCE_GROUP" \
  --name "$TARGET_SERVER" \
  --source-server "/subscriptions/<sub>/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.DBforPostgreSQL/flexibleServers/$SOURCE_SERVER" \
  --restore-time "$RESTORE_TIME"
```

Post-restore validation:

```bash
# Confirm Alembic head
cd backend
CCH_DATABASE_URL="postgresql+asyncpg://..." alembic current

# Schema sanity
psql "$DATABASE_URL" -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"
# Expect 86 tables at initial GA baseline
```

### Cutover to restored server

1. Update Key Vault secret `CCH-DATABASE-URL` and `CCH-MIGRATION-DATABASE-URL` to point at restored server.
2. Activate new ACA revision (API, worker, beat) to reload secrets.
3. Run migration job only if restored instance is behind head revision.
4. Verify readiness:

```bash
deployment/scripts/verify-health.sh prod
```

### Geo-restore (regional loss)

When primary region is unavailable and geo-redundant backup is enabled:

```bash
az postgres flexible-server geo-restore \
  --resource-group rg-cch-dr \
  --name psql-cch-dr \
  --source-server-id "/subscriptions/<sub>/resourceGroups/rg-cch-prod/providers/Microsoft.DBforPostgreSQL/flexibleServers/psql-cch-prod"
```

Follow DR cutover in `FAILOVER_PLAN.md`.

## 2. Blob storage recovery

### Single blob restore (soft delete)

```bash
az storage blob undelete \
  --account-name stcchprod \
  --container-name posters \
  --name "<workspace-id>/<asset-id>/original.png"
```

### Container-level recovery

Use Azure Portal **Storage browser → Soft deleted blobs** or lifecycle management policies.

### Account failover (GRS)

For regional storage account failure:

```bash
az storage account failover \
  --name stcchprod \
  --resource-group rg-cch-prod
```

**Warning:** Failover is irreversible until Microsoft reverses. Coordinate with incident commander.

Post-restore validation:

1. Health check reports storage as `healthy` or `degraded` (not `unhealthy`).
2. Sample download of known asset blob succeeds.
3. Database blob path references resolve to existing objects.

## 3. Redis recovery

Redis is rebuilt rather than restored in the default architecture.

### Standard recovery (no persistence)

1. Provision or restart Azure Cache for Redis instance.
2. Update Key Vault `CCH-REDIS-URL`.
3. Redeploy API, worker, and beat containers.
4. Scale workers to drain outbox backlog:

```bash
az containerapp update \
  --name ca-cch-worker-prod \
  --resource-group rg-cch-prod \
  --max-replicas 20
```

5. Monitor outbox lag metric until normalized.

### With RDB persistence (optional)

If premium persistence is enabled:

```bash
az redis force-reboot \
  --name redis-cch-prod \
  --resource-group rg-cch-prod \
  --reboot-type AllNodes
```

Expect partial loss of un-persisted queue entries. Outbox redispatches unpublished events.

## 4. Secrets recovery

Key Vault soft-deleted secrets:

```bash
az keyvault secret list-deleted \
  --vault-name kv-cch-prod

az keyvault secret recover \
  --vault-name kv-cch-prod \
  --name CCH-DATABASE-URL
```

Rotation after compromise:

1. Rotate credentials at source (PostgreSQL user, Redis access key).
2. Store new version in Key Vault.
3. Redeploy all ACA apps to pick up latest secret version.
4. Revoke prior credential version after verification.

## 5. Container recovery

### Revision rollback (fastest)

```bash
deployment/scripts/rollback.sh prod <prior-revision-name>
deployment/scripts/verify-health.sh prod
```

See `docs/backend/devops/ROLLBACK.md`.

### Full redeploy

When revision history is unavailable:

```bash
export IMAGE_TAG=<last-known-good-sha>
deployment/scripts/deploy.sh prod "$IMAGE_TAG"
deployment/scripts/migrate.sh prod
deployment/scripts/verify-health.sh prod
```

### Migration job recovery

Failed migration blocks safe operation:

```bash
az containerapp job execution list \
  --name caj-cch-migrate-prod \
  --resource-group rg-cch-prod

# After fix or DB restore:
deployment/scripts/migrate.sh prod
```

## 6. Outbox and event replay

After database restore, unpublished outbox rows are redispatched automatically by the outbox dispatcher.

Manual intervention when dispatcher was down during extended outage:

1. Confirm `outbox_events` rows with `published_at IS NULL` and `available_at <= now()`.
2. Restart worker replicas to resume Celery consumption.
3. Monitor `outbox_dispatch` health check — degraded indicates lag, unhealthy indicates database unreachable.
4. Inspect `dead_letters` for events that exhausted retries; replay per operations ticket.

Global events that cannot dead-letter require manual replay from audit logs.

## 7. Configuration restore

| Source | Restore action |
| ------ | -------------- |
| Bicep parameters | Redeploy from Git tag matching last known good |
| Key Vault | Recover soft-deleted secrets or restore from HSM backup |
| Database settings | Included in PostgreSQL PITR |
| `.env` (local only) | Copy from team password manager; never from Git |

Production and DR never load `.env` files (`docs/backend/devops/ENVIRONMENTS.md`).

## Verification checklist

After any restore:

- [ ] `GET /live` returns 200
- [ ] `GET /ready` returns 200 (database + Redis ok)
- [ ] Alembic head matches expected revision
- [ ] Outbox lag within warning threshold
- [ ] Worker queue depth decreasing
- [ ] Sample authenticated API call succeeds
- [ ] Blob upload/download round-trip succeeds
- [ ] No elevated 5xx rate in Log Analytics (15-minute window)

## Automated restore validation

```bash
pytest tests/backup/test_restore_validation.py -m backup
pytest tests/failover/test_migration_consistency.py -m failover
```

Integration tests require `CCH_DATABASE_URL` or `DATABASE_URL`.
