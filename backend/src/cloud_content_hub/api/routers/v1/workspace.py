"""Workspace HTTP routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from cloud_content_hub.api.dependencies import (
    Actor,
    IfMatch,
    IdempotencyKey,
    handler_dependency,
    require_permission,
)
from cloud_content_hub.api.responses import etag_for_version, success
from cloud_content_hub.api.schemas.transport import UpdateWorkspaceRequest
from cloud_content_hub.application.administration.commands import UpdateWorkspaceSettingsCommand
from cloud_content_hub.application.administration.dto.requests import UpdateWorkspaceSettingsRequestDto
from cloud_content_hub.application.administration.handlers.get_workspace_handler import (
    GetWorkspaceHandler,
)
from cloud_content_hub.application.administration.handlers.update_workspace_settings_handler import (
    UpdateWorkspaceSettingsHandler,
)
from cloud_content_hub.infrastructure.identity.principal import Principal

router = APIRouter(tags=["Workspace"])

GetWorkspaceHandlerDep = Annotated[
    GetWorkspaceHandler, Depends(handler_dependency("get_workspace"))
]
UpdateWorkspaceSettingsHandlerDep = Annotated[
    UpdateWorkspaceSettingsHandler, Depends(handler_dependency("update_workspace_settings"))
]


@router.get("", operation_id="getWorkspace")
async def get_workspace(
    actor: Actor,
    handler: GetWorkspaceHandlerDep,
) -> JSONResponse:
    result = await handler.handle(actor, workspace_id=actor.workspace_id)
    body = success(data=result, message="Workspace retrieved.").model_dump(
        by_alias=True, mode="json"
    )
    return JSONResponse(body, headers={"ETag": etag_for_version(result.version)})


@router.patch("", operation_id="updateWorkspaceSettings")
async def update_workspace_settings(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("admin:write"))],
    if_match: IfMatch,
    idempotency_key: IdempotencyKey,
    body: UpdateWorkspaceRequest,
    handler: UpdateWorkspaceSettingsHandlerDep,
) -> JSONResponse:
    result = await handler.handle(
        actor,
        UpdateWorkspaceSettingsCommand(
            workspace_id=actor.workspace_id,
            expected_version=if_match,
            request=UpdateWorkspaceSettingsRequestDto(
                name=body.name,
                time_zone=body.time_zone,
                retention_policy_days=body.retention_policy_days,
            ),
            idempotency_key=idempotency_key,
        ),
    )
    response_body = success(data=result, message="Workspace settings updated.").model_dump(
        by_alias=True, mode="json"
    )
    return JSONResponse(response_body, headers={"ETag": etag_for_version(result.version)})
