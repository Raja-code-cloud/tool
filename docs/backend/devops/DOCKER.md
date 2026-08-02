# Docker

Production images live under `docker/` and use multi-stage builds on `python:3.13-slim-bookworm`.

## Images

| File                       | Target    | Output                           |
| -------------------------- | --------- | -------------------------------- |
| `docker/Dockerfile`        | `runtime` | FastAPI API + Alembic migrations |
| `docker/Dockerfile`        | `dev`     | Editable install with reload     |
| `docker/Dockerfile`        | `test`    | pytest + dev tooling             |
| `docker/Dockerfile.worker` | `runtime` | Celery worker                    |
| `docker/Dockerfile.worker` | `dev`     | Editable worker for local dev    |

## Security properties

- Non-root user `cch` (UID/GID `10001`)
- Minimal runtime layer (wheel install only)
- Read-only root filesystem in Compose production profile
- `cap_drop: [ALL]` in production compose overlay
- Health check on API liveness endpoint

## Build commands

```bash
docker build -f docker/Dockerfile --target runtime -t cloud-content-hub-api:local .
docker build -f docker/Dockerfile.worker --target runtime -t cloud-content-hub-worker:local .
```

Build context is the repository root. `.dockerignore` excludes frontend artifacts and local caches.

## Compose files

| File                      | Use                                               |
| ------------------------- | ------------------------------------------------- |
| `docker-compose.yml`      | Base local stack: API, worker, postgres, redis    |
| `docker-compose.dev.yml`  | Hot reload overrides                              |
| `docker-compose.test.yml` | CI/integration test stack with Azurite            |
| `docker-compose.prod.yml` | Immutable digest-based production-like validation |

## Service commands

**API (default)**

```text
uvicorn cloud_content_hub.main:app --host 0.0.0.0 --port 8000
```

**Worker (default)**

```text
celery --app cloud_content_hub.workers.runtime:celery_app worker
```

**Beat**

```text
celery --app cloud_content_hub.workers.runtime:celery_app beat --schedule /tmp/celerybeat-schedule
```

**Migration**

```text
alembic upgrade head
```

## Health checks

Container health checks and Azure probes target implemented routes:

- Liveness: `GET /health/live`
- Readiness: `GET /health/ready` (checks PostgreSQL and Redis)

## Local profiles

```bash
# API + worker + postgres + redis
docker compose -f docker/docker-compose.yml up --build

# Include Celery beat
docker compose -f docker/docker-compose.yml --profile scheduler up --build

# Run migrations
docker compose -f docker/docker-compose.yml --profile tools run --rm migrate

# Run tests
docker compose -f docker/docker-compose.test.yml up --build --abort-on-container-exit
```

## Image labels

Images include OCI labels for revision and build date (`VCS_REF`, `BUILD_DATE` build args) to support traceability and SBOM correlation.
