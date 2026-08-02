# Known Issues

Tracked release blockers, deployment mismatches, and accepted limitations for Cloud Content Hub backend GA.

Update this document during RC validation and before each production release.

## Release blockers

### HEALTH-001: Probe path mismatch between application and deployment infrastructure

**Status:** Open — blocks ACA/Docker health verification until resolved

**Description:** The FastAPI application registers liveness and readiness at `/live` and `/ready` (see `backend/src/cloud_content_hub/api/routers/v1/health.py`). Deployment infrastructure references `/health/live` and `/health/ready` in:

- `infra/container-apps/bicep/main.bicep` (ACA probes)
- `docker/docker-compose.yml` (API healthcheck)
- `docker/Dockerfile` (HEALTHCHECK instruction)
- `deployment/scripts/verify-health.sh`
- `.github/workflows/backend-ci.yml` (Docker build smoke)

**Impact:** Container health checks and ACA readiness probes return 404. Deployments may fail or mark healthy containers unhealthy depending on probe configuration.

**Workaround:** None for automated deploy pipelines without path alignment.

**Resolution options (application or infrastructure team):**

1. Add route aliases `/health/live` and `/health/ready` in the health router, or
2. Update all deployment references to `/live` and `/ready`

**Verification:** `pytest tests/deployment/test_probe_alignment.py -m deployment -v`

---

## Accepted limitations (GA)

### ENV-001: Azure dev/qa map to application `staging`

Platform environments `dev` and `qa` set `CCH_ENVIRONMENT=staging` until dedicated enum values are added. See `docs/backend/devops/ENVIRONMENTS.md`.

### AI-001: Mock AI provider in non-local bootstrap

Non-local environments currently configure mock AI provider in bootstrap configuration. Production deployments must override with real provider credentials and verify provider health before GA traffic.

### MIG-001: Forward-only database migrations

Automated schema downgrade is not supported. Rollback requires application revision activation without schema reversal, or PITR for data incidents. See `ROLLBACK_GUIDE.md`.

---

## Resolved issues

| ID | Summary | Resolved in | Date |
| -- | ------- | ----------- | ---- |
| —  | —       | —           | —    |

---

## Reporting new issues

1. Add entry with unique ID (`AREA-NNN`)
2. Set status: Open, Mitigated, or Resolved
3. Link verification test if applicable
4. Update `RC_CHECKLIST.md` if release-blocking
