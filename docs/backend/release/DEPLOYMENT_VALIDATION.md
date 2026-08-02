# Deployment Validation

Procedures and automated checks for validating Cloud Content Hub backend deployments across local Docker Compose and Azure Container Apps.

## Automated suite

Run the deployment verification tests:

```bash
cd backend
pytest tests/deployment -m deployment -v
```

For integration with infrastructure (requires Azure CLI and optional live environment):

```bash
pytest tests/deployment -m "deployment and external" -v
```

## Validation areas

### Application startup

| Check | Method |
| ----- | ------ |
| App factory imports | `create_app()` in release tests |
| Settings validation | Production invariant tests |
| DI container wiring | Handler registry uniqueness |
| Lifespan hooks registered | FastAPI lifespan on `create_app()` |

### Configuration validation

| Variable | Production rule |
| -------- | --------------- |
| `CCH_ENVIRONMENT` | `production` for prod/DR |
| `CCH_DATABASE_URL` | `postgresql+asyncpg://` prefix |
| `CCH_HTTP_ALLOWED_ORIGINS` | No wildcard `*` |
| `CCH_OPENAPI_ENABLED` | `false` in prod |
| Mock identity | Disabled in production |

Validate template keys:

```bash
cd backend
python -c "from pathlib import Path; ..."  # see backend-ci.yml env template check
```

### Database migrations

| Step | Command |
| ---- | ------- |
| Apply migrations | `alembic upgrade head` |
| Docker profile | `docker compose --profile tools run --rm migrate` |
| ACA job | `deployment/scripts/migrate.sh <env>` |

Verify:

- Head revision exists under `backend/migrations/versions/`
- `target_metadata` matches ORM `Base.metadata`
- Migration job completes before API traffic increase

### Container startup

| Image | Dockerfile | Health probe |
| ----- | ---------- | ------------ |
| API | `docker/Dockerfile` (runtime target) | See probe alignment below |
| Worker | `docker/Dockerfile.worker` | Process health via worker runtime |
| Test | `docker/Dockerfile` (test target) | pytest entrypoint |

Local full stack:

```bash
cp docker/.env.example docker/.env
docker compose -f docker/docker-compose.yml -f docker/docker-compose.dev.yml up --build -d
docker compose --profile tools run --rm migrate
```

### Health endpoints

Application implements:

| Endpoint | Purpose |
| -------- | ------- |
| `GET /health` | Service summary (version, healthy) |
| `GET /health/live` | Liveness — process alive (canonical) |
| `GET /health/ready` | Readiness — PostgreSQL + Redis (canonical) |

Legacy aliases `GET /live` and `GET /ready` remain available with identical responses
(excluded from OpenAPI).

Expected responses use the API success envelope (`success: true`, `data.status`).

Deployment infrastructure (Bicep, Docker Compose healthcheck, Dockerfile HEALTHCHECK,
`verify-health.sh`, CI docker smoke) targets the canonical `/health/live` and
`/health/ready` paths.

### Azure Container Apps deployment

Deploy flow:

```bash
export ACR_LOGIN_SERVER=acrcchdev.azurecr.io
deployment/scripts/build-images.sh dev <git-sha>
deployment/scripts/deploy.sh dev <git-sha>
deployment/scripts/verify-health.sh dev
```

Verify:

- [ ] API ingress FQDN resolves
- [ ] User-assigned managed identity has AcrPull and Key Vault GET
- [ ] Secrets bound: database URL, redis URL
- [ ] Min/max replicas match parameter file
- [ ] Migration job `caj-cch-migrate-<env>` succeeded

### Connectivity checks

| Dependency | Readiness signal | Bootstrap startup |
| ---------- | ---------------- | ----------------- |
| PostgreSQL | `/health/ready` database check | `SELECT 1` on startup |
| Redis | `/health/ready` redis check | `PING` on startup |
| Blob storage | Health checker contributor | `storage_provider.health_check()` |
| Identity | Identity health service | Provider probe on startup |
| AI | Health checker contributor | Provider probe on startup |

### Secrets configuration

Key Vault secrets (per environment):

- `CCH-DATABASE-URL` — API/worker runtime
- `CCH-MIGRATION-DATABASE-URL` — migration job only
- `CCH-REDIS-URL` — API, worker, beat

Never commit secrets. CI validates `.env.example` uses `CCH_*` prefix only.

### Container image versioning

- Tag images with Git SHA: `<acr>/cloud-content-hub-api:<sha>`
- Environment alias: `<env>-latest` for convenience
- Production compose requires digests (`docker-compose.prod.yml`)
- Record SBOM per build

## Post-deploy verification script

```bash
deployment/scripts/verify-health.sh <env>
```

Manual extended checks:

```bash
export SMOKE_BASE_URL=https://<fqdn>
pytest tests/smoke -m "smoke and external" -v
```

## CI integration

`backend-ci.yml` stages:

1. Lint and type check
2. Unit tests
3. Integration tests (Compose)
4. Docker build smoke

Add release and deployment suites to promotion pipeline before RC:

```bash
pytest tests/release -m release -q
pytest tests/deployment -m deployment -q
pytest tests/smoke -m "smoke and not external" -q
```

## Related documents

- `docs/backend/devops/DEPLOYMENT_GUIDE.md`
- `docs/backend/devops/AZURE_CONTAINER_APPS.md`
- `docs/backend/devops/CI_CD.md`
- `RC_CHECKLIST.md`
- `ROLLBACK_GUIDE.md`
