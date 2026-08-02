"""Create publication command handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.publishing.commands import PublishContentCommand
from cloud_content_hub.application.publishing.dto.responses import PublicationDto
from cloud_content_hub.application.publishing.interfaces.publication_repository import (
    IPublicationRepository,
    NewPublication,
    NewPublicationTarget,
)
from cloud_content_hub.application.publishing.mappers.publication_mapper import PublicationMapper
from cloud_content_hub.application.publishing.validators.publication_validator import (
    validate_create_publication,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork


class CreatePublicationHandler:
    """Orchestrates publication creation."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        publication_repository_factory: Callable[[IUnitOfWork], IPublicationRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._publication_repository_factory = publication_repository_factory

    async def handle(self, actor: ActorContext, command: PublishContentCommand) -> PublicationDto:
        require_permission(actor, "publishing:write")

        async with self._unit_of_work_factory() as unit_of_work:
            publication_repository = self._publication_repository_factory(unit_of_work)

            asset_id, version_approved = await publication_repository.validate_content_version(
                workspace_id=actor.workspace_id,
                content_id=command.request.content_id,
                content_version_id=command.request.content_version_id,
            )
            account_ids = frozenset(target.social_account_id for target in command.request.targets)
            accounts_healthy = await publication_repository.validate_social_accounts(
                workspace_id=actor.workspace_id,
                social_account_ids=account_ids,
            )
            validate_create_publication(
                command.request,
                asset_id=asset_id,
                version_approved=version_approved,
                accounts_healthy=accounts_healthy,
            )

            publication = await publication_repository.create(
                NewPublication(
                    workspace_id=actor.workspace_id,
                    asset_id=asset_id,
                    content_version_id=command.request.content_version_id,
                    title=command.request.title,
                    targets=tuple(
                        NewPublicationTarget(
                            social_account_id=target.social_account_id,
                            generation_output_id=target.generation_output_id,
                        )
                        for target in command.request.targets
                    ),
                    created_by=actor.user_id,
                )
            )
            await unit_of_work.flush()

        return PublicationMapper.to_dto(publication)
