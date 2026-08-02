"""Search repository and provider ports."""

from cloud_content_hub.application.search.interfaces.event_publisher import ISearchEventPublisher
from cloud_content_hub.application.search.interfaces.publication_search_repository import (
    IPublicationSearchRepository,
    PublicationSearchCriteria,
    PublicationSearchPage,
    PublicationSearchRecord,
    PublicationStatus,
)
from cloud_content_hub.application.search.interfaces.recent_search_repository import (
    IRecentSearchRepository,
    NewRecentSearch,
    RecentSearchRecord,
)
from cloud_content_hub.application.search.interfaces.saved_search_repository import (
    ISavedSearchRepository,
    NewSavedSearch,
    SavedSearchRecord,
)
from cloud_content_hub.application.search.interfaces.suggestion_repository import (
    ISearchSuggestionRepository,
    SearchEntityType,
    SearchSuggestionCriteria,
    SearchSuggestionRecord,
    SuggestionKind,
)

__all__ = [
    "IPublicationSearchRepository",
    "IRecentSearchRepository",
    "ISavedSearchRepository",
    "ISearchEventPublisher",
    "ISearchSuggestionRepository",
    "NewRecentSearch",
    "NewSavedSearch",
    "PublicationSearchCriteria",
    "PublicationSearchPage",
    "PublicationSearchRecord",
    "PublicationStatus",
    "RecentSearchRecord",
    "SavedSearchRecord",
    "SearchEntityType",
    "SearchSuggestionCriteria",
    "SearchSuggestionRecord",
    "SuggestionKind",
]
