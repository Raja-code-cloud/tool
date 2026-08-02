# Asset Search and Listing

## Overview

Asset reads are split into two query handlers:

- **`ListAssetsHandler`** — structured filters without full-text search
- **`SearchAssetsHandler`** — full-text search with optional filters

Both return `PagedResultDto[AssetDto]` with cursor pagination.

## List assets

### Query: `ListAssetsQuery`

| Field                | Type                              | Default       | Description              |
| -------------------- | --------------------------------- | ------------- | ------------------------ |
| `asset_types`        | `frozenset[AssetType]`            | all           | Filter by asset type     |
| `lifecycle_statuses` | `frozenset[AssetLifecycleStatus]` | all           | Filter by lifecycle      |
| `owner_id`           | `UUID \| None`                    | none          | Filter by owner          |
| `project_id`         | `UUID \| None`                    | none          | Filter by project        |
| `folder_id`          | `UUID \| None`                    | none          | Filter by folder         |
| `cursor`             | `str \| None`                     | none          | Opaque pagination cursor |
| `limit`              | `int`                             | 25            | Page size (1–100)        |
| `sort`               | `str`                             | `-updated_at` | Sort allowlist           |

### Sort allowlist

- `updated_at`, `-updated_at`
- `created_at`, `-created_at`
- `title`, `-title`

### Repository method

`IAssetRepository.list_assets` applies workspace scoping, active-only filter (`deleted_at IS NULL`), and cursor-based pagination.

## Search assets

### Query: `SearchAssetsQuery`

| Field                | Type                              | Default     | Description                   |
| -------------------- | --------------------------------- | ----------- | ----------------------------- |
| `query`              | `str`                             | required    | Full-text query (2–200 chars) |
| `asset_types`        | `frozenset[AssetType]`            | all         | Filter by asset type          |
| `lifecycle_statuses` | `frozenset[AssetLifecycleStatus]` | all         | Filter by lifecycle           |
| `cursor`             | `str \| None`                     | none        | Opaque pagination cursor      |
| `limit`              | `int`                             | 25          | Page size                     |
| `sort`               | `str`                             | `relevance` | Sort mode                     |

### Query validation

The handler normalizes and validates the search query:

- Trimmed length must be 2–200 characters
- Invalid queries raise `ValidationError`

### Sort modes

| Value         | Behavior                                    |
| ------------- | ------------------------------------------- |
| `relevance`   | Full-text rank, then stable `id` tiebreaker |
| `-updated_at` | Most recently updated first                 |
| `updated_at`  | Oldest updated first                        |

### Full-text index

Assets store a `search_document` tsvector column on `content_assets`. The repository implementation uses PostgreSQL full-text search against title and summary fields.

## Get single asset

### Query: `GetAssetQuery`

Returns one active asset scoped to the workspace. When media scan status is `clean`, `AssetMapper` generates a short-lived download URL (15 minutes) via `IObjectStoragePort.generate_download_url`.

### Query: `GetAssetDetailsQuery`

Returns extended details via `AssetDetailsDto`:

- All fields from `AssetDto`
- `version_count` — immutable content version count
- `publication_count` — active publication references
- `collection_count` — collection membership count
- `comment_count` — comment count

## Asset usage

### Query: `AssetUsageQuery`

Returns dependency summary via `AssetUsageDto`:

| Field               | Description                                   |
| ------------------- | --------------------------------------------- |
| `publication_count` | Publications referencing this asset           |
| `collection_count`  | Collections containing this asset             |
| `relation_count`    | Content relations (incoming + outgoing)       |
| `can_delete`        | Whether soft-delete is safe                   |
| `blocking_reasons`  | Human-readable blockers when delete is unsafe |

## Response shape

All list/search handlers return:

```json
{
  "items": [/* AssetDto[] */],
  "page": {
    "nextCursor": "opaque-cursor-or-null",
    "hasMore": true,
    "limit": 25
  }
}
```

No total count is computed (expensive at scale).

## Authorization

All query handlers require `assets:read` permission and scope reads to `actor.workspace_id`.

## Related

- [API contract](../../api/ASSET_API.md)
- [Pagination](../../repositories/PAGINATION.md)
- [Filtering](../../repositories/FILTERING.md)
