# Naming Conventions

SQLAlchemy metadata uses deterministic naming via `NAMING_CONVENTION` in `naming.py` and `metadata.py`. Generated identifiers must stay within PostgreSQL's **63-byte** limit (`POSTGRESQL_IDENTIFIER_LIMIT`).

## Metadata convention map

| Token | Pattern                                                           | Example                                         |
| ----- | ----------------------------------------------------------------- | ----------------------------------------------- |
| `pk`  | `pk_%(table_name)s`                                               | `pk_users`                                      |
| `fk`  | `fk_%(table_name)s__%(column_0_N_name)s__%(referred_table_name)s` | `fk_comments__created_by__users`                |
| `ix`  | `ix_%(table_name)s__%(column_0_N_name)s`                          | `ix_content_assets__workspace_updated_cursor`   |
| `uq`  | `uq_%(table_name)s__%(column_0_N_name)s`                          | `uq_workspaces__organization_slug_where_active` |
| `ck`  | `ck_%(table_name)s__%(constraint_name)s`                          | `ck_users__status`                              |

## Explicit name helpers

`naming.py` provides validated builders for objects outside the convention dict:

- `check_name(table, rule)` → `ck_<table>__<rule>`
- `exclusion_name(table, rule)` → `ex_<table>__<rule>`
- `trigger_name(table, action)` → `trg_<table>__<action>`

## Index naming (INDEX_STRATEGY.md)

Beyond auto-generated names, strategic indexes use descriptive suffixes:

- `_where_active` — partial unique on `deleted_at IS NULL`
- `_cursor` — `(updated_at DESC, id DESC)` pagination
- `_claim` — worker queue dispatch
- `_due` — scheduler / expiry scans
- `_gin` / `brin_*` — access-method-specific indexes

Examples:

```
uq_users__email_where_active
ix_publication_schedules__due
brin_audit_logs__occurred_at
ix_content_assets__search_gin
```

## Python module naming

| DB table                 | Model file                 | Class name            |
| ------------------------ | -------------------------- | --------------------- |
| `content_assets`         | `content_asset.py`         | `ContentAsset`        |
| `ai_generation_requests` | `ai_generation_request.py` | `AIGenerationRequest` |
| `oauth_token_vaults`     | `oauth_token_vault.py`     | `OAuthTokenVault`     |

Singular file names; plural table names via `__tablename__`.

## Enum naming

Python enums use `PascalCase` class names with `SCREAMING_SNAKE` members. Persisted values are lowercase snake strings matching CHECK constraints:

```python
class JobState(DatabaseTextEnum):
    QUEUED = "queued"
    RUNNING = "running"
```

Canonical aliases in `enums.py` avoid duplication (`ContentStatus = ContentLifecycle`).

## Constraint naming in models

Models pass short `name=` to `CheckConstraint` (e.g., `"status"`, `"immutable_uac"`). SQLAlchemy combines with table name via the naming convention to produce `ck_<table>__<name>`.

Shared immutable-row check:

```python
from cloud_content_hub.infrastructure.database.constraints import IMMUTABLE_UAC_CHECK

CheckConstraint(IMMUTABLE_UAC_CHECK, name="ck_<table>__immutable_uac")
```

## Relationship naming

- FK column: `<entity>_id` (e.g., `workspace_id`, `asset_id`, `version_id`)
- ORM relationship: singular noun matching target (`asset`, `workspace`, `content_version`)
- Collections: plural (`versions`, `targets`, `memberships`)

Avoid naming relationships after UAC columns (`version` conflicts with optimistic-lock column).

## Alembic revision naming

Initial migration: `bd3726e86063_initial_schema.py`

Future revisions: `<revision>_<short_description>.py` per `MIGRATION_STRATEGY.md`.
