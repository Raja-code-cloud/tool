# Known Limitations

## External Social APIs

Platform publish workflows validate publication creation and dispatch job orchestration. External LinkedIn/Facebook/Instagram/X/Medium/YouTube API calls are not executed in E2E tests; provider integration is stubbed at the worker audit layer.

## Auth HTTP Routes

Authentication HTTP routes (`/api/v1/auth/*`) are not wired in the delivery layer. Login and OAuth flows are validated through the identity provider layer and JWT middleware instead of full HTTP auth endpoints.

## Unwired Handlers

The following API routes reference handlers not registered in `bootstrap/handlers.py` and are excluded from HTTP E2E coverage:

- `GET /api/v1/publish/history`
- `GET /api/v1/schedule`
- `PATCH /api/v1/schedule/{id}`

## Storage in TEST Environment

`Environment.TEST` uses `InMemoryStorageProvider` by default. Azurite from `docker-compose.test.yml` is available but requires explicit bootstrap configuration overrides to replace in-memory storage.

## Testcontainers

The suite uses environment-configured PostgreSQL and Redis (including Docker Compose) rather than embedded Testcontainers Python modules, to align with existing integration test conventions.

## Celery Worker Process

E2E tests execute Celery tasks synchronously via `FakeCeleryBroker` and `TaskDispatcher` rather than requiring a separate worker container.

## Test Isolation

All E2E tests share one migrated PostgreSQL database per session. Tests use unique idempotency keys and seeded suffixes to minimize cross-test interference. Soft-delete tests create disposable assets.
