# Query Strategy

## Overview

Repository adapters combine three query building blocks:

1. **`SqlAlchemyRepository`** — generic CRUD, soft delete, optimistic locking, offset pagination.
2. **`cursor_pagination.py`** — keyset (cursor) pagination used by application search ports.
3. **Adapter-specific SQLAlchemy queries** — joins, aggregates, eager loading, and filters
   that are too domain-specific for the generic repository.

All queries follow the same invariants: explicit workspace scope, active-row filtering, and
no transaction commits inside adapters.

## Workspace isolation

Every workspace-owned table query includes:

```python
Model.workspace_id == workspace_id
Model.deleted_at.is_(None)  # unless explicitly including deleted rows
```

Cross-workspace reads are rejected by returning `None` or empty result sets rather than
raising, matching application port semantics.

Composite foreign keys (for example `workspace_id` + `project_id`) are honored when joining
related tables so rows cannot leak across tenants through surrogate keys alone.

## Soft delete

Active reads use `active_row_expression()` or repository defaults that append
`deleted_at IS NULL`. Named port methods such as `get_deleted_by_id` opt in to deleted rows.

Restore and soft-delete mutations increment the row `version` through the generic repository
so concurrent updates are detected.

## Optimistic locking

Mutable rows carry a mapped `version` column (`VersionMixin`). Updates call
`SqlAlchemyRepository.update(..., expected_version=...)` or equivalent version-checked
SQLAlchemy updates. Stale writes raise `ConcurrencyConflict` for the application layer to map.

## Pagination

### Offset pagination (generic repository)

`find_paginated` and `find_offset` on `SqlAlchemyRepository` use page number and limit.
These remain available for internal or legacy flows but are not exposed on application search
ports.

### Keyset cursor pagination (application ports)

Application search criteria carry `cursor`, `limit`, and `sort`. Adapters:

1. Parse and validate the sort token against an allowlist (`normalize_sort_token`).
2. Apply keyset predicates with `apply_keyset_pagination` (fetch `limit + 1` rows).
3. Build the response page with `build_keyset_page`, returning `items`, `next_cursor`, and
   `has_more`.

Cursor encoding is opaque base64 JSON containing sort column, direction, sort value, and
entity id. Cursors are tied to a specific sort; changing sort invalidates prior cursors.

Supported sort columns are declared per adapter (for example assets: `updated_at`, `created_at`).

## Filtering and search

| Domain         | Strategy                                                                                                                                                    |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Assets         | PostgreSQL `to_tsquery` full-text search on `ContentAsset.search_vector` when `query` is set; additional filters on type, lifecycle, owner, project, folder |
| Content        | Title/body ILIKE and lifecycle filters; cursor pagination on content list                                                                                   |
| Notifications  | ILIKE on title/body, severity/type/read/archive/time-range filters; join to `NotificationType` for type code                                                |
| Analytics      | Latest snapshot subquery per publication target; metric code filtering on read models; observation aggregation with optional platform/account scope         |
| Administration | Workspace and user listing with membership joins; settings lookups by scoped key                                                                            |
| Users (helper) | Workspace membership join; display name/email ILIKE                                                                                                         |

## Sorting

Sort tokens use a leading `-` for descending order (for example `-updated_at`). Unknown columns
raise `SpecificationError` at the infrastructure boundary.

Analytics post-performance ranking maps API camelCase fields (`engagementRate`) to ORM column
names (`engagement_rate`).

## Eager loading

Adapters use `selectinload` / joined loads only where N+1 queries would occur on hot read paths:

- Asset details: storage links and tags when building `AssetRecord`.
- Content reads: draft and version relationships for aggregate assembly.
- Notifications: notification type code via join or aliased select.

Loads are kept minimal — adapters fetch only columns needed for the target read model.

## Aggregations and snapshots

Analytics adapters prefer pre-materialized `AnalyticsSnapshot` rows keyed by period,
`snapshot_type`, and dimension payload (for example platform id set). When no snapshot exists,
they fall back to live aggregation over `MetricObservation` and `ContentPerformanceSnapshot`.

Dashboard cache refresh writes or replaces workspace KPI snapshots; archive flows create
reference snapshots rather than deleting source rows.

## Bulk operations

Bulk creates use `session.add_all` followed by `flush` (imports, multi-row inserts). Bulk soft
delete/update delegate to generic repository bulk helpers where the port requires them.

## Transaction usage

Adapters assume an open transaction from `SqlAlchemyUnitOfWork`. They may call `flush()` to
assign server-generated values or enforce constraints before subsequent queries in the same
request, but never `commit()` or `rollback()`.

## Performance guidelines

- Prefer keyset pagination over offset for large inbox and library lists.
- Push filters into SQL; avoid loading collections into Python for filtering.
- Use `limit + 1` cursor fetches instead of separate count queries for `has_more`.
- Scope aggregates by workspace and time range indexes (`observed_at`, `snapshot_at`).
- Reuse subqueries (for example latest performance snapshot per target) instead of correlated
  per-row lookups.

## Related documentation

- Adapter inventory: `docs/backend/repository-adapters/REPOSITORY_ADAPTERS.md`
- Generic pagination: `docs/backend/repositories/PAGINATION.md`
- Filtering pattern: `docs/backend/repositories/FILTERING.md`
