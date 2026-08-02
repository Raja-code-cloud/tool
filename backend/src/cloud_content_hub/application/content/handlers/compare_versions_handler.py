"""Compare content versions query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.content.dto.responses import VersionComparisonResponse
from cloud_content_hub.application.content.exceptions.content_errors import (
    ContentVersionNotFoundError,
)
from cloud_content_hub.application.content.interfaces.content_repository import IContentRepository
from cloud_content_hub.application.content.mappers.content_mapper import ContentMapper
from cloud_content_hub.application.content.queries import CompareVersionsQuery
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class CompareVersionsHandler:
    """Compares two immutable content versions."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        content_repository_factory: Callable[[IUnitOfWork], IContentRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._content_repository_factory = content_repository_factory

    async def handle(
        self,
        actor: ActorContext,
        query: CompareVersionsQuery,
    ) -> VersionComparisonResponse:
        require_permission(actor, "content:read")

        async with self._unit_of_work_factory() as unit_of_work:
            content_repository = self._content_repository_factory(unit_of_work)
            comparison = await content_repository.compare_versions(
                workspace_id=actor.workspace_id,
                source_version_id=query.source_version_id,
                target_version_id=query.target_version_id,
            )
            if comparison is None:
                raise ContentVersionNotFoundError(
                    parameters={
                        "sourceVersionId": str(query.source_version_id),
                        "targetVersionId": str(query.target_version_id),
                    },
                )

        return ContentMapper.to_comparison_dto(comparison)
