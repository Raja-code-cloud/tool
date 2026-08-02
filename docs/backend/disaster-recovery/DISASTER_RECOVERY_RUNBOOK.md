# Disaster Recovery Runbook

Scenario playbooks for Cloud Content Hub backend incidents. Use with `docs/backend/devops/RUNBOOK.md` for day-to-day operations.

## Incident response phases

```text
Detect → Triage → Contain → Recover → Verify → Post-incident review
```

| Phase | Owner | Key actions |
| ----- | ----- | ----------- |
| Detect | Monitoring / on-call | Alert fires, customer report, health check failure |
| Triage | Incident commander | Classify severity, assign workstreams |
| Contain | SRE | Stop bleeding — rollback, scale, isolate |
| Recover | Platform + Engineering | Restore data, redeploy, fail over |
| Verify | Engineering | Health checks, smoke tests, metrics normalization |
| Review | All | Timeline, RTO/RPO achieved, action items |

## Severity classification

| Level | Criteria | Response |
| ----- | -------- | -------- |
| SEV-3 | Degraded non-critical dependency | Business hours fix |
| SEV-2 | Readiness failures, worker backlog | On-call within 15 min |
| SEV-1 | API unavailable for tenants | Immediate, all-hands |
| SEV-0 | Regional / data loss event | DR activation |

---

## Scenario: Database unavailable

**Symptoms:** `/health/ready` database check `unavailable`, 503 responses, SQLAlchemy pool errors.

**Immediate actions:**

1. Check Azure PostgreSQL server status in portal.
2. Review recent deploys and migration job executions.
3. Confirm connection string in Key Vault unchanged.

**Recovery paths:**

| Cause | Action |
| ----- | ------ |
| Azure platform outage | Monitor Azure status; prepare DR if prolonged |
| Connection limit | Reduce API min replicas temporarily |
| Failed migration | Stop deploys; PITR restore if schema corrupted |
| Credential rotation error | Fix Key Vault secret; redeploy ACA |

**Verification:**

```bash
deployment/scripts/verify-health.sh <env>
pytest tests/disaster_recovery/test_dependency_unavailability.py -m disaster_recovery
```

**RTO target:** 4 hours (PITR) / 60 seconds (HA failover)

---

## Scenario: Redis unavailable

**Symptoms:** `/health/ready` redis check `unavailable`, Celery connection errors, cache misses only.

**Immediate actions:**

1. Check Azure Cache for Redis status.
2. Do **not** restart API if database is healthy — readiness correctly fails.

**Recovery:**

1. Restore Redis instance or fail over to DR Redis.
2. Update `CCH-REDIS-URL` in Key Vault.
3. Redeploy API, worker, beat.
4. Scale workers to process outbox backlog.

**Data impact:** In-flight Celery tasks may be lost. Outbox redispatches unpublished events.

**RTO target:** 30 minutes

---

## Scenario: Blob storage unavailable

**Symptoms:** Storage health degraded, upload/download 503/502, readiness may still pass.

**Immediate actions:**

1. Check storage account health and throttling metrics.
2. Identify scope — single container vs account-wide.

**Recovery:**

| Cause | Action |
| ----- | ------ |
| Throttling | Backoff retries; scale down bulk export jobs |
| Regional outage | GRS account failover |
| Accidental delete | Soft-delete undelete |
| Credential failure | Rotate storage identity / keys |

**Verification:** Storage health check returns healthy; sample blob round-trip.

**RTO target:** 4 hours (regional), 1 hour (undelete)

---

## Scenario: Container failure

**Symptoms:** ACA revision unhealthy, liveness probe failures, single-replica crash loop.

**Immediate actions:**

1. List revisions and identify failing image tag.
2. Check container logs in Log Analytics.

**Recovery:**

```bash
# Rollback to last healthy revision
deployment/scripts/rollback.sh prod <revision>

# Or restart latest
az containerapp revision restart \
  --name ca-cch-api-prod \
  --resource-group rg-cch-prod \
  --revision <revision-name>
```

**RTO target:** 15 minutes

---

## Scenario: Worker failure

**Symptoms:** Queue depth increasing, outbox lag degraded, publications stuck.

**Immediate actions:**

