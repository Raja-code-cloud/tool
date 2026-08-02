"""Get content version query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.content.dto.responses import ContentVersionResponse
from cloud_content_hub.application.content.exceptions.content_errors import (
    ContentVersionNotFoundError,
)
from cloud_content_hub.application.content.interfaces.content_repository import IContentRepository
from cloud_content_hub.application.content.mappers.content_mapper import ContentMapper
from cloud_content_hub.application.content.queries import GetContentVersionQuery
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class GetContentVersionHandler:
    """Retrieves a single content version projection."""

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
        query: GetContentVersionQuery,
    ) -> ContentVersionResponse:
        require_permission(actor, "content:read")

        async with self._unit_of_work_factory() as unit_of_work:
            content_repository = self._content_repository_factory(unit_of_work)
            version = await content_repository.get_version_detail_by_id(
                workspace_id=actor.workspace_id,
                version_id=query.version_id,
            )
            if version is None:
                raise ContentVersionNotFoundError(parameters={"versionId": str(query.version_id)})

        return ContentMapper.to_version_dto(version)
