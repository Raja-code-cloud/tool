"""Notifications HTTP routes."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import JSONResponse

from cloud_content_hub.api.dependencies import (
    Actor,
    IfMatch,
    handler_dependency,
    require_permission,
)
from cloud_content_hub.api.pagination import PageLimit
from cloud_content_hub.api.responses import etag_for_version, paged_success, success
from cloud_content_hub.application.notifications.commands import (
    DeleteNotificationCommand,
    MarkNotificationReadCommand,
    UpdatePreferencesCommand,
)
from cloud_content_hub.application.notifications.dto.requests import (
    MarkNotificationReadRequestDto,
    UpdatePreferencesRequestDto,
)
from cloud_content_hub.application.notifications.handlers.delete_notification_handler import (
    DeleteNotificationHandler,
)
from cloud_content_hub.application.notifications.handlers.get_notifications_handler import (
    GetNotificationsHandler,
)
from cloud_content_hub.application.notifications.handlers.get_preferences_handler import (
    GetPreferencesHandler,
)
from cloud_content_hub.application.notifications.handlers.mark_notification_read_handler import (
    MarkNotificationReadHandler,
)
from cloud_content_hub.application.notifications.handlers.update_preferences_handler import (
    UpdatePreferencesHandler,
)
from cloud_content_hub.application.notifications.interfaces.notification_repository import (
    NotificationSeverity,
)
from cloud_content_hub.application.notifications.queries import GetNotificationsQuery, GetPreferencesQuery
from cloud_content_hub.infrastructure.identity.principal import Principal

router = APIRouter(tags=["Notifications"])

ListNotificationsHandlerDep = Annotated[
    GetNotificationsHandler, Depends(handler_dependency("list_notifications"))
]
MarkNotificationReadHandlerDep = Annotated[
    MarkNotificationReadHandler, Depends(handler_dependency("mark_notification_read"))
]
DeleteNotificationHandlerDep = Annotated[
    DeleteNotificationHandler, Depends(handler_dependency("delete_notification"))
]
GetPreferencesHandlerDep = Annotated[
    GetPreferencesHandler, Depends(handler_dependency("get_notification_preferences"))
]
UpdatePreferencesHandlerDep = Annotated[
    UpdatePreferencesHandler, Depends(handler_dependency("update_notification_preferences"))
]


def _parse_severities(values: list[str] | None) -> frozenset[NotificationSeverity]:
    if not values:
        return frozenset()
    return frozenset(NotificationSeverity(value) for value in values)


@router.get("", operation_id="listNotifications")
async def list_notifications(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("notifications:read"))],
    handler: ListNotificationsHandlerDep,
    cursor: str | None = None,
    limit: PageLimit = 25,
    q: str | None = None,
    severity: Annotated[list[str] | None, Query()] = None,
    type_code: Annotated[list[str] | None, Query(alias="typeCode")] = None,
    read: bool | None = None,
    created_after: Annotated[datetime | None, Query(alias="createdAfter")] = None,
    created_before: Annotated[datetime | None, Query(alias="createdBefore")] = None,
    sort: str = "-updatedAt",
) -> JSONResponse:
    query = GetNotificationsQuery(
        query=q,
        severities=_parse_severities(severity),
        type_codes=frozenset(type_code or ()),
        read=read,
        created_after=created_after,
        created_before=created_before,
        cursor=cursor,
        limit=limit,
        sort=sort.replace("updatedAt", "updated_at").replace("createdAt", "created_at"),
    )
    page = await handler.handle(actor, query)
    return JSONResponse(
        paged_success(
            items=page.items, page=page.page, message="Notifications retrieved."
        ).model_dump(by_alias=True, mode="json")
    )


@router.patch("/{notification_id}/read", operation_id="markNotificationRead")
async def mark_notification_read(
    notification_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("notifications:write"))],
    if_match: IfMatch,
    body: MarkNotificationReadRequestDto,
    handler: MarkNotificationReadHandlerDep,
) -> JSONResponse:
    result = await handler.handle(
        actor,
        MarkNotificationReadCommand(
            notification_id=notification_id,
            expected_version=if_match,
            request=body,
        ),
    )
    body = success(data=result, message="Notification updated.").model_dump(
        by_alias=True, mode="json"
    )
    return JSONResponse(body, headers={"ETag": etag_for_version(result.version)})


@router.delete("/{notification_id}", operation_id="deleteNotification", status_code=204)
async def delete_notification(
    notification_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("notifications:delete"))],
    if_match: IfMatch,
    handler: DeleteNotificationHandlerDep,
) -> Response:
    await handler.handle(
        actor,
        DeleteNotificationCommand(notification_id=notification_id, expected_version=if_match),
    )
    return Response(status_code=204)


@router.get("/preferences", operation_id="getNotificationPreferences")
async def get_notification_preferences(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("notifications:read"))],
    handler: GetPreferencesHandlerDep,
) -> JSONResponse:
    preferences = await handler.handle(actor, GetPreferencesQuery())
    return JSONResponse(
        success(data=preferences, message="Notification preferences retrieved.").model_dump(
            by_alias=True, mode="json"
        )
    )


@router.patch("/preferences", operation_id="updateNotificationPreferences")
async def update_notification_preferences(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("notifications:write"))],
    body: UpdatePreferencesRequestDto,
    handler: UpdatePreferencesHandlerDep,
) -> JSONResponse:
    preferences = await handler.handle(
        actor,
        UpdatePreferencesCommand(request=body),
    )
    return JSONResponse(
        success(data=preferences, message="Notification preferences updated.").model_dump(
            by_alias=True, mode="json"
        )
    )
