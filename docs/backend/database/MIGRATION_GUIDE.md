# Migration Guide

Alembic manages schema evolution for the Cloud Content Hub PostgreSQL 17 database. The ORM layer is the single source of truth for table definitions; migrations are generated from `Base.metadata`.

## Prerequisites

- Python 3.13+ with `cloud-content-hub` installed (`pip install -e ".[dev]"` from `backend/`)
- PostgreSQL 17 with `citext` extension available
- Database URL configured in application settings (`CCH_DATABASE_URL` or equivalent in `core/config.py`)

## Project layout

```text
backend/
├── alembic.ini
└── migrations/
    ├── env.py              # Async Alembic env; target_metadata = Base.metadata
    ├── script.py.mako
    └── versions/
        └── bd3726e86063_initial_schema.py   # Initial 86-table baseline
```

## Initial migration

Revision `bd3726e86063` creates:

- PostgreSQL extension `citext`
- All **86** tables with primary keys, foreign keys, check constraints, and indexes
- Partial unique indexes (`postgresql_where=...`) for soft-delete-aware business keys
- GIN index on `content_assets.search_document`
- BRIN indexes on high-volume time columns (`audit_logs`, `usage_events`, `metric_observations`, `outbox_events`)

### Apply

```bash
cd backend
alembic upgrade head
```

Docker profile (when compose is available):

```bash
docker compose --profile tools run --rm migrate
```

## Generating new revisions

After ORM model changes:

```bash
cd backend
alembic revision --autogenerate -m "describe_change"
```

Review the generated script carefully:

1. **No accidental drops** — autogenerate may propose dropping unrecognized objects
2. **Concurrent indexes** — production index additions should use `CREATE INDEX CONCURRENTLY` per `MIGRATION_STRATEGY.md` (may require manual SQL)
3. **Zero-downtime** — expand/contract pattern for column renames and type changes
4. **Partial indexes** — verify `postgresql_where` clauses match `INDEX_STRATEGY.md`

## Metadata registration

Alembic discovers tables only when model modules are imported. Ensure new models are added to `models/__init__.py`:

```python
from cloud_content_hub.infrastructure.database.models.new_model import NewModel
```

Then verify table count:

```python
from cloud_content_hub.infrastructure.database.base import Base
import cloud_content_hub.infrastructure.database.models as _models

assert len(Base.metadata.tables) == 86  # update count after additions
```

## Upgrade / downgrade requirements

Every revision must provide:

- **`upgrade()`** — idempotent where possible; extensions via `IF NOT EXISTS`
- **`downgrade()`** — reverse DDL in dependency-safe order (drop FKs before tables)

The initial revision's `downgrade()` drops all tables in reverse dependency order.

## Offline generation

When no database is reachable, metadata can be rendered offline (as used for the initial revision). Prefer live autogenerate against an empty database for subsequent changes to capture dialect-specific diffs accurately.

## Validation checklist

Before merging migration PRs:

- [ ] `alembic upgrade head` on empty database succeeds
- [ ] `alembic downgrade -1` succeeds (when safe in dev)
- [ ] Table count matches approved schema (86)
- [ ] Constraint names match `NAMING_CONVENTIONS.md`
- [ ] No manual SQL unless required (concurrent indexes, RLS policies, triggers)
- [ ] Migration tests pass (`tests/migration/` when present)

## Related documents

- `MIGRATION_STRATEGY.md` (repo root) — zero-downtime production process
- `INDEX_STRATEGY.md` — index inventory and partial-index rules
- `SOFT_DELETE_STRATEGY.md` — deletion classification per table
- `TABLE_SPECIFICATIONS.md` — authoritative column-level spec
