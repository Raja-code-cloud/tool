"""Asset HTTP routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile
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
from cloud_content_hub.api.validators import parse_uuid
from cloud_content_hub.application.assets.commands import (
    DeleteAssetCommand,
    ReplaceAssetCommand,
    UploadAssetCommand,
)
from cloud_content_hub.application.assets.dto.requests import (
    AssetTypeDto,
    ReplaceAssetRequestDto,
    UploadAssetRequestDto,
)
from cloud_content_hub.application.assets.handlers.delete_asset_handler import DeleteAssetHandler
from cloud_content_hub.application.assets.handlers.get_asset_handler import GetAssetHandler
from cloud_content_hub.application.assets.handlers.replace_asset_handler import ReplaceAssetHandler
from cloud_content_hub.application.assets.handlers.search_assets_handler import (
    ListAssetsHandler,
    SearchAssetsHandler,
)
from cloud_content_hub.application.assets.handlers.upload_asset_handler import UploadAssetHandler
from cloud_content_hub.application.assets.interfaces.asset_repository import AssetLifecycleStatus
from cloud_content_hub.application.assets.queries import (
    GetAssetQuery,
    ListAssetsQuery,
    SearchAssetsQuery,
)
from cloud_content_hub.infrastructure.identity.principal import Principal

router = APIRouter(tags=["Assets"])

UploadAssetHandlerDep = Annotated[UploadAssetHandler, Depends(handler_dependency("upload_asset"))]
ListAssetsHandlerDep = Annotated[ListAssetsHandler, Depends(handler_dependency("list_assets"))]
SearchAssetsHandlerDep = Annotated[
    SearchAssetsHandler, Depends(handler_dependency("search_assets"))
]
GetAssetHandlerDep = Annotated[GetAssetHandler, Depends(handler_dependency("get_asset"))]
DeleteAssetHandlerDep = Annotated[DeleteAssetHandler, Depends(handler_dependency("delete_asset"))]
ReplaceAssetHandlerDep = Annotated[
    ReplaceAssetHandler, Depends(handler_dependency("replace_asset"))
]


def _parse_asset_types(values: list[str] | None) -> frozenset[AssetTypeDto]:
    if not values:
        return frozenset()
    return frozenset(AssetTypeDto(value) for value in values)


def _parse_lifecycle_statuses(values: list[str] | None) -> frozenset[AssetLifecycleStatus]:
    if not values:
        return frozenset()
    return frozenset(AssetLifecycleStatus(value) for value in values)


@router.post(
    "/upload",
    operation_id="uploadAsset",
    status_code=202,
    responses={202: {"description": "Upload accepted."}},
)
async def upload_asset(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("assets:write"))],
    idempotency_key: IdempotencyKey,
    handler: UploadAssetHandlerDep,
    asset_type: Annotated[AssetTypeDto, Form(alias="assetType")],
    title: Annotated[str, Form(min_length=1, max_length=300)],
    file: Annotated[UploadFile, File()],
    summary: Annotated[str | None, Form()] = None,
    project_id: Annotated[str | None, Form(alias="projectId")] = None,
    folder_id: Annotated[str | None, Form(alias="folderId")] = None,
    checksum_sha256: Annotated[str | None, Form(alias="checksumSha256")] = None,
) -> JSONResponse:
    payload = await file.read()
    request = UploadAssetRequestDto(
        asset_type=asset_type,
        title=title,
        summary=summary,
        project_id=parse_uuid(project_id, field="projectId") if project_id else None,
        folder_id=parse_uuid(folder_id, field="folderId") if folder_id else None,
        checksum_sha256=checksum_sha256,
        filename=file.filename or "upload.bin",
        content_type=file.content_type or "application/octet-stream",
        content_length=len(payload),
        file_data=payload,
    )
    result = await handler.handle(
        actor,
        UploadAssetCommand(request=request, idempotency_key=idempotency_key),
    )
    body = success(data=result, message="Upload accepted.").model_dump(by_alias=True, mode="json")
    return JSONResponse(
        body,
        status_code=202,
        headers={"Location": f"/api/v1/assets/{result.resource_id or result.id}"},
    )


@router.get("", operation_id="listAssets")
async def list_assets(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("assets:read"))],
    handler: ListAssetsHandlerDep,
    cursor: str | None = None,
    limit: PageLimit = 25,
    asset_type: Annotated[list[str] | None, Query(alias="assetType")] = None,
    lifecycle_status: Annotated[list[str] | None, Query(alias="lifecycleStatus")] = None,
    owner_id: Annotated[str | None, Query(alias="ownerId")] = None,
    project_id: Annotated[str | None, Query(alias="projectId")] = None,
    folder_id: Annotated[str | None, Query(alias="folderId")] = None,
    sort: str = "-updatedAt",
) -> JSONResponse:
    query = ListAssetsQuery(
        asset_types=_parse_asset_types(asset_type),
        lifecycle_statuses=_parse_lifecycle_statuses(lifecycle_status),
        owner_id=parse_uuid(owner_id, field="ownerId") if owner_id else None,
        project_id=parse_uuid(project_id, field="projectId") if project_id else None,
        folder_id=parse_uuid(folder_id, field="folderId") if folder_id else None,
        cursor=cursor,
        limit=limit,
        sort=sort.replace("updatedAt", "updated_at").replace("createdAt", "created_at"),
    )
    page = await handler.handle(actor, query)
    return JSONResponse(
        paged_success(items=page.items, page=page.page, message="Assets retrieved.").model_dump(
            by_alias=True, mode="json"
        )
    )


@router.get("/search", operation_id="searchAssets")
async def search_assets(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("assets:read"))],
    handler: SearchAssetsHandlerDep,
    q: Annotated[str, Query(min_length=2, max_length=200)],
    cursor: str | None = None,
    limit: PageLimit = 25,
    asset_type: Annotated[list[str] | None, Query(alias="assetType")] = None,
    lifecycle_status: Annotated[list[str] | None, Query(alias="lifecycleStatus")] = None,
    sort: str = "relevance",
) -> JSONResponse:
    query = SearchAssetsQuery(
        query=q,
        asset_types=_parse_asset_types(asset_type),
        lifecycle_statuses=_parse_lifecycle_statuses(lifecycle_status),
        cursor=cursor,
        limit=limit,
        sort=sort.replace("-updatedAt", "-updated_at").replace("updatedAt", "updated_at"),
    )
    page = await handler.handle(actor, query)
    return JSONResponse(
        paged_success(
            items=page.items, page=page.page, message="Assets search completed."
        ).model_dump(by_alias=True, mode="json")
    )


@router.get("/{asset_id}", operation_id="getAsset")
async def get_asset(
    asset_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("assets:read"))],
    handler: GetAssetHandlerDep,
) -> JSONResponse:
    result = await handler.handle(actor, GetAssetQuery(asset_id=asset_id))
    return JSONResponse(
        success(data=result, message="Asset retrieved.").model_dump(by_alias=True, mode="json"),
        headers={"ETag": etag_for_version(result.version)},
    )


@router.delete("/{asset_id}", operation_id="deleteAsset", status_code=204)
async def delete_asset(
    asset_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("assets:delete"))],
    if_match: IfMatch,
    handler: DeleteAssetHandlerDep,
) -> Response:
    await handler.handle(
        actor,
        DeleteAssetCommand(asset_id=asset_id, expected_version=if_match),
    )
    return Response(status_code=204)


@router.post(
    "/{asset_id}/replace",
    operation_id="replaceAssetFile",
    status_code=202,
    responses={202: {"description": "Replacement accepted."}},
)
async def replace_asset_file(
    asset_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("assets:write"))],
    if_match: IfMatch,
    idempotency_key: IdempotencyKey,
    handler: ReplaceAssetHandlerDep,
    file: Annotated[UploadFile, File()],
    checksum_sha256: Annotated[str | None, Form(alias="checksumSha256")] = None,
) -> JSONResponse:
    payload = await file.read()
    request = ReplaceAssetRequestDto(
        checksum_sha256=checksum_sha256,
        filename=file.filename or "upload.bin",
        content_type=file.content_type or "application/octet-stream",
        content_length=len(payload),
        file_data=payload,
    )
    result = await handler.handle(
        actor,
        ReplaceAssetCommand(
            asset_id=asset_id,
            expected_version=if_match,
            request=request,
            idempotency_key=idempotency_key,
        ),
    )
    body = success(data=result, message="Replacement accepted.").model_dump(
        by_alias=True, mode="json"
    )
    return JSONResponse(
        body,
        status_code=202,
        headers={"Location": f"/api/v1/assets/{asset_id}"},
    )
