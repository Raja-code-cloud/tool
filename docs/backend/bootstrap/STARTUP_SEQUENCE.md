# Bootstrap Startup Sequence

## HTTP process (`bootstrap.api.create_app`)

1. **Load settings** — `load_settings()` parses `CCH_*` environment variables into immutable `Settings`.
2. **Configure logging** — structured logging is initialized from settings.
3. **Build container** — `Container.create(settings)` synchronously constructs all process dependencies (see below).
4. **Wire handlers** — `wire_handlers(container)` populates `app.state.handlers`.
5. **Attach middleware and routes** — CORS, compression, request context, exception handlers, v1 router.
6. **Lifespan startup** — `bootstrap_lifespan` calls `startup_application(container)` before accepting traffic.
7. **Lifespan shutdown** — on exit, `shutdown_application(container)` releases resources.

## `Container.create` (synchronous construction)

```text
load_bootstrap_configuration(settings)
  → identity, observability, storage, AI configs
create_database_engine + create_session_factory
Redis.from_url
create_celery_app
create_observability_bundle
create_event_bundle (outbox + Celery producer)
create_identity_factory + build_registry + IdentityHealthService
create_storage_provider (InMemory for local/test, Azure otherwise)
create_ai_client (mock provider for local/test)
AIGenerationPortAdapter + ObjectStoragePortAdapter
create_repository_factories
create_application_services
admin status port adapters
build_health_checker
return Container
```

## `startup_application` (async verification)

Executed once per process before the FastAPI app serves requests:

1. Verify database connectivity (`SELECT 1`).
2. Ping Redis.
3. Run storage provider health check.
4. Health-check each configured AI provider.
5. Run identity provider health aggregation.
6. Execute registered `HealthChecker` contributors (application, database, Redis, storage, outbox lag).

Startup logs emit structured events with dependency names; secret values are never logged.

## `shutdown_application` (graceful disposal)

Executed in reverse dependency order:

1. Close storage provider HTTP clients.
2. Close AI provider clients (when supported).
3. Close Redis connection.
4. Dispose SQLAlchemy engine / connection pool.

Workers using `bootstrap.worker.create_celery_app` share Redis broker configuration but manage their own process lifecycle outside the HTTP lifespan hook.

## Readiness vs liveness

- **Liveness** — process responds; no external calls required.
- **Readiness** — `Container.health_checker` and `/health/ready` verify database and Redis (delivery layer) plus registered bootstrap health contributors.

Environment-specific defaults:

| Environment             | Storage                                 | AI                          |
| ----------------------- | --------------------------------------- | --------------------------- |
| `local`, `test`         | In-memory provider                      | Mock provider               |
| `staging`, `production` | Azure Blob (from `CCH_AZURE_STORAGE_*`) | Configured provider catalog |

Production storage and AI credentials must be supplied through environment variables or managed identity; bootstrap does not embed secrets.
