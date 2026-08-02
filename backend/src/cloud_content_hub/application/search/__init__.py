"""Search application module."""

from cloud_content_hub.application.search.commands import (
    ClearRecentSearchesCommand,
    DeleteSavedSearchCommand,
    SaveSearchCommand,
)
from cloud_content_hub.application.search.dto.responses import (
    RecentSearchResponse,
    SavedSearchResponse,
    SearchResponse,
    SearchResult,
    SearchSuggestion,
)
from cloud_content_hub.application.search.events import (
    RecentSearchCleared,
    SavedSearchCreated,
    SavedSearchDeleted,
    SearchExecuted,
)
from cloud_content_hub.application.search.handlers.clear_recent_searches_handler import (
    ClearRecentSearchesHandler,
)
from cloud_content_hub.application.search.handlers.delete_saved_search_handler import (
    DeleteSavedSearchHandler,
)
from cloud_content_hub.application.search.handlers.get_recent_searches_handler import (
    GetRecentSearchesHandler,
)
from cloud_content_hub.application.search.handlers.get_saved_searches_handler import (
    GetSavedSearchesHandler,
)
from cloud_content_hub.application.search.handlers.save_search_handler import SaveSearchHandler
from cloud_content_hub.application.search.handlers.search_all_handler import SearchAllHandler
from cloud_content_hub.application.search.handlers.search_assets_handler import SearchAssetsHandler
from cloud_content_hub.application.search.handlers.search_content_handler import (
    SearchContentHandler,
)
from cloud_content_hub.application.search.handlers.search_publications_handler import (
    SearchPublicationsHandler,
)
from cloud_content_hub.application.search.handlers.search_suggestions_handler import (
    SearchSuggestionsHandler,
)
from cloud_content_hub.application.search.queries import (
    GetRecentSearchesQuery,
    GetSavedSearchesQuery,
    SearchAllQuery,
    SearchAssetsQuery,
    SearchContentQuery,
    SearchPublicationsQuery,
    SearchSuggestionsQuery,
)
from cloud_content_hub.application.search.services.global_search_service import GlobalSearchService
from cloud_content_hub.application.search.services.search_history_service import (
    SearchHistoryService,
)

__all__ = [
    "ClearRecentSearchesCommand",
    "ClearRecentSearchesHandler",
    "DeleteSavedSearchCommand",
    "DeleteSavedSearchHandler",
    "GetRecentSearchesHandler",
    "GetRecentSearchesQuery",
    "GetSavedSearchesHandler",
    "GetSavedSearchesQuery",
    "GlobalSearchService",
    "RecentSearchCleared",
    "RecentSearchResponse",
    "SaveSearchCommand",
    "SaveSearchHandler",
    "SavedSearchCreated",
    "SavedSearchDeleted",
    "SavedSearchResponse",
    "SearchAllHandler",
    "SearchAllQuery",
    "SearchAssetsHandler",
    "SearchAssetsQuery",
    "SearchContentHandler",
    "SearchContentQuery",
    "SearchExecuted",
    "SearchHistoryService",
    "SearchPublicationsHandler",
    "SearchPublicationsQuery",
    "SearchResponse",
    "SearchResult",
    "SearchSuggestion",
    "SearchSuggestionsHandler",
    "SearchSuggestionsQuery",
]
