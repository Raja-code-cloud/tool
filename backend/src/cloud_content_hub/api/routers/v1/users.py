"""User profile HTTP routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from cloud_content_hub.api.dependencies import (
    IfMatch,
    ProfileActor,
    handler_dependency,
    require_permission,
)
from cloud_content_hub.api.responses import etag_for_version, success
from cloud_content_hub.api.schemas.transport import UpdateUserRequest, UserDto, UserStatusDto
from cloud_content_hub.application.administration.dto.requests import UpdateUserProfileRequestDto
from cloud_content_hub.application.administration.dto.responses import UserSummaryResponse
from cloud_content_hub.application.administration.handlers.get_user_profile_handler import (
    GetUserProfileHandler,
)
from cloud_content_hub.application.administration.handlers.update_user_profile_handler import (
    UpdateUserProfileCommand,
    UpdateUserProfileHandler,
)
from cloud_content_hub.infrastructure.identity.principal import Principal

router = APIRouter(tags=["Users"])

GetUserProfileHandlerDep = Annotated[
    GetUserProfileHandler, Depends(handler_dependency("get_user_profile"))
]
UpdateUserProfileHandlerDep = Annotated[
    UpdateUserProfileHandler, Depends(handler_dependency("update_user_profile"))
]


def _to_user_dto(profile: UserSummaryResponse) -> UserDto:
    return UserDto(
        id=profile.id,
        version=profile.version,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
        email=profile.email,
        display_name=profile.display_name,
        locale=profile.locale,
        time_zone=profile.time_zone,
        status=UserStatusDto(profile.status.value),
    )


@router.get("/me", operation_id="getUserProfile")
async def get_user_profile(
    actor: ProfileActor,
    _: Annotated[Principal, Depends(require_permission("profile:read"))],
    handler: GetUserProfileHandlerDep,
) -> JSONResponse:
    result = await handler.handle(actor)
    body = success(data=_to_user_dto(result), message="Profile retrieved.").model_dump(
        by_alias=True, mode="json"
    )
    return JSONResponse(body, headers={"ETag": etag_for_version(result.version)})


@router.patch("/me", operation_id="updateUserProfile")
async def update_user_profile(
    actor: ProfileActor,
    _: Annotated[Principal, Depends(require_permission("profile:write"))],
    if_match: IfMatch,
    body: UpdateUserRequest,
    handler: UpdateUserProfileHandlerDep,
) -> JSONResponse:
    result = await handler.handle(
        actor,
        UpdateUserProfileCommand(
            expected_version=if_match,
            request=UpdateUserProfileRequestDto(
                display_name=body.display_name,
                locale=body.locale,
                time_zone=body.time_zone,
                avatar_object_key=body.avatar_object_key,
            ),
        ),
    )
    response_body = success(data=_to_user_dto(result), message="Profile updated.").model_dump(
        by_alias=True, mode="json"
    )
    return JSONResponse(response_body, headers={"ETag": etag_for_version(result.version)})
