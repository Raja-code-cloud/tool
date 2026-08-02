# Failover Plan

Failover procedures for Cloud Content Hub backend components and regional disaster recovery.

## Failover tiers

| Tier | Trigger | Method | Traffic impact |
| ---- | ------- | ------ | -------------- |
| T0 | Single container crash | ACA auto-restart / replica scale | None |
| T1 | Bad deploy | ACA revision rollback | Brief (< 1 min) |
| T2 | Dependency degradation | Scale workers, optional read-only mode | Partial |
| T3 | Single-region dependency loss | Restore / failover dependency | Minutes to hours |
| T4 | Regional outage | DR environment activation | Hours |

## Component failover

### API (Azure Container Apps)

**Detection:** `/ready` returns 503, ACA liveness failures, elevated 5xx.

**Failover:**

```bash
# Option A: Rollback revision
deployment/scripts/rollback.sh prod <healthy-revision>

# Option B: Scale out
az containerapp update \
  --name ca-cch-api-prod \
  --resource-group rg-cch-prod \
  --min-replicas 2
```

**Health probes (implemented routes):**

| Probe | Route | Failure action |
| ----- | ----- | -------------- |
| Liveness | `GET /live` | Restart container |
| Readiness | `GET /ready` | Remove from load balancer |

Note: Deployment scripts may reference `/health/live` and `/health/ready`. Align probe paths with implemented routes per `docs/backend/release/RC_CHECKLIST.md`.

### Worker (Celery)

**Detection:** Queue depth growth, worker job failure metrics, outbox lag degraded.

**Failover:**

1. Verify Redis connectivity.
2. Scale worker replicas:

```bash
az containerapp update \
  --name ca-cch-worker-prod \
  --resource-group rg-cch-prod \
  --max-replicas 25
```

3. If worker image is faulty, deploy prior tag:

```bash
deployment/scripts/deploy.sh prod <prior-git-sha>
```

**Recovery guarantee:** Outbox pattern ensures at-least-once redelivery after worker recovery (`docs/backend/events/OUTBOX_PATTERN.md`).

### Beat (Scheduler)

**Detection:** Missed scheduled publications, scheduler lag alerts.

**Failover:**

- Beat runs as fixed single replica (`minReplicas = maxReplicas = 1`).
- ACA restarts failed beat container automatically.
- Manual redeploy if image corruption suspected:

```bash
az containerapp update \
  --name ca-cch-beat-prod \
  --resource-group rg-cch-prod \
  --image acrcchprod.azurecr.io/cloud-content-hub-worker:<tag>
```

**Note:** Duplicate beat instances must never run simultaneously. Keep max replicas at 1.

### Outbox dispatcher

**Detection:** `outbox_dispatch` health check degraded, growing unpublished row count.

**Failover:**

1. Confirm database reachable.
2. Restart worker fleet (dispatcher runs in worker process).
3. Scale workers to increase dispatch throughput.
4. If poison messages accumulate, inspect `dead_letters` table.

### PostgreSQL

**Detection:** Readiness database check fails, connection pool exhaustion.

**Failover options:**

| Scenario | Action |
| -------- | ------ |
| Connection saturation | Scale API replicas down temporarily; increase DB compute |
| Server failure (HA enabled) | Azure automatic failover to standby |
| Data corruption | PITR restore per `RESTORE_GUIDE.md` |
| Regional loss | Geo-restore to DR region |

Application uses `postgresql+asyncpg://` with connection pooling. After failover, recycle all ACA revisions to reset pools.

### Redis

**Detection:** Readiness redis check fails, Celery connection errors.

**Failover:**

| Scenario | Action |
| -------- | ------ |
| Transient outage | Wait for Azure recovery; ACA restarts |
| Instance loss | Recreate cache; update Key Vault URL; redeploy |
| Regional loss | Provision DR Redis; update DR Key Vault |

Queued Celery tasks may be lost. Outbox redispatches integration events.

### Blob storage

**Detection:** Storage health check degraded (optional dependency on readiness).

Storage failure is **degraded**, not blocking, for API readiness. Upload/download operations fail until storage recovers.

**Failover:**

- GRS account failover for regional loss.
- Soft-delete undelete for accidental deletion.
- CDN origin update if using custom domain.

### AI / identity providers

**Detection:** Provider health metrics, administration provider status API.

**Failover:**

- AI: Route to secondary provider if configured; otherwise return 503 on generation endpoints.
- Identity: JWKS cache TTL bounds outage impact; fail closed when verification impossible (`docs/backend/SECURITY_GUIDELINES.md`).

## Regional DR failover (T4)

DR environment is defined in `infra/container-apps/bicep/parameters/dr.bicepparam`:

| Setting | Production | DR |
| ------- | ---------- | -- |
| Region | eastus | westus2 |
| Registry | acrcchprod | acrcchprod (shared) |
| Key Vault | kv-cch-prod | kv-cch-dr |
| Custom domain | api.cloudcontenthub.example | api-dr.cloudcontenthub.example |

### DR activation procedure

1. **Confirm regional outage** — Azure status, multi-service correlation.
2. **Database** — Geo-restore or promote read replica to DR region.
3. **Redis** — Ensure DR Redis instance available; update DR Key Vault.
4. **Blob storage** — Account failover or confirm GRS secondary accessible from westus2.
5. **Deploy ACA** — If not warm standby:

```bash
az deployment group create \
  --resource-group rg-cch-dr \
  --template-file infra/container-apps/bicep/main.bicep \
  --parameters infra/container-apps/bicep/parameters/dr.bicepparam \
  --parameters imageTag=<prod-git-sha>
```

6. **Run migrations** — `deployment/scripts/migrate.sh dr`
7. **Verify health** — `deployment/scripts/verify-health.sh dr`
8. **DNS failover** — Update global load balancer / Traffic Manager to DR FQDN.
9. **Communicate** — Status page, customer notification per BCP.

### Failback

After primary region recovery:

1. Reconcile data drift (DB replication lag, blob consistency).
2. Restore primary region services.
3. Gradual DNS traffic shift back to eastus.
4. Decommission temporary DR overrides.

## Failover validation

Automated simulations:

```bash
pytest tests/failover -m failover
```

Tests verify:

- Application startup after simulated dependency recovery
- Migration head consistency expectations
- Worker and queue recovery behavior
- Event replay through outbox redispatch

## Escalation

| Severity | Condition | Escalation |
| -------- | --------- | ---------- |
| SEV-2 | Single dependency degraded > 15 min | On-call SRE |
| SEV-1 | API unavailable > 5 min | Incident commander + platform |
| SEV-0 | Regional outage | DR activation + executive notification |

Emergency contacts (replace placeholders):

| Role | Contact |
| ---- | ------- |
| Incident commander | oncall-platform@example.com |
| Database administrator | dba-team@example.com |
| Security officer | security@example.com |
| Azure subscription owner | azure-admin@example.com |
