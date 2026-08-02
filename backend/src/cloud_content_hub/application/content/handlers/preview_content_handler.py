"""Preview content query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.content.dto.responses import ContentPreviewResponse
from cloud_content_hub.application.content.exceptions.content_errors import (
    ContentVersionNotFoundError,
)
from cloud_content_hub.application.content.interfaces.content_repository import IContentRepository
from cloud_content_hub.application.content.queries import PreviewContentQuery
from cloud_content_hub.application.content.services.content_generation_service import (
    ContentGenerationService,
)
from cloud_content_hub.application.content.validators.content_validator import (
    validate_generation_request,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class PreviewContentHandler:
    """Generates a non-persisted preview through the AI port."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        content_repository_factory: Callable[[IUnitOfWork], IContentRepository],
        generation_service: ContentGenerationService,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._content_repository_factory = content_repository_factory
        self._generation_service = generation_service

    async def handle(
        self, actor: ActorContext, query: PreviewContentQuery
    ) -> ContentPreviewResponse:
        require_permission(actor, "content:generate")
        validate_generation_request(query.request)

        async with self._unit_of_work_factory() as unit_of_work:
            content_repository = self._content_repository_factory(unit_of_work)
            source_version = await content_repository.get_version_detail_by_id(
                workspace_id=actor.workspace_id,
                version_id=query.request.source_version_id,
            )
            if source_version is None:
                raise ContentVersionNotFoundError(
                    parameters={"sourceVersionId": str(query.request.source_version_id)},
                )

        model = str(query.request.parameters.get("model") or query.request.model_id)
        return await self._generation_service.preview(
            request=query.request,
            scope=query.request.scope,
            model=model,
            source_title=source_version.title,
            source_body=source_version.body_text,
            parameters=dict(query.request.parameters),
        )
