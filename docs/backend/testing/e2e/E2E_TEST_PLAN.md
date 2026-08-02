# End-to-End Test Plan

## Purpose

Validate complete Cloud Content Hub backend business workflows across authentication, assets, content, publishing, scheduling, analytics, notifications, and administration without introducing new production features.

## Scope

| In scope                                                         | Out of scope                    |
| ---------------------------------------------------------------- | ------------------------------- |
| Workflow correctness across handlers, workers, and HTTP delivery | New APIs or repositories        |
| Positive, negative, retry, and recovery paths                    | Performance benchmarking        |
| Security isolation and permission enforcement                    | Penetration testing             |
| Outbox, Celery, PostgreSQL, Redis integration                    | Provider implementation changes |

## Test Layers

```
tests/e2e/          Infrastructure smoke tests and shared fixtures
tests/workflows/    Business workflow validation (15 workflows)
tests/scenarios/    Failure, security, and recovery scenarios
tests/fixtures/     Deterministic seed data and helpers
```

## Infrastructure Requirements

| Service             | Purpose                                             |
| ------------------- | --------------------------------------------------- |
| PostgreSQL 17       | Primary persistence with Alembic migrations         |
| Redis 7             | Celery broker and worker retry state                |
| Azurite (optional)  | Blob storage when overriding TEST in-memory storage |
| Celery (in-process) | Synchronous task execution via `FakeCeleryBroker`   |

## Workflow Coverage

1. Authentication and authorization
2. Poster upload (blob, metadata, outbox)
3. Master article upload and AI generation
4. Video upload
5. Content generation pipeline
6. Schedule publication (outbox + Celery)
   7–12. Platform publish (LinkedIn, Facebook, Instagram, X, Medium, YouTube)
7. Analytics import and dashboard
8. Notification delivery
9. Administration (roles, feature flags, maintenance mode)

## Execution

```bash
cd backend
export CCH_DATABASE_URL=postgresql+asyncpg://cch_test:cch-test-only@localhost:5432/cloud_content_hub_test
export CCH_REDIS_URL=redis://localhost:6379/0
pytest -m e2e
```

Or via Docker Compose:

```bash
docker compose -f docker/docker-compose.test.yml up --abort-on-container-exit test
```

## Success Criteria

- All `@pytest.mark.e2e` tests pass against PostgreSQL and Redis
- Workflow matrix entries marked **Automated**
- Failure and security scenarios documented and validated
- No modifications to production modules except verified defect fixes
