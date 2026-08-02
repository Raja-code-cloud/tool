"""Scheduler HTTP routes."""

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
from cloud_content_hub.api.schemas.transport import UpdateScheduleRequest
from cloud_content_hub.api.validators import parse_uuid
from cloud_content_hub.application.scheduler.commands import (
    CancelScheduleCommand,
    SchedulePublicationCommand,
)
from cloud_content_hub.application.scheduler.dto.requests import ScheduleRequestDto
from cloud_content_hub.application.scheduler.handlers.cancel_schedule_handler import (
    CancelScheduleHandler,
)
from cloud_content_hub.application.scheduler.handlers.create_schedule_handler import (
    CreateScheduleHandler,
)
from cloud_content_hub.application.scheduler.handlers.get_schedule_handler import GetScheduleHandler
from cloud_content_hub.application.scheduler.queries import GetScheduleQuery
from cloud_content_hub.application.shared.dto.base import PagedResultDto
from cloud_content_hub.infrastructure.identity.principal import Principal

router = APIRouter(tags=["Scheduler"])

CreateScheduleHandlerDep = Annotated[
    CreateScheduleHandler, Depends(handler_dependency("create_schedule"))
]
ListSchedulesHandlerDep = Annotated[object, Depends(handler_dependency("list_schedules"))]
GetScheduleHandlerDep = Annotated[GetScheduleHandler, Depends(handler_dependency("get_schedule"))]
UpdateScheduleHandlerDep = Annotated[object, Depends(handler_dependency("update_schedule"))]
CancelScheduleHandlerDep = Annotated[
    CancelScheduleHandler, Depends(handler_dependency("cancel_schedule"))
]


@router.post(
    "",
    operation_id="createSchedule",
    status_code=201,
    responses={201: {"description": "Schedule created."}},
)
async def create_schedule(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("schedule:write"))],
    idempotency_key: IdempotencyKey,
    handler: CreateScheduleHandlerDep,
    body: ScheduleRequestDto,
) -> JSONResponse:
    result = await handler.handle(
        actor,
        SchedulePublicationCommand(request=body, idempotency_key=idempotency_key),
    )
    body = success(data=result, message="Schedule created.").model_dump(by_alias=True, mode="json")
    return JSONResponse(
        body,
        status_code=201,
        headers={
            "ETag": etag_for_version(result.version),
            "Location": f"/api/v1/schedule/{result.id}",
        },
    )


@router.get("", operation_id="listSchedules")
async def list_schedules(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("schedule:read"))],
    handler: ListSchedulesHandlerDep,
    cursor: str | None = None,
    limit: PageLimit = 25,
    state: Annotated[list[str] | None, Query()] = None,
    priority: Annotated[list[str] | None, Query()] = None,
    publication_target_id: Annotated[str | None, Query(alias="publicationTargetId")] = None,
    scheduled_after: Annotated[datetime | None, Query(alias="scheduledAfter")] = None,
    scheduled_before: Annotated[datetime | None, Query(alias="scheduledBefore")] = None,
    sort: str = "-updatedAt",
) -> JSONResponse:
    query = {
        "cursor": cursor,
        "limit": limit,
        "states": frozenset(state or ()),
        "priorities": frozenset(priority or ()),
        "publication_target_id": (
            parse_uuid(publication_target_id, field="publicationTargetId")
            if publication_target_id
            else None
        ),
        "scheduled_after": scheduled_after,
        "scheduled_before": scheduled_before,
        "sort": sort.replace("updatedAt", "updated_at").replace("scheduledFor", "scheduled_for"),
    }
    page: PagedResultDto[object] = await handler.handle(actor, query)
    return JSONResponse(
        paged_success(items=page.items, page=page.page, message="Schedules retrieved.").model_dump(
            by_alias=True, mode="json"
        )
    )


@router.get("/{schedule_id}", operation_id="getSchedule")
async def get_schedule(
    schedule_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("schedule:read"))],
    handler: GetScheduleHandlerDep,
) -> JSONResponse:
    result = await handler.handle(actor, GetScheduleQuery(schedule_id=schedule_id))
    return JSONResponse(
        success(data=result, message="Schedule retrieved.").model_dump(by_alias=True, mode="json"),
        headers={"ETag": etag_for_version(result.version)},
    )


@router.patch("/{schedule_id}", operation_id="updateSchedule")
async def update_schedule(
    schedule_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("schedule:write"))],
    if_match: IfMatch,
    body: UpdateScheduleRequest,
    handler: UpdateScheduleHandlerDep,
) -> JSONResponse:
    command = {
        "schedule_id": schedule_id,
        "expected_version": if_match,
        "request": body,
    }
    result = await handler.handle(actor, command)
    return JSONResponse(
        success(data=result, message="Schedule updated.").model_dump(by_alias=True, mode="json"),
        headers={"ETag": etag_for_version(result.version)},
    )


@router.delete("/{schedule_id}", operation_id="cancelSchedule")
async def cancel_schedule(
    schedule_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("schedule:delete"))],
    if_match: IfMatch,
    handler: CancelScheduleHandlerDep,
) -> JSONResponse:
    result = await handler.handle(
        actor,
        CancelScheduleCommand(schedule_id=schedule_id, expected_version=if_match),
    )
    return JSONResponse(
        success(data=result, message="Schedule cancelled.").model_dump(by_alias=True, mode="json"),
        headers={"ETag": etag_for_version(result.version)},
    )
