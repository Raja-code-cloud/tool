# Operational Runbooks

Step-by-step procedures for Cloud Content Hub AI backend incidents. For infrastructure
actions (scaling, rollback), also see `docs/backend/devops/RUNBOOK.md`.

---

## API unavailable

**Symptoms:** `CchApiUnavailable`, readiness 503, users cannot access API.

**Impact:** All user-facing functionality down.

### Diagnosis

1. Check ACA revision status: `az containerapp revision list --name ca-cch-api-<env> -g rg-cch-<env>`
2. Verify health probes: `./backend/operations/scripts/validate_health.sh https://<api-fqdn>`
3. Check recent deploy correlation in CI/CD logs.
4. Inspect Log Analytics for `service=cloud-content-hub`, filter by `level=error`.

### Resolution

1. If deploy-related: roll back revision (see [Deployment rollback](#deployment-rollback)).
2. If dependency-related: follow database or Redis runbooks below.
3. Scale API replicas if traffic spike: see OPERATIONS_GUIDE.md.
4. Confirm recovery: availability SLI returns to target, alerts resolve.

---

## High latency

**Symptoms:** `CchApiHighLatency`, elevated p95 in API dashboard.

### Diagnosis

1. Check `cch:api_latency:p95_5m` and in-flight requests.
2. Inspect database operation duration and pool utilization.
3. Check AI provider latency if content generation endpoints affected.
4. Review recent deploy or config change.

### Resolution

1. Scale API replicas if CPU-saturated.
2. Investigate slow queries via database logs.
3. If AI-bound: check provider status, enable circuit breaker if available.
4. Roll back if regression from latest deploy.

---

## Database unavailable

**Symptoms:** Readiness 503, `CchDatabaseErrors`, `/health/ready` database check fails.

### Diagnosis

1. Verify Azure PostgreSQL status in Azure Portal.
2. Test connectivity from ACA console or migration job.
3. Check connection pool exhaustion alert.

### Resolution

1. Fail over to replica if primary unavailable (Azure managed failover).
2. Reduce API/worker replicas temporarily to lower connection pressure.
3. Verify Key Vault secret `CCH-DATABASE-URL` is valid.
4. Redeploy containers after secret rotation.

---

## Redis unavailable

**Symptoms:** Readiness 503, `CchCacheErrors`, Celery workers idle.

### Diagnosis

1. Verify Azure Cache for Redis status.
2. Test `PING` from API readiness path.
3. Check memory usage and eviction metrics in Azure.

### Resolution

1. Restart Redis if transient (Azure portal).
2. Scale Redis vertically if memory pressure.
3. Verify Key Vault secret `CCH-REDIS-URL`.
4. Restart worker fleet after Redis recovery to clear stale connections.

---

## Blob storage failure

**Symptoms:** `CchStorageFailures`, upload/download errors, storage health degraded.

### Diagnosis

1. Check Azure Storage account health and throttling metrics.
2. Review `cloud_content_hub_blob_operations_total{outcome="error"}`.
3. Verify managed identity has Storage Blob Data Contributor role.

### Resolution

1. If throttled: request quota increase or reduce concurrent uploads.
2. If auth failure: verify managed identity and RBAC assignments.
3. Fail over to GRS secondary if regional outage (see storage ops guide).
4. Storage is degraded (not blocking) for readiness — API stays up but uploads fail.

---

## Worker crash

**Symptoms:** `CchWorkerHighFailureRate`, queue depth growing, tasks not processing.

### Diagnosis

1. Check worker ACA replica count and restart count.
2. Inspect worker logs for task exceptions.
3. Check Redis broker connectivity.
4. Review DLQ keys: `cloud_content_hub:dlq:*`.

### Resolution

1. Scale worker max replicas.
2. Restart worker revision if crash loop.
3. Inspect and replay DLQ messages after root cause fix.
4. Verify `CELERY_CONCURRENCY` appropriate for workload.

---

## Scheduler failure

**Symptoms:** `CchSchedulerLag`, scheduled publishes not firing, beat container down.

### Diagnosis

1. Verify beat container has exactly 1 replica running.
2. Check `/tmp/celerybeat-schedule` exists (liveness probe).
3. Inspect beat logs for broker connection errors.

### Resolution

1. Restart beat container app.
2. Verify Redis broker available.
3. Check scheduler job metrics for stuck jobs.
4. Manually trigger overdue publishes via admin API if needed (ops approval).

---

## Outbox backlog

**Symptoms:** `CchOutboxBacklog`, publishing lag, outbox health degraded.

### Diagnosis

1. Check `cch:outbox_retries:rate5m` and maintenance queue depth.
2. Verify outbox dispatch worker processing `cloud_content_hub.deliver_outbox_event`.
3. Review outbox table for pending rows (admin query).
4. Default lag warning threshold: 60 seconds (`dispatch_lag_warning_seconds`).

### Resolution

1. Scale workers; prioritize maintenance queue.
2. Verify `cleanup_outbox` task running on schedule.
3. Investigate poison messages exceeding `max_attempts=10`.
4. After recovery, monitor until backlog drains below SLO.

---

## Provider outage

**Symptoms:** `CchAiProviderFailures`, `CchSocialProviderFailures`, `CchAuthFailureSpike`.

### Diagnosis

1. Check provider status pages (OpenAI, Anthropic, Google, social platforms, IdP).
2. Review error rates by provider label in metrics.
3. Distinguish auth spike (possible attack) from provider outage.

### Resolution

1. Enable fallback provider if configured.
2. Pause non-critical AI/social jobs if needed.
3. Communicate user-facing degradation.
4. Resume when provider recovers; monitor retry metrics.

---

## Deployment rollback

**Symptoms:** Errors correlate with latest ACA revision; smoke tests fail.

### Procedure

1. Identify last healthy revision:
   ```bash
   az containerapp revision list --name ca-cch-api-<env> -g rg-cch-<env> -o table
   ```
2. Activate previous revision:
   ```bash
   az containerapp revision activate --name ca-cch-api-<env> -g rg-cch-<env> \
     --revision <previous-revision-name>
   ```
3. Repeat for worker and beat if affected.
4. Run `./deployment/scripts/verify-health.sh <env>` (align probe paths first).
5. Database migrations are forward-only — do not roll back schema.

See `docs/backend/devops/ROLLBACK.md` for full procedure.

---

## Related

- `INCIDENT_RESPONSE.md` — incident lifecycle
- `OPERATIONS_GUIDE.md` — day-to-day operations
- `docs/backend/devops/RUNBOOK.md` — infrastructure runbook
