# Filtering

## Purpose

Repository filtering helpers translate common list/query parameters into safe SQLAlchemy predicates.

## RepositoryFilter

`RepositoryFilter` supports:

| Field                              | Purpose                                                         |
| ---------------------------------- | --------------------------------------------------------------- |
| `search`                           | case-insensitive substring search across configured columns     |
| `created_after` / `created_before` | creation timestamp bounds                                       |
| `updated_after` / `updated_before` | update timestamp bounds                                         |
| `status`                           | exact match on a mapped `status` column                         |
| `platform`                         | exact match on a mapped or aliased platform column              |
| `tags`                             | tag membership when the mapped model exposes a `tags` attribute |
| `custom`                           | explicit attribute/value pairs via `filterable_columns`         |

## Repository configuration

Construct repositories with explicit allowlists:

```python
SqlAlchemyRepository(
    session,
    SocialAccount,
    workspace_scoped=True,
    search_columns=("display_name", "external_account_id"),
    sortable_columns=frozenset({"display_name", "updated_at"}),
    filterable_columns={"platform": "platform_id"},
)
```

Unknown sort or filter targets raise `SpecificationError`.

## Active-row behavior

Filters apply after the active-row predicate (`deleted_at IS NULL`) unless the caller explicitly requests deleted rows through repository method parameters intended for administrative access.

## Workspace scope

Workspace-owned repositories require `workspace_id` on read and mutation methods. Filters never substitute for tenant scope.

## Custom filters

Use `custom` for stable, allowlisted query parameters that map to specific columns. Do not accept arbitrary column names from clients.

For join-heavy filters such as asset tags through junction tables, prefer:

1. an entity-specific repository helper, or
2. a `CustomSpecification`

## Search behavior

Search uses `ILIKE` against each configured search column and combines the predicates with OR semantics. Empty or whitespace-only search values are ignored.
