"""Search read model to DTO mappers."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from cloud_content_hub.application.assets.interfaces.asset_repository import AssetRecord
from cloud_content_hub.application.content.interfaces.content_repository import ContentRecord
from cloud_content_hub.application.search.dto.requests import SearchEntityTypeDto, SearchFiltersDto
from cloud_content_hub.application.search.dto.responses import (
    RecentSearchResponse,
    SavedSearchResponse,
    SearchResult,
    SearchSuggestion,
    SearchSuggestionKindDto,
)
from cloud_content_hub.application.search.interfaces.publication_search_repository import (
    PublicationSearchRecord,
)
from cloud_content_hub.application.search.interfaces.recent_search_repository import (
    RecentSearchRecord,
)
from cloud_content_hub.application.search.interfaces.saved_search_repository import (
    SavedSearchRecord,
)
from cloud_content_hub.application.search.interfaces.suggestion_repository import (
    SearchSuggestionRecord,
)


class SearchMapper:
    """Maps search read models to response DTOs."""

    @staticmethod
    def from_asset(record: AssetRecord, *, score: float | None = None) -> SearchResult:
        return SearchResult(
            entity_type=SearchEntityTypeDto.ASSET,
            entity_id=record.id,
            title=record.title,
            summary=record.summary,
            score=score,
            updated_at=record.updated_at,
            metadata={
                "assetType": record.asset_type.value,
                "lifecycleStatus": record.lifecycle_status.value,
                "ownerId": str(record.owner_id) if record.owner_id else None,
                "projectId": str(record.project_id) if record.project_id else None,
                "folderId": str(record.folder_id) if record.folder_id else None,
            },
        )

    @staticmethod
    def from_content(record: ContentRecord, *, score: float | None = None) -> SearchResult:
        return SearchResult(
            entity_type=SearchEntityTypeDto.CONTENT,
            entity_id=record.id,
            title=record.title,
            summary=record.body_text,
            score=score,
            updated_at=record.updated_at,
            metadata={
                "assetId": str(record.asset_id),
                "lifecycleStatus": record.lifecycle_status.value,
                "origin": record.origin.value,
            },
        )

    @staticmethod
    def from_publication(
        record: PublicationSearchRecord,
        *,
        score: float | None = None,
    ) -> SearchResult:
        return SearchResult(
            entity_type=SearchEntityTypeDto.PUBLICATION,
            entity_id=record.id,
            title=record.title,
            summary=None,
            score=score,
            updated_at=record.updated_at,
            metadata={
                "assetId": str(record.asset_id),
                "contentVersionId": str(record.content_version_id),
                "status": record.status.value,
            },
        )

    @staticmethod
    def to_saved_search_dto(record: SavedSearchRecord) -> SavedSearchResponse:
        return SavedSearchResponse(
            id=record.id,
            version=record.version,
            created_at=record.created_at,
            updated_at=record.updated_at,
            owner_id=record.owner_id,
            name=record.name,
            query=record.query,
            filters=SearchMapper.filter_spec_to_dto(record.filter_spec),
            sort=record.sort,
            is_shared=record.is_shared,
        )

    @staticmethod
    def to_recent_search_dto(record: RecentSearchRecord) -> RecentSearchResponse:
        return RecentSearchResponse(
            id=record.id,
            query=record.query,
            filters=SearchMapper.filter_spec_to_dto(record.filter_spec),
            executed_at=record.executed_at,
        )

    @staticmethod
    def to_suggestion_dto(record: SearchSuggestionRecord) -> SearchSuggestion:
        return SearchSuggestion(
            text=record.text,
            kind=SearchSuggestionKindDto(record.kind.value),
            entity_type=(
                SearchEntityTypeDto(record.entity_type.value)
                if record.entity_type is not None
                else None
            ),
            entity_id=record.entity_id,
            score=record.score,
        )

    @staticmethod
    def filter_spec_to_dto(filter_spec: dict[str, Any]) -> SearchFiltersDto:
        return SearchFiltersDto(
            entity_types=frozenset(filter_spec.get("entityTypes", ())),
            asset_types=frozenset(filter_spec.get("assetTypes", ())),
            lifecycle_statuses=frozenset(filter_spec.get("lifecycleStatuses", ())),
            content_origins=frozenset(filter_spec.get("contentOrigins", ())),
            publication_statuses=frozenset(filter_spec.get("publicationStatuses", ())),
            owner_id=_parse_uuid(filter_spec.get("ownerId")),
            project_id=_parse_uuid(filter_spec.get("projectId")),
            folder_id=_parse_uuid(filter_spec.get("folderId")),
            updated_after=_parse_datetime(filter_spec.get("updatedAfter")),
            updated_before=_parse_datetime(filter_spec.get("updatedBefore")),
        )


def _parse_uuid(value: object) -> UUID | None:
    if value is None:
        return None
    return UUID(str(value))


def _parse_datetime(value: object) -> datetime | None:
    if value is None:
        return None
    return datetime.fromisoformat(str(value))
