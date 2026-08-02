"""Begin social account OAuth authorization handler."""

from __future__ import annotations

import secrets
from collections.abc import Callable
from urllib.parse import urlencode

from cloud_content_hub.application.content.interfaces.platforms import ContentPlatform
from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.application.shared.authorization import require_permission
from cloud_content_hub.application.shared.interfaces.unit_of_work import IUnitOfWork
from cloud_content_hub.application.social_accounts.dto.requests import AuthorizeSocialAccountRequestDto
from cloud_content_hub.application.social_accounts.dto.responses import AuthorizeSocialAccountResponseDto
from cloud_content_hub.application.social_accounts.exceptions.social_account_errors import (
    SocialPlatformNotFoundError,
    SocialPlatformUnavailableError,
)
from cloud_content_hub.application.social_accounts.interfaces.social_account_repository import (
    ISocialAccountRepository,
)
from cloud_content_hub.infrastructure.database.enums import PlatformStatus


_SUPPORTED_PLATFORM_CODES = frozenset(platform.value for platform in ContentPlatform)


class AuthorizeSocialAccountHandler:
    """Starts a mock OAuth authorization flow for social platform connection."""

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
        request: AuthorizeSocialAccountRequestDto,
    ) -> AuthorizeSocialAccountResponseDto:
        require_permission(actor, "publishing:write")

        platform_code = request.platform_code.strip().lower()
        if platform_code not in _SUPPORTED_PLATFORM_CODES:
            raise SocialPlatformNotFoundError(
                parameters={"platformCode": platform_code},
            )

        async with self._unit_of_work_factory() as unit_of_work:
            repository = self._social_account_repository_factory(unit_of_work)
            platform = await repository.get_platform_by_code(platform_code)
            if platform is None:
                raise SocialPlatformNotFoundError(
                    parameters={"platformCode": platform_code},
                )
            if platform.status != PlatformStatus.ENABLED.value:
                raise SocialPlatformUnavailableError(
                    parameters={"platformCode": platform_code},
                )

        state = secrets.token_urlsafe(24)
        code_verifier = secrets.token_urlsafe(48)
        mock_code = secrets.token_urlsafe(16)
        query = urlencode(
            {
                "redirect_uri": request.redirect_uri,
                "state": state,
                "code": mock_code,
                "platform": platform_code,
            }
        )
        authorization_url = f"mock://social-oauth/authorize?{query}"

        return AuthorizeSocialAccountResponseDto(
            authorization_url=authorization_url,
            state=state,
            code_verifier=code_verifier,
            platform_code=platform_code,
        )
