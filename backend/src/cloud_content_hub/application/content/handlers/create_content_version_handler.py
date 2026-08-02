"""Create content version command handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.content.commands import CreateContentVersionCommand
from cloud_content_hub.application.content.dto.responses import ContentVersionResponse
from cloud_content_hub.application.content.exceptions.content_errors import (
    ContentVersionNotFoundError,
)
from cloud_content_hub.application.content.interfaces.content_repository import IContentRepository
from cloud_content_hub.application.content.mappers.content_mapper import ContentMapper
from cloud_content_hub.application.content.services.content_version_service import (
    ContentVersionService,
)
from cloud_content_hub.application.content.validators.content_validator import (
    validate_expected_version,
    validate_version_creation,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class CreateContentVersionHandler:
    """Orchestrates user-origin version creation."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        content_repository_factory: Callable[[IUnitOfWork], IContentRepository],
        version_service: ContentVersionService | None = None,
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._content_repository_factory = content_repository_factory
        self._version_service = version_service or ContentVersionService()

    async def handle(
        self,
        actor: ActorContext,
        command: CreateContentVersionCommand,
    ) -> ContentVersionResponse:
        require_permission(actor, "content:write")

        async with self._unit_of_work_factory() as unit_of_work:
            content_repository = self._content_repository_factory(unit_of_work)
            content = await content_repository.get_by_id(
                workspace_id=actor.workspace_id,
                content_id=command.content_id,
            )
            content = validate_version_creation(content)
            assert content is not None
            validate_expected_version(content, command.expected_version)

            if command.request.source_version_id is not None:
                source_version = await content_repository.get_version_by_id(
                    workspace_id=actor.workspace_id,
                    version_id=command.request.source_version_id,
                )
                if source_version is None or source_version.asset_id != content.asset_id:
                    raise ContentVersionNotFoundError(
                        parameters={"sourceVersionId": str(command.request.source_version_id)},
                    )

            version, _updated = await self._version_service.create_user_version(
                content_repository,
                content=content,
                title=command.request.title,
                body_text=command.request.body_text,
                body_rich=command.request.body_rich,
                metadata=dict(command.request.metadata),
                source_version_id=command.request.source_version_id,
                change_summary=command.request.change_summary,
                actor_id=actor.user_id,
            )
            await unit_of_work.flush()

        return ContentMapper.to_version_dto(version)
