"""Content HTTP routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
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
from cloud_content_hub.api.schemas.transport import UpdateContentRequest
from cloud_content_hub.application.content.commands import (
    ArchiveContentCommand,
    CreateContentVersionCommand,
    DeleteContentCommand,
    DuplicateContentCommand,
    GenerateContentCommand,
    RegenerateContentCommand,
)
from cloud_content_hub.application.content.dto.requests import (
    CreateContentVersionRequestDto,
    DuplicateContentRequestDto,
    GenerationRequestDto,
    RegenerationRequestDto,
)
from cloud_content_hub.application.content.handlers.archive_content_handler import (
    ArchiveContentHandler,
)
from cloud_content_hub.application.content.handlers.create_content_version_handler import (
    CreateContentVersionHandler,
)
from cloud_content_hub.application.content.handlers.delete_content_handler import (
    DeleteContentHandler,
)
from cloud_content_hub.application.content.handlers.duplicate_content_handler import (
    DuplicateContentHandler,
)
from cloud_content_hub.application.content.handlers.generate_content_handler import (
    GenerateContentHandler,
)
from cloud_content_hub.application.content.handlers.get_content_handler import GetContentHandler
from cloud_content_hub.application.content.handlers.regenerate_content_handler import (
    RegenerateContentHandler,
)
from cloud_content_hub.application.content.handlers.search_content_handler import ListContentHandler
from cloud_content_hub.application.content.interfaces.content_repository import (
    ContentLifecycleStatus,
    ContentOrigin,
)
from cloud_content_hub.application.content.queries import GetContentQuery, ListContentQuery
from cloud_content_hub.core.errors import ValidationError
from cloud_content_hub.infrastructure.identity.principal import Principal

router = APIRouter(tags=["Content"])

GenerateContentHandlerDep = Annotated[
    GenerateContentHandler, Depends(handler_dependency("generate_content"))
]
RegenerateContentHandlerDep = Annotated[
    RegenerateContentHandler, Depends(handler_dependency("regenerate_content"))
]
ListContentHandlerDep = Annotated[ListContentHandler, Depends(handler_dependency("list_content"))]
GetContentHandlerDep = Annotated[GetContentHandler, Depends(handler_dependency("get_content"))]
CreateContentVersionHandlerDep = Annotated[
    CreateContentVersionHandler, Depends(handler_dependency("create_content_version"))
]
DeleteContentHandlerDep = Annotated[
    DeleteContentHandler, Depends(handler_dependency("delete_content"))
]
DuplicateContentHandlerDep = Annotated[
    DuplicateContentHandler, Depends(handler_dependency("duplicate_content"))
]
ArchiveContentHandlerDep = Annotated[
    ArchiveContentHandler, Depends(handler_dependency("archive_content"))
]


def _parse_lifecycle(values: list[str] | None) -> frozenset[ContentLifecycleStatus]:
    if not values:
        return frozenset()
    return frozenset(ContentLifecycleStatus(value) for value in values)


def _parse_origins(values: list[str] | None) -> frozenset[ContentOrigin]:
    if not values:
        return frozenset()
    return frozenset(ContentOrigin(value) for value in values)


@router.post(
    "/generate",
    operation_id="generateContent",
    status_code=202,
    responses={202: {"description": "Generation accepted."}},
)
async def generate_content(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("content:generate"))],
    idempotency_key: IdempotencyKey,
    handler: GenerateContentHandlerDep,
    body: GenerationRequestDto,
) -> JSONResponse:
    result = await handler.handle(
        actor,
        GenerateContentCommand(request=body, idempotency_key=idempotency_key),
    )
    body_json = success(data=result, message="Generation accepted.").model_dump(
        by_alias=True, mode="json"
    )
    return JSONResponse(
        body_json,
        status_code=202,
        headers={"Location": f"/api/v1/content/{result.resource_id or result.id}"},
    )


@router.post(
    "/regenerate",
    operation_id="regenerateContent",
    status_code=202,
    responses={202: {"description": "Regeneration accepted."}},
)
async def regenerate_content(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("content:generate"))],
    idempotency_key: IdempotencyKey,
    handler: RegenerateContentHandlerDep,
    body: RegenerationRequestDto,
) -> JSONResponse:
    result = await handler.handle(
        actor,
        RegenerateContentCommand(request=body, idempotency_key=idempotency_key),
    )
    body_json = success(data=result, message="Regeneration accepted.").model_dump(
        by_alias=True, mode="json"
    )
    return JSONResponse(
        body_json,
        status_code=202,
        headers={"Location": f"/api/v1/content/{result.resource_id or result.id}"},
    )


@router.get("", operation_id="listContent")
async def list_content(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("content:read"))],
    handler: ListContentHandlerDep,
    cursor: str | None = None,
    limit: PageLimit = 25,
    lifecycle_status: Annotated[list[str] | None, Query(alias="lifecycleStatus")] = None,
    origin: Annotated[list[str] | None, Query()] = None,
    sort: str = "-updatedAt",
) -> JSONResponse:
    query = ListContentQuery(
        lifecycle_statuses=_parse_lifecycle(lifecycle_status),
        origins=_parse_origins(origin),
        cursor=cursor,
        limit=limit,
        sort=sort.replace("updatedAt", "updated_at").replace("createdAt", "created_at"),
    )
    page = await handler.handle(actor, query)
    return JSONResponse(
        paged_success(items=page.items, page=page.page, message="Content retrieved.").model_dump(
            by_alias=True, mode="json"
        )
    )


@router.get("/{content_id}", operation_id="getContent")
async def get_content(
    content_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("content:read"))],
    handler: GetContentHandlerDep,
) -> JSONResponse:
    result = await handler.handle(actor, GetContentQuery(content_id=content_id))
    return JSONResponse(
        success(data=result, message="Content retrieved.").model_dump(by_alias=True, mode="json"),
        headers={"ETag": etag_for_version(result.version)},
    )


@router.patch("/{content_id}", operation_id="updateContent")
async def update_content(
    content_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("content:write"))],
    if_match: IfMatch,
    body: UpdateContentRequest,
    handler: CreateContentVersionHandlerDep,
) -> JSONResponse:
    if body.title is None:
        raise ValidationError(detail="title is required when updating content.")
    version_request = CreateContentVersionRequestDto(
        title=body.title,
        body_text=body.body_text,
        body_rich=body.body_rich,
        metadata=body.metadata or {},
    )
    result = await handler.handle(
        actor,
        CreateContentVersionCommand(
            content_id=content_id,
            expected_version=if_match,
            request=version_request,
        ),
    )
    return JSONResponse(
        success(data=result, message="Content updated.").model_dump(by_alias=True, mode="json"),
        headers={"ETag": etag_for_version(result.version)},
    )


@router.delete("/{content_id}", operation_id="deleteContent", status_code=204)
async def delete_content(
    content_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("content:delete"))],
    if_match: IfMatch,
    handler: DeleteContentHandlerDep,
) -> Response:
    await handler.handle(
        actor,
        DeleteContentCommand(content_id=content_id, expected_version=if_match),
    )
    return Response(status_code=204)


@router.post(
    "/{content_id}/duplicate",
    operation_id="duplicateContent",
    status_code=201,
    responses={201: {"description": "Content duplicated."}},
)
async def duplicate_content(
    content_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("content:write"))],
    idempotency_key: IdempotencyKey,
    handler: DuplicateContentHandlerDep,
    body: DuplicateContentRequestDto,
) -> JSONResponse:
    result = await handler.handle(
        actor,
        DuplicateContentCommand(
            content_id=content_id,
            request=body,
            idempotency_key=idempotency_key,
        ),
    )
    body = success(data=result, message="Content duplicated.").model_dump(
        by_alias=True, mode="json"
    )
    return JSONResponse(
        body,
        status_code=201,
        headers={
            "ETag": etag_for_version(result.version),
            "Location": f"/api/v1/content/{result.id}",
        },
    )


@router.post("/{content_id}/archive", operation_id="archiveContent")
async def archive_content(
    content_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("content:write"))],
    if_match: IfMatch,
    handler: ArchiveContentHandlerDep,
) -> JSONResponse:
    result = await handler.handle(
        actor,
        ArchiveContentCommand(content_id=content_id, expected_version=if_match),
    )
    return JSONResponse(
        success(data=result, message="Content archived.").model_dump(by_alias=True, mode="json"),
        headers={"ETag": etag_for_version(result.version)},
    )
