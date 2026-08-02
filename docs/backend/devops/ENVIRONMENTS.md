# Environments

Cloud Content Hub recognizes deployment classes through `CCH_ENVIRONMENT` and infrastructure-specific overlays.

## Mapping

| Platform environment | `CCH_ENVIRONMENT` value | Notes                               |
| -------------------- | ----------------------- | ----------------------------------- |
| local                | `local`                 | Docker Compose, `.env` allowed      |
| test / CI            | `test`                  | Compose test stack, disposable data |
| dev                  | `staging`*              | ACA dev subscription                |
| qa                   | `staging`*              | ACA qa subscription                 |
| prod                 | `production`            | No `.env`, OpenAPI disabled         |
| dr                   | `production`            | DR region, production invariants    |

\*Azure `dev` and `qa` platform environments map to application `staging` until dedicated enum values are introduced in `core/config.py`.

## Configuration precedence

1. Explicit bootstrap overrides (tests/CLI)
2. Process environment / ACA secret refs
3. Local `.env` (`local` and `test` only)
4. Safe code defaults

Production and DR never load `.env` files.

## Typed variables

All infrastructure configuration uses the `CCH_` prefix. See `backend/.env.example` and `docs/backend/CONFIGURATION_GUIDE.md`.

Common deployment variables:

```text
CCH_ENVIRONMENT
CCH_SERVICE_NAME
CCH_SERVICE_VERSION
CCH_LOG_LEVEL
CCH_DATABASE_URL
CCH_REDIS_URL
CCH_HTTP_ALLOWED_ORIGINS
CCH_OPENAPI_ENABLED
CCH_AZURE_STORAGE_ACCOUNT_URL
```

## Secrets by role

| Role           | Secret source                | Used by           |
| -------------- | ---------------------------- | ----------------- |
| API runtime    | `CCH-DATABASE-URL`           | API container     |
| Worker runtime | `CCH-DATABASE-URL`           | Worker container  |
| Migration      | `CCH-MIGRATION-DATABASE-URL` | Migration job     |
| Redis          | `CCH-REDIS-URL`              | API, worker, beat |

Separate database credentials enforce least privilege per `MIGRATION_STRATEGY.md`.

## Local overrides

Copy `docker/.env.example` to `docker/.env` for Compose-specific values (ports, postgres password). Application settings still use `CCH_*` names inside containers.

## Production invariants

Enforced by `Settings.validate_production()`:

- Database URL must use `postgresql+asyncpg://`
- `CCH_HTTP_ALLOWED_ORIGINS` cannot include `*`

Additional deployment policy:

- `CCH_OPENAPI_ENABLED=false`
- Managed identity for Azure Blob
- Exact HTTPS CORS origins

## Feature rollout

Temporary behavior changes use feature flags in the database settings model, not environment variables. Infrastructure settings remain deployment configuration.

## Validation

CI validates `.env.example` key naming. Extend with a typed settings contract test as the settings model grows.
