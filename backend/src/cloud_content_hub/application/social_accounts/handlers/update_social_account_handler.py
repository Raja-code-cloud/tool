"""Update social account command handler."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from uuid import UUID

from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.application.social_accounts.dto.requests import UpdateSocialAccountRequestDto
from cloud_content_hub.application.social_accounts.dto.responses import SocialAccountDto
from cloud_content_hub.application.social_accounts.exceptions.social_account_errors import (
    SocialAccountNotFoundError,
)
from cloud_content_hub.application.social_accounts.interfaces.social_account_repository import (
    DefaultSettingsUpdate,
    ISocialAccountRepository,
    SocialAccountUpdate,
)
from cloud_content_hub.application.social_accounts.mappers.social_account_mapper import (
    SocialAccountMapper,
)
from cloud_content_hub.core.errors import VersionConflictError


class UpdateSocialAccountHandler:
    """Updates mutable social account settings."""

    def __init__(
        self,
        *,
        unit_of_work_factory: Callable[[], IUnitOfWork],
        social_account_repository_factory: Callable[[IUnitOfWork], ISocialAccountRepository],
    ) -> None:
        self._unit_of_work_factory = unit_of_work_factory
        self._social_account_repository_factory = social_account_repository_factory

    async def handle(
        self,
        actor: ActorContext,
        command: dict[str, Any],
    ) -> SocialAccountDto:
        require_permission(actor, "publishing:write")

        account_id: UUID = command["account_id"]
        expected_version: int = command["expected_version"]
        request: UpdateSocialAccountRequestDto = command["request"]

        default_settings = None
        if request.default_settings is not None:
            default_settings = DefaultSettingsUpdate(
                visibility=request.default_settings.visibility,
                hashtag_strategy=request.default_settings.hashtags,
                auto_publish=request.default_settings.auto_publish,
                ai_optimization=request.default_settings.ai_optimization,
                auto_schedule=request.default_settings.auto_schedule,
                url_tracking=request.default_settings.url_tracking,
            )

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._social_account_repository_factory(unit_of_work)
            existing = await repository.get_by_id(
                workspace_id=actor.workspace_id,
                account_id=account_id,
            )
            if existing is None:
                raise SocialAccountNotFoundError(parameters={"accountId": str(account_id)})
            if existing.version != expected_version:
                raise VersionConflictError(
                    parameters={
                        "accountId": str(account_id),
                        "expectedVersion": expected_version,
                    },
                )

            record = await repository.update_account(
                workspace_id=actor.workspace_id,
                account_id=account_id,
                expected_version=expected_version,
                update=SocialAccountUpdate(
                    publishing_enabled=request.publishing_enabled,
                    default_settings=default_settings,
                ),
                updated_by=actor.user_id,
            )
            await unit_of_work.flush()

        return SocialAccountMapper.to_dto(record)