1. Check worker replica count and CPU/memory.
2. Inspect dead-letter and retry metrics.

**Recovery:**

1. Scale workers.
2. Rollback worker image if regression correlated with deploy.
3. Restart beat if scheduler-related tasks stalled.

```bash
az containerapp update \
  --name ca-cch-worker-prod \
  --resource-group rg-cch-prod \
  --max-replicas 20
```

**RTO target:** 30 minutes

---

## Scenario: Scheduler (beat) failure

**Symptoms:** Scheduled publications not enqueueing, beat container not running.

**Recovery:**

1. Confirm exactly one beat replica (never scale above 1).
2. Restart beat container app.
3. Review missed schedules in `scheduled_publications` table.
4. Manual catch-up via administration API if needed.

**RTO target:** 15 minutes

---

## Scenario: Outbox failure

**Symptoms:** `outbox_dispatch` health degraded/unhealthy, integration events not delivered.

**Immediate actions:**

1. Confirm database reachable (outbox lives in PostgreSQL).
2. Check worker dispatcher logs.

**Recovery:**

1. Restart worker fleet.
2. Scale workers for catch-up.
3. Query backlog:

```sql
SELECT COUNT(*) FROM outbox_events WHERE published_at IS NULL;
```

4. Inspect `dead_letters` for exhausted retries.

**Event replay:** Unpublished rows are automatically claimed by dispatcher (`FOR UPDATE SKIP LOCKED`). No manual replay needed unless dead-lettered.

**RTO target:** 1 hour

---

## Scenario: Provider outage (AI / OIDC)

**Symptoms:** AI generation failures, authentication errors, provider health degraded.

**Recovery:**

1. Confirm provider status page.
2. AI: enable secondary provider or display maintenance message.
3. OIDC: JWKS cache may sustain brief outage; fail closed if verification impossible.

**RTO target:** 4 hours (external dependency)

---

## Scenario: Regional outage

**Symptoms:** Multiple eastus services unavailable, Azure status confirms regional incident.

**Recovery:** Follow `FAILOVER_PLAN.md` § Regional DR failover.

**Checklist:**

- [ ] Incident commander assigned
- [ ] DR PostgreSQL geo-restore initiated
- [ ] DR Redis available
- [ ] Blob GRS secondary or failover complete
- [ ] DR ACA deployed and healthy
- [ ] DNS / Traffic Manager updated
- [ ] Customer communication sent
- [ ] Primary region failback plan documented

**RTO target:** 8 hours

---

## Master recovery checklist

Use after any recovery action:

### Infrastructure

- [ ] PostgreSQL accepting connections
- [ ] Redis responding to PING
- [ ] Blob storage health check passing
- [ ] Key Vault secrets current version loaded

### Application

- [ ] `GET /health/live` → 200
- [ ] `GET /health/ready` → 200
- [ ] Alembic at expected head revision
- [ ] Handler registry loads without errors

### Async processing

- [ ] Worker replicas running
- [ ] Beat replica exactly 1
- [ ] Outbox lag within warning threshold
- [ ] Celery queue depth decreasing

### Security

- [ ] No secrets in logs
- [ ] Rotated credentials if compromise suspected
- [ ] CORS and production invariants enforced

### Observability

- [ ] Error rate normalized (< baseline + 1%)
- [ ] Latency p95 within SLO
- [ ] Alerts cleared or acknowledged

## Automated checklist validation

```bash
pytest tests/disaster_recovery/test_disaster_recovery_checklist.py -m disaster_recovery
```

## Post-incident review template

| Field | Value |
| ----- | ----- |
| Incident ID | |
| Start time (UTC) | |
| Detection time (UTC) | |
| Recovery time (UTC) | |
| RTO achieved | |
| RPO achieved | |
| Root cause | |
| Contributing factors | |
| What went well | |
| Action items | |

## Related documents

- [RESTORE_GUIDE.md](RESTORE_GUIDE.md)
- [FAILOVER_PLAN.md](FAILOVER_PLAN.md)
- [RTO_RPO.md](RTO_RPO.md)
- [BUSINESS_CONTINUITY_PLAN.md](BUSINESS_CONTINUITY_PLAN.md)
