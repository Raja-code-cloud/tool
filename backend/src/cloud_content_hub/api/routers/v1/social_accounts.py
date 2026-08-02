"""Social accounts HTTP routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from cloud_content_hub.api.dependencies import (
    Actor,
    IfMatch,
    handler_dependency,
    require_permission,
)
from cloud_content_hub.api.pagination import PageLimit
from cloud_content_hub.api.responses import etag_for_version, list_success, paged_success, success
from cloud_content_hub.application.shared.dto.base import PagedResultDto
from cloud_content_hub.application.social_accounts.dto.requests import (
    AuthorizeSocialAccountRequestDto,
    ConnectSocialAccountRequestDto,
    UpdateSocialAccountRequestDto,
)
from cloud_content_hub.application.social_accounts.dto.responses import (
    ActivityEventDto,
    AuthorizeSocialAccountResponseDto,
    SocialAccountDto,
    SocialPlatformDto,
)
from cloud_content_hub.application.social_accounts.handlers.authorize_social_account_handler import (
    AuthorizeSocialAccountHandler,
)
from cloud_content_hub.application.social_accounts.handlers.connect_social_account_handler import (
    ConnectSocialAccountHandler,
)
from cloud_content_hub.application.social_accounts.handlers.disconnect_social_account_handler import (
    DisconnectSocialAccountHandler,
)
from cloud_content_hub.application.social_accounts.handlers.list_social_account_activity_handler import (
    ListSocialAccountActivityHandler,
)
from cloud_content_hub.application.social_accounts.handlers.list_social_accounts_handler import (
    ListSocialAccountsHandler,
)
from cloud_content_hub.application.social_accounts.handlers.list_social_platforms_handler import (
    ListSocialPlatformsHandler,
)
from cloud_content_hub.application.social_accounts.handlers.refresh_social_account_handler import (
    RefreshSocialAccountHandler,
)
from cloud_content_hub.application.social_accounts.handlers.update_social_account_handler import (
    UpdateSocialAccountHandler,
)
from cloud_content_hub.infrastructure.identity.principal import Principal

router = APIRouter(tags=["Social Accounts"])

ListSocialAccountsHandlerDep = Annotated[
    ListSocialAccountsHandler, Depends(handler_dependency("list_social_accounts"))
]
ListSocialPlatformsHandlerDep = Annotated[
    ListSocialPlatformsHandler, Depends(handler_dependency("list_social_platforms"))
]
AuthorizeSocialAccountHandlerDep = Annotated[
    AuthorizeSocialAccountHandler, Depends(handler_dependency("authorize_social_account"))
]
ConnectSocialAccountHandlerDep = Annotated[
    ConnectSocialAccountHandler, Depends(handler_dependency("connect_social_account"))
]
DisconnectSocialAccountHandlerDep = Annotated[
    DisconnectSocialAccountHandler, Depends(handler_dependency("disconnect_social_account"))
]
RefreshSocialAccountHandlerDep = Annotated[
    RefreshSocialAccountHandler, Depends(handler_dependency("refresh_social_account"))
]
UpdateSocialAccountHandlerDep = Annotated[
    UpdateSocialAccountHandler, Depends(handler_dependency("update_social_account"))
]
ListSocialAccountActivityHandlerDep = Annotated[
    ListSocialAccountActivityHandler,
    Depends(handler_dependency("list_social_account_activity")),
]


@router.get("", operation_id="listSocialAccounts")
async def list_social_accounts(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("publishing:read"))],
    handler: ListSocialAccountsHandlerDep,
    cursor: str | None = None,
    limit: PageLimit = 25,
    sort: str = "-updatedAt",
) -> JSONResponse:
    query = {
        "cursor": cursor,
        "limit": limit,
        "sort": sort.replace("updatedAt", "updated_at").replace("connectedSince", "connected_at"),
    }
    page: PagedResultDto[SocialAccountDto] = await handler.handle(actor, query)
    return JSONResponse(
        paged_success(
            items=page.items,
            page=page.page,
            message="Social accounts retrieved.",
        ).model_dump(by_alias=True, mode="json")
    )


@router.get("/platforms", operation_id="listSocialPlatforms")
async def list_social_platforms(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("publishing:read"))],
    handler: ListSocialPlatformsHandlerDep,
) -> JSONResponse:
    platforms: tuple[SocialPlatformDto, ...] = await handler.handle(actor)
    return JSONResponse(
        list_success(items=platforms, message="Social platforms retrieved.").model_dump(
            by_alias=True, mode="json"
        )
    )


@router.post("/authorize", operation_id="authorizeSocialAccount")
async def authorize_social_account(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("publishing:write"))],
    handler: AuthorizeSocialAccountHandlerDep,
    body: AuthorizeSocialAccountRequestDto,
) -> JSONResponse:
    result: AuthorizeSocialAccountResponseDto = await handler.handle(actor, body)
    return JSONResponse(
        success(data=result, message="Social account authorization started.").model_dump(
            by_alias=True, mode="json"
        )
    )


@router.post("/connect", operation_id="connectSocialAccount", status_code=201)
async def connect_social_account(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("publishing:write"))],
    handler: ConnectSocialAccountHandlerDep,
    body: ConnectSocialAccountRequestDto,
) -> JSONResponse:
    result: SocialAccountDto = await handler.handle(actor, body)
    return JSONResponse(
        success(data=result, message="Social account connected.").model_dump(
            by_alias=True, mode="json"
        ),
        status_code=201,
        headers={
            "ETag": etag_for_version(result.version),
            "Location": f"/api/v1/social-accounts/{result.id}",
        },
    )


@router.get("/activity", operation_id="listSocialAccountActivity")
async def list_social_account_activity(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("publishing:read"))],
    handler: ListSocialAccountActivityHandlerDep,
    cursor: str | None = None,
    limit: PageLimit = 25,
    sort: str = "-timestamp",
) -> JSONResponse:
    query = {
        "cursor": cursor,
        "limit": limit,
        "sort": sort,
    }
    page: PagedResultDto[ActivityEventDto] = await handler.handle(actor, query)
    return JSONResponse(
        paged_success(
            items=page.items,
            page=page.page,
            message="Social account activity retrieved.",
        ).model_dump(by_alias=True, mode="json")
    )


@router.post("/{account_id}/disconnect", operation_id="disconnectSocialAccount")
async def disconnect_social_account(
    account_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("publishing:write"))],
    handler: DisconnectSocialAccountHandlerDep,
) -> JSONResponse:
    result: SocialAccountDto = await handler.handle(actor, account_id)
    return JSONResponse(
        success(data=result, message="Social account disconnected.").model_dump(
            by_alias=True, mode="json"
        ),
        headers={"ETag": etag_for_version(result.version)},
    )


@router.post("/{account_id}/refresh", operation_id="refreshSocialAccount")
async def refresh_social_account(
    account_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("publishing:write"))],
    handler: RefreshSocialAccountHandlerDep,
) -> JSONResponse:
    result: SocialAccountDto = await handler.handle(actor, account_id)
    return JSONResponse(
        success(data=result, message="Social account refreshed.").model_dump(
            by_alias=True, mode="json"
        ),
        headers={"ETag": etag_for_version(result.version)},
    )


@router.patch("/{account_id}", operation_id="updateSocialAccount")
async def update_social_account(
    account_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("publishing:write"))],
    if_match: IfMatch,
    body: UpdateSocialAccountRequestDto,
    handler: UpdateSocialAccountHandlerDep,
) -> JSONResponse:
    result: SocialAccountDto = await handler.handle(
        actor,
        {
            "account_id": account_id,
            "expected_version": if_match,
            "request": body,
        },
    )
    return JSONResponse(
        success(data=result, message="Social account updated.").model_dump(
            by_alias=True, mode="json"
        ),
        headers={"ETag": etag_for_version(result.version)},
    )
