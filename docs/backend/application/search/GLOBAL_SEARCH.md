# Global Search

## Overview

`SearchAllHandler` delegates to `GlobalSearchService`, which federates search across assets, content, and publications. Results are merged into a single `SearchResponse` with unified `SearchResult` items.

## Query: `SearchAllQuery`

| Field                        | Type                                | Default       | Description                              |
| ---------------------------- | ----------------------------------- | ------------- | ---------------------------------------- |
| `query`                      | `str`                               | required      | Full-text query (2–200 chars after trim) |
| `entity_types`               | `frozenset[SearchEntityType]`       | all permitted | Limit entity types                       |
| `asset_types`                | `frozenset[AssetType]`              | all           | Asset subtype filter                     |
| `lifecycle_statuses`         | `frozenset[AssetLifecycleStatus]`   | all           | Asset lifecycle filter                   |
| `content_lifecycle_statuses` | `frozenset[ContentLifecycleStatus]` | all           | Content lifecycle filter                 |
| `content_origins`            | `frozenset[ContentOrigin]`          | all           | Content origin filter                    |
| `publication_statuses`       | `frozenset[PublicationStatus]`      | all           | Publication status filter                |
| `owner_id`                   | `UUID \| None`                      | none          | Asset owner filter                       |
| `project_id`                 | `UUID \| None`                      | none          | Asset project filter                     |
| `folder_id`                  | `UUID \| None`                      | none          | Asset folder filter                      |
| `updated_after`              | `datetime \| None`                  | none          | Client-side updated-at lower bound       |
| `updated_before`             | `datetime \| None`                  | none          | Client-side updated-at upper bound       |
| `cursor`                     | `str \| None`                       | none          | Opaque pagination cursor                 |
| `limit`                      | `int`                               | 25            | Page size (1–100)                        |
| `sort`                       | `str`                               | `relevance`   | Global sort allowlist                    |

## Permission filtering

The service resolves entity types against the actor's permissions:

| Entity type   | Required permission |
| ------------- | ------------------- |
| `asset`       | `assets:read`       |
| `content`     | `content:read`      |
| `publication` | `publishing:read`   |

When no requested entity type is permitted, the handler raises `SearchAccessDeniedError`.

## Merge strategy

1. Search each permitted entity repository with the normalized query.
2. Map records to `SearchResult` via `SearchMapper`.
3. Apply optional `updated_after` / `updated_before` filters in memory.
4. Sort merged hits by `updated_at` (or relevance when supported by repositories).
5. Truncate to the requested `limit`.

## Response shape

```json
{
  "items": [
    {
      "entityType": "asset",
      "entityId": "01900000-0000-7000-8000-000000000101",
      "title": "Launch poster",
      "summary": "Campaign creative",
      "score": null,
      "highlight": null,
      "updatedAt": "2026-08-02T12:00:00Z",
      "metadata": {
        "assetType": "poster",
        "lifecycleStatus": "active"
      }
    }
  ],
  "query": "launch",
  "filters": {},
  "pageNextCursor": null,
  "pageHasMore": false,
  "pageLimit": 25
}
```

## Search history

Every successful global search records a recent search entry through `SearchHistoryService` and optionally emits `SearchExecuted`.

## Entity-specific handlers

Dedicated handlers return the same `SearchResponse` envelope scoped to one entity type:

- `SearchAssetsHandler` → `IAssetRepository.search`
- `SearchContentHandler` → `IContentRepository.search`
- `SearchPublicationsHandler` → `IPublicationSearchRepository.search`

These handlers require the corresponding entity read permission and record history for their entity type only.

## Sort allowlists

| Scope        | Allowed values                                                                           |
| ------------ | ---------------------------------------------------------------------------------------- |
| Global       | `relevance`, `-updated_at`, `updated_at`                                                 |
| Assets       | `relevance`, `-updated_at`, `updated_at`, `-created_at`, `created_at`                    |
| Content      | `relevance`, `-updated_at`, `updated_at`, `-created_at`, `created_at`, `title`, `-title` |
| Publications | `relevance`, `-updated_at`, `updated_at`                                                 |

## Related

- [Search module overview](SEARCH_MODULE.md)
- [Filters](FILTERS.md)
