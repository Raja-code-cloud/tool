"""Get authenticated user profile query handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.administration.dto.responses import UserSummaryResponse
from cloud_content_hub.application.administration.interfaces.administration_repository import (
    IAdministrationRepository,
)
from cloud_content_hub.application.administration.mappers.administration_mapper import (
    AdministrationMapper,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.core.errors import ResourceNotFoundError


class GetUserProfileHandler:
    """Retrieves the authenticated user's global profile."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        administration_repository_factory: Callable[[IUnitOfWork], IAdministrationRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._administration_repository_factory = administration_repository_factory

    async def handle(self, actor: ActorContext) -> UserSummaryResponse:
        require_permission(actor, "profile:read")

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._administration_repository_factory(unit_of_work)
            user = await repository.get_user(actor.user_id)

        if user is None:
            raise ResourceNotFoundError(
                detail="User profile was not found.",
                parameters={"userId": str(actor.user_id)},
            )

        return AdministrationMapper.to_user_summary_dto(user)
