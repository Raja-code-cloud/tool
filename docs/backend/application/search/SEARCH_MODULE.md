# Search Module

## Purpose

The search application module coordinates discovery use cases for Cloud Content Hub AI. It federates reads across asset, content, and publication repositories, manages saved and recent searches, and exposes a unified `SearchResult` projection to delivery layers.

Implementation lives in `backend/src/cloud_content_hub/application/search/`.

## Structure

```text
search/
├── commands/         # SaveSearch, DeleteSavedSearch, ClearRecentSearches
├── queries/          # SearchAll, SearchAssets, SearchContent, SearchPublications, ...
├── handlers/         # Command and query handler classes
├── dto/              # SearchRequest, SearchResponse, SearchResult, SearchSuggestion, ...
├── validators/       # Query length, filters, sort allowlists, ownership
├── interfaces/       # Saved/recent/suggestion/publication search repository ports
├── exceptions/       # Search-specific application errors
├── mappers/          # Read model → response DTO mapping
├── services/         # GlobalSearchService, SearchHistoryService
└── events/           # SearchExecuted, SavedSearchCreated, ...
```

## Use cases

| Use case              | Handler                      | Permission                                              |
| --------------------- | ---------------------------- | ------------------------------------------------------- |
| Global search         | `SearchAllHandler`           | Any of `assets:read`, `content:read`, `publishing:read` |
| Search assets         | `SearchAssetsHandler`        | `assets:read`                                           |
| Search content        | `SearchContentHandler`       | `content:read`                                          |
| Search publications   | `SearchPublicationsHandler`  | `publishing:read`                                       |
| Recent searches       | `GetRecentSearchesHandler`   | Any search read permission                              |
| Saved searches        | `GetSavedSearchesHandler`    | Any search read permission                              |
| Suggestions           | `SearchSuggestionsHandler`   | Entity-scoped read permissions                          |
| Save search           | `SaveSearchHandler`          | Any search read permission                              |
| Delete saved search   | `DeleteSavedSearchHandler`   | Owner only                                              |
| Clear recent searches | `ClearRecentSearchesHandler` | Current user history only                               |

## Business rules

- All searches are scoped to `actor.workspace_id`.
- Users only search entity types they hold read permission for.
- Recent search history belongs to the authenticated user.
- Saved searches are workspace scoped; deletion requires ownership.
- Handlers never return ORM models — only application DTOs.

## Repository orchestration

| Port                           | Responsibility                                   |
| ------------------------------ | ------------------------------------------------ |
| `IAssetRepository`             | Asset full-text search (existing assets port)    |
| `IContentRepository`           | Content full-text search (existing content port) |
| `IPublicationSearchRepository` | Publication full-text search                     |
| `ISavedSearchRepository`       | Persisted saved searches                         |
| `IRecentSearchRepository`      | Per-user recent search history                   |
| `ISearchSuggestionRepository`  | Autocomplete suggestions                         |

Infrastructure implements the search-specific ports. Application handlers depend on ports only.

## Events

| Event                 | Trigger                                |
| --------------------- | -------------------------------------- |
| `SearchExecuted`      | Successful search that records history |
| `SavedSearchCreated`  | Saved search persisted                 |
| `SavedSearchDeleted`  | Saved search soft-deleted              |
| `RecentSearchCleared` | User clears recent history             |

Events are published through `ISearchEventPublisher` inside the same unit-of-work transaction as the originating mutation.

## Related

- [Global search](GLOBAL_SEARCH.md)
- [Filters](FILTERS.md)
- [Saved searches](SAVED_SEARCHES.md)
- [Application layer](../APPLICATION_LAYER.md)
