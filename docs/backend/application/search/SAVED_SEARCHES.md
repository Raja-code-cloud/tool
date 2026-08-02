# Saved Searches

## Overview

Saved searches let users persist named query and filter combinations within a workspace. Recent searches capture ephemeral query history per user.

## Saved searches

### Command: `SaveSearchCommand`

| Field               | Type               | Description                        |
| ------------------- | ------------------ | ---------------------------------- |
| `request.name`      | `str`              | Display name (1–120 chars)         |
| `request.query`     | `str`              | Search text (2–200 chars)          |
| `request.filters`   | `SearchFiltersDto` | Advanced filters                   |
| `request.sort`      | `str`              | Sort allowlist value               |
| `request.is_shared` | `bool`             | Visible to other workspace members |

Returns: `SavedSearchResponse`

### Query: `GetSavedSearchesQuery`

| Field            | Type   | Default | Description                   |
| ---------------- | ------ | ------- | ----------------------------- |
| `include_shared` | `bool` | `true`  | Include shared saved searches |

Returns: `tuple[SavedSearchResponse, ...]`

The repository returns searches owned by the actor plus shared searches when `include_shared` is true.

### Command: `DeleteSavedSearchCommand`

| Field              | Type   | Description                    |
| ------------------ | ------ | ------------------------------ |
| `saved_search_id`  | `UUID` | Saved search identifier        |
| `expected_version` | `int`  | Optimistic concurrency version |

Only the owner may delete a saved search. Deletion is a soft delete through `ISavedSearchRepository.soft_delete`.

Raises:

- `SavedSearchNotFoundError` when the record is missing
- `SavedSearchOwnershipError` when the actor is not the owner
- `VersionConflictError` on version mismatch

## Recent searches

### Query: `GetRecentSearchesQuery`

| Field   | Type  | Default | Description            |
| ------- | ----- | ------- | ---------------------- |
| `limit` | `int` | 10      | Maximum entries (1–50) |

Returns: `tuple[RecentSearchResponse, ...]`

Recent searches are always scoped to `actor.user_id` within `actor.workspace_id`.

### Command: `ClearRecentSearchesCommand`

Clears all recent searches for the authenticated user.

Returns: `int` — number of entries removed.

## History recording

Entity search handlers and `SearchAllHandler` call `SearchHistoryService.record()` after a successful search. The service:

1. Upserts a recent search row through `IRecentSearchRepository`
2. Optionally publishes `SearchExecuted` through `ISearchEventPublisher`

## Events

| Event                 | Payload highlights                                     |
| --------------------- | ------------------------------------------------------ |
| `SavedSearchCreated`  | `saved_search_id`, `owner_id`, `name`                  |
| `SavedSearchDeleted`  | `saved_search_id`, `owner_id`, `version`               |
| `RecentSearchCleared` | `user_id`, `cleared_count`                             |
| `SearchExecuted`      | `query`, `entity_types`, `result_count`, `filter_spec` |

## Authorization summary

| Operation             | Rule                                           |
| --------------------- | ---------------------------------------------- |
| List saved searches   | Any search read permission; workspace scoped   |
| Save search           | Any search read permission; owner set to actor |
| Delete saved search   | Owner only                                     |
| List recent searches  | Current user only                              |
| Clear recent searches | Current user only                              |

## Related

- [Search module overview](SEARCH_MODULE.md)
- [Filters](FILTERS.md)
