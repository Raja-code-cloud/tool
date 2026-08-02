"""Update authenticated user profile command handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.administration.dto.requests import UpdateUserProfileRequestDto
from cloud_content_hub.application.administration.dto.responses import UserSummaryResponse
from cloud_content_hub.application.administration.interfaces.administration_repository import (
    IAdministrationRepository,
    UserProfileUpdate,
)
from cloud_content_hub.application.administration.mappers.administration_mapper import (
    AdministrationMapper,
)
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.core.errors import ValidationError


class UpdateUserProfileCommand:
    """Command payload for profile updates."""

    __slots__ = ("expected_version", "request")

    def __init__(self, *, expected_version: int, request: UpdateUserProfileRequestDto) -> None:
        self.expected_version = expected_version
        self.request = request


class UpdateUserProfileHandler:
    """Updates the authenticated user's global profile."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        administration_repository_factory: Callable[[IUnitOfWork], IAdministrationRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._administration_repository_factory = administration_repository_factory

    async def handle(
        self,
        actor: ActorContext,
        command: UpdateUserProfileCommand,
    ) -> UserSummaryResponse:
        require_permission(actor, "profile:write")
        request = command.request
        if not any(
            value is not None
            for value in (
                request.display_name,
                request.locale,
                request.time_zone,
                request.avatar_object_key,
            )
        ):
            raise ValidationError(detail="At least one profile field must be provided.")

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._administration_repository_factory(unit_of_work)
            user = await repository.update_user_profile(
                UserProfileUpdate(
                    user_id=actor.user_id,
                    expected_version=command.expected_version,
                    display_name=request.display_name,
                    locale=request.locale,
                    time_zone=request.time_zone,
                    avatar_object_key=request.avatar_object_key,
                    updated_by=actor.user_id,
                )
            )
            await unit_of_work.flush()

        return AdministrationMapper.to_user_summary_dto(user)
