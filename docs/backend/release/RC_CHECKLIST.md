# Release Candidate Checklist

Use this checklist before promoting a backend build from QA to Release Candidate (RC) and again before General Availability (GA).

## Build identity

- [ ] Image tag equals promoted Git SHA (immutable digest recorded)
- [ ] SBOM artifact uploaded for the build
- [ ] Security scan passed (pip-audit, gitleaks, Trivy CRITICAL/HIGH gate)
- [ ] Cosign signature present for release tags (when enabled)

## Static validation (CI)

- [ ] Ruff lint and format clean
- [ ] mypy strict clean on `src` and `tests`
- [ ] Unit tests pass (`pytest tests/unit`)
- [ ] Integration and contract tests pass (Compose test stack)
- [ ] Release validation suite passes (`pytest tests/release -m release`)
- [ ] Deployment verification suite passes (`pytest tests/deployment -m deployment`)
- [ ] Smoke suite passes locally (`pytest tests/smoke -m "smoke and not external"`)

## Application startup

- [ ] `create_app()` loads without import errors
- [ ] `load_settings()` and `load_bootstrap_configuration()` succeed for target environment
- [ ] Production invariants enforced (`CCH_DATABASE_URL` asyncpg, no wildcard CORS)
- [ ] Mock identity provider disabled for production (`IdentitySettings` validation)
- [ ] Handler registry wires without duplicate keys
- [ ] Health checker registers expected contributors (database, redis, storage, identity, AI)

## Health probes (blocking)

Verify implemented routes respond before ACA traffic cutover:

| Probe     | Canonical route     | Expected                                |
| --------- | ------------------- | --------------------------------------- |
| Liveness  | `GET /health/live`  | 200                                     |
| Readiness | `GET /health/ready` | 200 when PostgreSQL and Redis reachable |
| Summary   | `GET /health`       | 200                                     |

Legacy aliases `GET /live` and `GET /ready` remain available and return identical responses.

- [ ] Liveness returns 200 without dependency checks
- [ ] Readiness returns 200 with database and redis checks ok
- [ ] Readiness returns 503 when a required dependency is unavailable
- [ ] ACA Bicep, Docker HEALTHCHECK, and `verify-health.sh` target `/health/live` and `/health/ready`

## Database migrations

- [ ] Alembic head revision identified and recorded
- [ ] Migration job (`caj-cch-migrate-<env>`) succeeded before API scale-up
- [ ] Schema table count matches baseline (86 tables at initial GA)
- [ ] No pending autogenerate drift (`alembic check` or revision review)
- [ ] Rollback strategy documented if migration is not reversible

## Container startup

- [ ] API container starts on port 8000 with non-root user
- [ ] Worker and beat containers start with Celery entrypoint
- [ ] Read-only root filesystem and tmpfs configured
- [ ] Graceful shutdown completes within stop grace period (API lifespan, worker `stop_grace_period`)

## Dependency connectivity

- [ ] PostgreSQL reachable from API and worker roles
- [ ] Redis reachable (broker and cache)
- [ ] Azure Blob Storage reachable (managed identity or connection string per environment)
- [ ] Identity provider endpoints reachable (Entra, Google, or configured OIDC)
- [ ] AI provider credentials configured (non-mock in staging/production)

## Secrets and configuration

- [ ] Key Vault secrets resolve: `CCH-DATABASE-URL`, `CCH-MIGRATION-DATABASE-URL`, `CCH-REDIS-URL`
- [ ] Separate migration database role enforced
- [ ] `CCH_OPENAPI_ENABLED=false` in production and DR
- [ ] `CCH_HTTP_ALLOWED_ORIGINS` lists exact HTTPS origins (no `*`)
- [ ] `CCH_SERVICE_VERSION` matches deployed image tag

## Observability

- [ ] Structured JSON logs emitted to stdout
- [ ] `/metrics` endpoint reachable (when exposed internally)
- [ ] Trace context propagated (`X-Correlation-ID`, OpenTelemetry when configured)
- [ ] Alert rules configured per `docs/backend/observability/ALERTING.md`

## Smoke validation

Run against QA or RC environment after deploy:

```bash
export SMOKE_BASE_URL=https://<api-fqdn>
pytest tests/smoke -m "smoke and external" -v
```

- [ ] Authentication (protected routes reject anonymous callers)
- [ ] Asset upload/list
- [ ] Content generation endpoint accepts authenticated requests
- [ ] Publishing history/list
- [ ] Scheduler list/create
- [ ] Analytics dashboard
- [ ] Notifications list
- [ ] Administration system status

## Rollback readiness

- [ ] Prior healthy ACA revision identified
- [ ] `deployment/scripts/rollback.sh` tested in QA
- [ ] Database rollback strategy documented (forward-only default)
- [ ] Incident runbook linked (`docs/backend/devops/RUNBOOK.md`)

## Sign-off

| Role             | Name | Date | RC / GA |
| ---------------- | ---- | ---- | ------- |
| Backend engineer |      |      |         |
| DevOps           |      |      |         |
| Security         |      |      |         |
| Release manager  |      |      |         |
