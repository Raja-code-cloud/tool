# Test Execution Guide

## Prerequisites

- Python 3.13
- PostgreSQL 17 with database `cloud_content_hub_test`
- Redis 7
- Backend dependencies installed (`pip install -e ".[dev]"`)

## Local Execution

### 1. Start infrastructure

```bash
docker compose -f docker/docker-compose.test.yml up -d postgres-test redis-test
```

### 2. Configure environment

```bash
export CCH_ENVIRONMENT=test
export CCH_DATABASE_URL=postgresql+asyncpg://cch_test:cch-test-only@localhost:5432/cloud_content_hub_test
export CCH_REDIS_URL=redis://localhost:6379/0
```

### 3. Run migrations

```bash
cd backend
alembic upgrade head
```

### 4. Execute tests

```bash
# Full E2E suite
pytest -m e2e -v

# Workflow tests only
pytest tests/workflows -m e2e -v

# Failure and security scenarios
pytest tests/scenarios -m e2e -v

# Infrastructure smoke tests
pytest tests/e2e -m e2e -v
```

## Docker Compose (CI parity)

```bash
docker compose -f docker/docker-compose.test.yml up --abort-on-container-exit test
```

Reports are written to `backend/test-results/`.

## Static Analysis

```bash
cd backend
ruff check tests
mypy tests
```

## Markers

| Marker | Description |
| --- | --- |
| `e2e` | End-to-end workflow validation (requires PostgreSQL + Redis) |
| `integration` | Inherited by E2E fixtures |

## Troubleshooting

| Symptom | Resolution |
| --- | --- |
| Tests skipped for missing `DATABASE_URL` | Export `CCH_DATABASE_URL` |
| Alembic migration failure | Ensure PostgreSQL is healthy and credentials match compose file |
| Redis connection errors | Start `redis-test` service or set `CCH_REDIS_URL` |
| Unique constraint violations | Drop and recreate test database, rerun migrations |

## Determinism Notes

- E2E container uses `FixedClock` and `FixedUuidGenerator` where injected
- Outbox draining is synchronous; no sleep-based polling required
- Mock AI and in-memory storage are selected automatically for `Environment.TEST`
