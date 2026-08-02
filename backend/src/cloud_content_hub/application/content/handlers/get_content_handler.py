"""Get content query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.content.dto.responses import ContentDto
from cloud_content_hub.application.content.exceptions.content_errors import ContentNotFoundError
from cloud_content_hub.application.content.interfaces.content_repository import IContentRepository
from cloud_content_hub.application.content.mappers.content_mapper import ContentMapper
from cloud_content_hub.application.content.queries import GetContentQuery
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class GetContentHandler:
    """Retrieves a single content projection."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        content_repository_factory: Callable[[IUnitOfWork], IContentRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._content_repository_factory = content_repository_factory

    async def handle(self, actor: ActorContext, query: GetContentQuery) -> ContentDto:
        require_permission(actor, "content:read")

        async with self._unit_of_work_factory() as unit_of_work:
            content_repository = self._content_repository_factory(unit_of_work)
            content = await content_repository.get_by_id(
                workspace_id=actor.workspace_id,
                content_id=query.content_id,
            )
            if content is None:
                raise ContentNotFoundError(parameters={"contentId": str(query.content_id)})

        return ContentMapper.to_dto(content)
