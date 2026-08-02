# Search Filters

## Overview

Search filters are validated in `search/validators/search_validator.py` and serialized to JSON-safe specifications for saved and recent searches.

## Filter DTO: `SearchFiltersDto`

| Field                  | Type                             | Description                                             |
| ---------------------- | -------------------------------- | ------------------------------------------------------- |
| `entity_types`         | `frozenset[SearchEntityTypeDto]` | Limit results to asset, content, or publication         |
| `asset_types`          | `frozenset[str]`                 | Asset subtype allowlist                                 |
| `lifecycle_statuses`   | `frozenset[str]`                 | Shared lifecycle filter (`draft`, `active`, `archived`) |
| `content_origins`      | `frozenset[str]`                 | Content origin allowlist                                |
| `publication_statuses` | `frozenset[str]`                 | Publication status allowlist                            |
| `owner_id`             | `UUID \| None`                   | Asset owner                                             |
| `project_id`           | `UUID \| None`                   | Asset project                                           |
| `folder_id`            | `UUID \| None`                   | Asset folder                                            |
| `updated_after`        | `datetime \| None`               | Updated-at lower bound                                  |
| `updated_before`       | `datetime \| None`               | Updated-at upper bound                                  |

## Supported values

### Asset types

`article`, `video`, `poster`, `thumbnail`

### Lifecycle statuses

`draft`, `active`, `archived`

### Content origins

`user`, `ai`, `import`, `regeneration`

### Publication statuses

`draft`, `ready`, `in_progress`, `completed`, `partially_failed`, `cancelled`

## Validation rules

| Rule                              | Error                          |
| --------------------------------- | ------------------------------ |
| Unknown asset type                | `UnsupportedSearchFilterError` |
| Unknown lifecycle status          | `UnsupportedSearchFilterError` |
| Unknown content origin            | `UnsupportedSearchFilterError` |
| Unknown publication status        | `UnsupportedSearchFilterError` |
| `updated_after >= updated_before` | `ValidationError`              |
| Unknown sort field                | `UnsupportedSearchSortError`   |
| Page size outside 1–100           | `ValidationError`              |
| Query outside 2–200 chars         | `ValidationError`              |

## Filter specification storage

Saved and recent searches persist filters as a camelCase JSON object via `filters_to_spec()`:

```json
{
  "entityTypes": ["asset", "content"],
  "assetTypes": ["poster"],
  "lifecycleStatuses": ["active"],
  "ownerId": "01900000-0000-7000-8000-000000000201"
}
```

`SearchMapper.filter_spec_to_dto()` reverses the mapping when returning saved or recent search DTOs.

## Advanced filter application

| Filter                                             | Applied by                         |
| -------------------------------------------------- | ---------------------------------- |
| Asset, content, publication repository filters     | Repository implementations         |
| `updated_after`, `updated_before` on global search | `GlobalSearchService` (post-merge) |
| Entity type restriction                            | Permission-aware entity resolution |

## Related

- [Global search](GLOBAL_SEARCH.md)
- [Saved searches](SAVED_SEARCHES.md)
