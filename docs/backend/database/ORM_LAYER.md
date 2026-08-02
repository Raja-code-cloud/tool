# ORM Layer

The SQLAlchemy 2.x ORM layer lives under `backend/src/cloud_content_hub/infrastructure/database/`. It maps the approved **86-table** PostgreSQL 17 schema without business logic, API concerns, or repository implementations.

## Layout

```text
infrastructure/database/
├── base.py           # DeclarativeBase root
├── metadata.py       # Shared MetaData + naming convention
├── naming.py         # Deterministic constraint/index name helpers
├── mixins.py         # Reusable column bundles (UAC, tenancy, PK)
├── enums.py          # Central Python StrEnum vocabulary (text + CHECK)
├── constraints.py    # Shared CHECK helpers (check_in, IMMUTABLE_UAC_CHECK)
├── session.py        # Async engine and session factory
└── models/           # One mapped class per file (86 tables)
    └── __init__.py   # Stable import surface for Alembic metadata discovery
```

## Design principles

1. **No PostgreSQL ENUM types** — state is `Text` plus named `CHECK` constraints backed by `DatabaseTextEnum` subclasses in `enums.py`.
2. **Universal Audit Columns (UAC)** on every table via `UACMixin`: `created_at`, `updated_at`, `created_by`, `updated_by`, `deleted_at`, `version`.
3. **Tenancy** — `WorkspaceMixin` / `OrganizationMixin` for scoped tables; composite `(workspace_id, id)` unique constraints on workspace roots; composite FKs on children.
4. **Lazy loading** — relationships default to `lazy="raise"` so services must choose explicit loading strategies.
5. **Persistence only** — no validation beyond DB constraints, no domain rules, no side effects.

## Mixins

| Mixin                 | Purpose                                                        |
| --------------------- | -------------------------------------------------------------- |
| `UUIDPrimaryKeyMixin` | Application-generated UUID `id` primary key                    |
| `TimestampMixin`      | `created_at`, `updated_at` with `now()` server defaults        |
| `AuditActorMixin`     | Nullable `created_by` / `updated_by` → `users.id` (`SET NULL`) |
| `SoftDeleteMixin`     | Nullable `deleted_at` soft-delete marker                       |
| `VersionMixin`        | Optimistic concurrency via SQLAlchemy `version_id_col`         |
| `UACMixin`            | All six universal audit columns                                |
| `WorkspaceMixin`      | Required `workspace_id` FK                                     |
| `OrganizationMixin`   | Required `organization_id` FK                                  |

## Enums

All constrained text states are defined once in `enums.py`. Models reference them for typing and build CHECK constraints with `check_in()` from `constraints.py`. Aliases (`ContentStatus`, `PublishStatus`, `JobStatus`, etc.) point at canonical enums for API-facing naming compatibility.

## Alembic

- Config: `backend/alembic.ini`, env: `backend/migrations/env.py`
- Initial revision: `migrations/versions/bd3726e86063_initial_schema.py`
- Metadata source: `Base.metadata` after importing `cloud_content_hub.infrastructure.database.models`
- Extensions: `citext` created in upgrade

## Out of scope

This layer intentionally excludes FastAPI routers, services, repositories, authentication, Azure Blob, Redis, Celery, AI providers, and schedulers. Those belong in upper Clean Architecture layers.
