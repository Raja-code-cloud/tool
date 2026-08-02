"""Search suggestions query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.search.dto.responses import SearchSuggestion
from cloud_content_hub.application.search.exceptions.search_errors import SearchAccessDeniedError
from cloud_content_hub.application.search.interfaces.suggestion_repository import (
    ISearchSuggestionRepository,
    SearchEntityType,
    SearchSuggestionCriteria,
)
from cloud_content_hub.application.search.mappers.search_mapper import SearchMapper
from cloud_content_hub.application.search.queries import SearchSuggestionsQuery
from cloud_content_hub.application.search.validators.search_validator import (
    normalize_suggestion_prefix,
    validate_suggestion_limit,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class SearchSuggestionsHandler:
    """Returns autocomplete suggestions for the current prefix."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        suggestion_repository_factory: Callable[[IUnitOfWork], ISearchSuggestionRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._suggestion_repository_factory = suggestion_repository_factory

    async def handle(
        self,
        actor: ActorContext,
        query: SearchSuggestionsQuery,
    ) -> tuple[SearchSuggestion, ...]:
        prefix = normalize_suggestion_prefix(query.prefix)
        validate_suggestion_limit(query.limit)
        entity_types = self._resolve_entity_types(query, actor)
        if not entity_types:
            raise SearchAccessDeniedError(
                detail="The actor lacks permission to receive suggestions for any resource type.",
            )

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._suggestion_repository_factory(unit_of_work)
            records = await repository.suggest(
                SearchSuggestionCriteria(
                    workspace_id=actor.workspace_id,
                    user_id=actor.user_id,
                    prefix=prefix,
                    entity_types=entity_types,
                    limit=query.limit,
                )
            )

        return tuple(SearchMapper.to_suggestion_dto(record) for record in records)

    @staticmethod
    def _resolve_entity_types(
        query: SearchSuggestionsQuery,
        actor: ActorContext,
    ) -> frozenset[SearchEntityType]:
        requested = query.entity_types or frozenset(
            {
                SearchEntityType.ASSET,
                SearchEntityType.CONTENT,
                SearchEntityType.PUBLICATION,
            }
        )
        allowed: set[SearchEntityType] = set()
        if SearchEntityType.ASSET in requested and actor.has_permission("assets:read"):
            allowed.add(SearchEntityType.ASSET)
        if SearchEntityType.CONTENT in requested and actor.has_permission("content:read"):
            allowed.add(SearchEntityType.CONTENT)
        if SearchEntityType.PUBLICATION in requested and actor.has_permission("publishing:read"):
            allowed.add(SearchEntityType.PUBLICATION)
        return frozenset(allowed)
