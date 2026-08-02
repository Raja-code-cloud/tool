# Go-Live Checklist

Final verification before enabling production traffic for Cloud Content Hub backend GA.

Complete every item in `RC_CHECKLIST.md` first. This checklist adds production-specific gates.

## Pre-cutover (T-24h)

- [ ] Change window approved and communicated
- [ ] On-call rotation confirmed
- [ ] Rollback revision and image digest recorded
- [ ] Database PITR backup verified within SLA
- [ ] DR environment validated (optional parallel smoke)

## Deployment sequence

Execute in order; do not skip migration before API traffic increase.

1. [ ] Build and push images to production ACR with Git SHA tag
2. [ ] Deploy Bicep or update ACA revisions with new image tag
3. [ ] Run migration job: `deployment/scripts/migrate.sh prod`
4. [ ] Confirm migration job exit code 0 in ACA job logs
5. [ ] Update worker and beat to new image tag
6. [ ] Update API revision; keep prior revision active during verification
7. [ ] Run health verification: `deployment/scripts/verify-health.sh prod`

## Production health gates

- [ ] `GET /live` returns 200 on production FQDN
- [ ] `GET /ready` returns 200 with database and redis checks ok
- [ ] No elevated 5xx rate in first 15 minutes
- [ ] Celery worker replicas healthy; queue depth stable
- [ ] Beat single replica running

## Production configuration

- [ ] `CCH_ENVIRONMENT=production`
- [ ] `CCH_OPENAPI_ENABLED=false` (no public `/docs` or `/openapi.json`)
- [ ] Mock identity provider disabled
- [ ] Managed identity for Blob Storage (no connection string in prod)
- [ ] CORS origins match production frontend URLs only

## External smoke (production)

```bash
export SMOKE_BASE_URL=https://<prod-api-fqdn>
pytest tests/smoke -m "smoke and external" -v --tb=short
```

Use a service account or test workspace with non-production data where possible.

- [ ] Authenticated API flows succeed
- [ ] No secrets or PII in error responses
- [ ] Rate limiting behaves as expected under nominal load

## Traffic cutover

- [ ] Shift 100% traffic to new revision (or activate revision in ACA)
- [ ] Monitor error rate, latency p95, queue lag for 30 minutes
- [ ] Deactivate failed revision after stability confirmed

## Post-go-live (T+1h)

- [ ] Log Analytics queries return expected structured fields
- [ ] Prometheus/metrics scraping healthy (if configured)
- [ ] Alerting channels tested (non-paging verification)
- [ ] Update release notes and `KNOWN_ISSUES.md` if new issues discovered
- [ ] Archive deployment record: image tag, revision names, migration revision, sign-offs

## Emergency rollback trigger

Initiate rollback immediately if any of the following persist after deploy:

- Readiness probe failures (`/ready` 503)
- Migration job failure on production
- Sustained 5xx above error budget
- Data integrity incident correlated with release

Follow `ROLLBACK_GUIDE.md`.

## Sign-off

| Role             | Name | Date | Approved |
| ---------------- | ---- | ---- | -------- |
| Release manager  |      |      |          |
| Engineering lead |      |      |          |
| Operations       |      |      |          |
