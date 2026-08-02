# Repository Pattern

## Purpose

The repository layer isolates persistence from application and domain policy. Application services depend on repository ports; SQLAlchemy implementations live in infrastructure and never commit transactions directly.

## Layout

```text
src/cloud_content_hub/
├── domain/repositories/interfaces/base.py
└── infrastructure/repositories/sqlalchemy/
    ├── base.py
    ├── unit_of_work.py
    ├── transaction.py
    ├── specification.py
    ├── pagination.py
    ├── filters.py
    ├── sorting.py
    ├── exceptions.py
    └── utils.py
```

## Port contract

`IRepository` defines the persistence surface consumed by application services:

- `get_by_id`, `get_all`, `find`, `exists`, `count`
- `create`, `update`, `delete`
- `soft_delete`, `restore`
- `bulk_create`, `bulk_update`, `bulk_delete`
- `find_paginated`, `find_offset`

Repositories translate database outcomes into repository exceptions. Delivery and application layers map those to stable application errors.

## Generic implementation

`SqlAlchemyRepository` is parameterized by a mapped model type and supports:

- async SQLAlchemy 2.x sessions
- active-row filtering via `deleted_at IS NULL`
- explicit workspace scoping for tenant-owned aggregates
- optimistic concurrency via the mapped `version` column
- composable specifications, filters, sorting, and pagination

Entity-specific repositories should subclass or compose the generic repository and declare allowed search, sort, and filter columns.

## Rules

- Repositories never call `commit()`.
- Workspace-owned reads require an explicit `workspace_id`.
- Active reads exclude soft-deleted rows unless a named administrative method opts in.
- Hard delete is reserved for junction/ephemeral tables or privileged maintenance flows.
- ORM instances must not cross infrastructure boundaries into application services.

## Example

```python
repository = SqlAlchemyRepository(
    unit_of_work.session,
    Tag,
    workspace_scoped=True,
    search_columns=("name",),
    sortable_columns=frozenset({"name", "created_at", "updated_at"}),
)

tag = await repository.get_by_id(tag_id, workspace_id=workspace_id)
await repository.soft_delete(tag_id, expected_version=tag.version, workspace_id=workspace_id)
```
