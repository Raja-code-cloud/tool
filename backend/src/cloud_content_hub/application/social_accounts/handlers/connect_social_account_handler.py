"""Complete social account OAuth connection handler."""

from __future__ import annotations

from collections.abc import Callable

from cloud_content_hub.application.content.interfaces.platforms import ContentPlatform
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.application.social_accounts.dto.requests import ConnectSocialAccountRequestDto
from cloud_content_hub.application.social_accounts.dto.responses import SocialAccountDto
from cloud_content_hub.application.social_accounts.exceptions.social_account_errors import (
    SocialOAuthValidationError,
    SocialPlatformNotFoundError,
    SocialPlatformUnavailableError,
)
from cloud_content_hub.application.social_accounts.interfaces.social_account_repository import (
    ConnectSocialAccountInput,
    ISocialAccountRepository,
)
from cloud_content_hub.application.social_accounts.mappers.social_account_mapper import (
    SocialAccountMapper,
)
from cloud_content_hub.infrastructure.database.enums import PlatformStatus


_SUPPORTED_PLATFORM_CODES = frozenset(platform.value for platform in ContentPlatform)


class ConnectSocialAccountHandler:
    """Completes mock OAuth and creates or refreshes a connected social account."""

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
        request: ConnectSocialAccountRequestDto,
    ) -> SocialAccountDto:
        require_permission(actor, "publishing:write")

        platform_code = request.platform_code.strip().lower()
        if platform_code not in _SUPPORTED_PLATFORM_CODES:
            raise SocialPlatformNotFoundError(parameters={"platformCode": platform_code})
        if not all(
            (
                request.authorization_code.strip(),
                request.code_verifier.strip(),
                request.redirect_uri.strip(),
                request.state.strip(),
            )
        ):
            raise SocialOAuthValidationError(
                detail="authorizationCode, codeVerifier, redirectUri, and state are required.",
            )

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._social_account_repository_factory(unit_of_work)
            platform = await repository.get_platform_by_code(platform_code)
            if platform is None:
                raise SocialPlatformNotFoundError(parameters={"platformCode": platform_code})
            if platform.status != PlatformStatus.ENABLED.value:
                raise SocialPlatformUnavailableError(parameters={"platformCode": platform_code})

            record = await repository.connect_account(
                ConnectSocialAccountInput(
                    workspace_id=actor.workspace_id,
                    platform_code=platform_code,
                    authorization_code=request.authorization_code.strip(),
                    code_verifier=request.code_verifier.strip(),
                    redirect_uri=request.redirect_uri.strip(),
                    state=request.state.strip(),
                    connected_by=actor.user_id,
                )
            )
            await unit_of_work.flush()

        return SocialAccountMapper.to_dto(record)
