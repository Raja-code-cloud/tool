# Known Issues

Tracked release blockers, deployment mismatches, and accepted limitations for Cloud Content Hub backend GA.

Update this document during RC validation and before each production release.

## Release blockers

None.

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
| HEALTH-001 | Probe path mismatch between application and deployment infrastructure | Application route aliases and infra alignment | 2026-08-02 |

### HEALTH-001 (resolved): Probe path mismatch

**Resolution:** The application now exposes canonical routes `GET /health/live` and
`GET /health/ready`. Legacy aliases `GET /live` and `GET /ready` remain available with
identical responses (excluded from OpenAPI). Deployment infrastructure (ACA Bicep,
Docker Compose, Dockerfile HEALTHCHECK, `verify-health.sh`, CI smoke) targets the
canonical paths.

**Verification:** `pytest tests/deployment/test_probe_alignment.py -m deployment -v`

---

## Reporting new issues

1. Add entry with unique ID (`AREA-NNN`)
2. Set status: Open, Mitigated, or Resolved
3. Link verification test if applicable
4. Update `RC_CHECKLIST.md` if release-blocking
