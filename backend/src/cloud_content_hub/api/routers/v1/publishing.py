"""Publishing HTTP routes."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from cloud_content_hub.api.dependencies import (
    Actor,
    IdempotencyKey,
    IfMatch,
    handler_dependency,
    require_permission,
)
from cloud_content_hub.api.pagination import PageLimit
from cloud_content_hub.api.responses import etag_for_version, paged_success, success
from cloud_content_hub.api.schemas.transport import PublicationHistoryItemDto
from cloud_content_hub.application.publishing.commands import (
    CancelPublicationCommand,
    DispatchPublicationCommand,
    PublishContentCommand,
)
from cloud_content_hub.application.publishing.dto.requests import (
    CreatePublicationRequestDto,
    DispatchPublicationRequestDto,
)
from cloud_content_hub.application.publishing.handlers.cancel_publication_handler import (
    CancelPublicationHandler,
)
from cloud_content_hub.application.publishing.handlers.create_publication_handler import (
    CreatePublicationHandler,
)
from cloud_content_hub.application.publishing.handlers.dispatch_publication_handler import (
    DispatchPublicationHandler,
)
from cloud_content_hub.application.shared.dto.base import PagedResultDto
from cloud_content_hub.infrastructure.identity.principal import Principal

router = APIRouter(tags=["Publishing"])

CreatePublicationHandlerDep = Annotated[
    CreatePublicationHandler, Depends(handler_dependency("create_publication"))
]
DispatchPublicationHandlerDep = Annotated[
    DispatchPublicationHandler, Depends(handler_dependency("dispatch_publication"))
]
CancelPublicationHandlerDep = Annotated[
    CancelPublicationHandler, Depends(handler_dependency("cancel_publication"))
]
ListPublicationHistoryHandlerDep = Annotated[
    object, Depends(handler_dependency("list_publication_history"))
]


@router.post(
    "",
    operation_id="createPublication",
    status_code=201,
    responses={201: {"description": "Publication created."}},
)
async def create_publication(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("publishing:write"))],
    idempotency_key: IdempotencyKey,
    handler: CreatePublicationHandlerDep,
    body: CreatePublicationRequestDto,
) -> JSONResponse:
    result = await handler.handle(
        actor,
        PublishContentCommand(request=body, idempotency_key=idempotency_key),
    )
    return JSONResponse(
        success(data=result, message="Publication created.").model_dump(by_alias=True, mode="json"),
        status_code=201,
        headers={
            "ETag": etag_for_version(result.version),
            "Location": f"/api/v1/publish/{result.id}",
        },
    )


@router.post(
    "/{publication_id}",
    operation_id="dispatchPublication",
    status_code=202,
    responses={202: {"description": "Publication dispatch accepted."}},
)
async def dispatch_publication(
    publication_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("publishing:write"))],
    if_match: IfMatch,
    idempotency_key: IdempotencyKey,
    handler: DispatchPublicationHandlerDep,
    body: DispatchPublicationRequestDto | None = None,
) -> JSONResponse:
    request = body or DispatchPublicationRequestDto()
    result = await handler.handle(
        actor,
        DispatchPublicationCommand(
            publication_id=publication_id,
            expected_version=if_match,
            request=request,
            idempotency_key=idempotency_key,
        ),
    )
    return JSONResponse(
        success(data=result, message="Publication dispatch accepted.").model_dump(
            by_alias=True, mode="json"
        ),
        status_code=202,
        headers={"Location": f"/api/v1/publish/{publication_id}"},
    )


@router.get("/history", operation_id="listPublicationHistory")
async def list_publication_history(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("publishing:read"))],
    handler: ListPublicationHistoryHandlerDep,
    cursor: str | None = None,
    limit: PageLimit = 25,
    occurred_after: Annotated[datetime | None, Query(alias="occurredAfter")] = None,
    occurred_before: Annotated[datetime | None, Query(alias="occurredBefore")] = None,
    state: Annotated[list[str] | None, Query()] = None,
    content_id: Annotated[str | None, Query(alias="contentId")] = None,
    platform_id: Annotated[str | None, Query(alias="platformId")] = None,
    social_account_id: Annotated[str | None, Query(alias="socialAccountId")] = None,
    sort: str = "-occurredAt",
) -> JSONResponse:
    from cloud_content_hub.api.validators import parse_uuid

    query = {
        "cursor": cursor,
        "limit": limit,
        "occurred_after": occurred_after,
        "occurred_before": occurred_before,
        "states": frozenset(state or ()),
        "content_id": parse_uuid(content_id, field="contentId") if content_id else None,
        "platform_id": parse_uuid(platform_id, field="platformId") if platform_id else None,
        "social_account_id": (
            parse_uuid(social_account_id, field="socialAccountId") if social_account_id else None
        ),
        "sort": sort.replace("occurredAt", "occurred_at"),
    }
    page: PagedResultDto[PublicationHistoryItemDto] = await handler.handle(actor, query)
    return JSONResponse(
        paged_success(
            items=page.items,
            page=page.page,
            message="Publication history retrieved.",
        ).model_dump(by_alias=True, mode="json")
    )


@router.delete("/{publication_id}", operation_id="cancelPublication")
async def cancel_publication(
    publication_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("publishing:delete"))],
    if_match: IfMatch,
    handler: CancelPublicationHandlerDep,
) -> JSONResponse:
    result = await handler.handle(
        actor,
        CancelPublicationCommand(publication_id=publication_id, expected_version=if_match),
    )
    body = success(data=result, message="Publication cancelled.").model_dump(
        by_alias=True, mode="json"
    )
    return JSONResponse(body, headers={"ETag": etag_for_version(result.version)})
