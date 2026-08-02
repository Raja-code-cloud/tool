"""Administration HTTP routes."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from cloud_content_hub.api.dependencies import (
    AdminActor,
    handler_dependency,
    require_permission,
)
from cloud_content_hub.api.pagination import PageLimit
from cloud_content_hub.api.responses import list_success, paged_success, success
from cloud_content_hub.api.schemas.transport import JobDto
from cloud_content_hub.api.validators import parse_uuid
from cloud_content_hub.application.administration.handlers.get_provider_health_handler import (
    GetProviderHealthHandler,
)
from cloud_content_hub.application.administration.handlers.get_queue_status_handler import (
    GetQueueStatusHandler,
)
from cloud_content_hub.application.administration.handlers.get_system_status_handler import (
    GetSystemStatusHandler,
)
from cloud_content_hub.application.administration.interfaces.provider_health_port import (
    ProviderOperationalStatus,
    ProviderType,
)
from cloud_content_hub.application.administration.interfaces.queue_status_port import AdminQueueName
from cloud_content_hub.application.administration.queries import (
    GetProviderHealthQuery,
    GetQueueStatusQuery,
    GetSystemStatusQuery,
)
from cloud_content_hub.application.shared.dto.base import PagedResultDto
from cloud_content_hub.infrastructure.identity.principal import Principal

router = APIRouter(tags=["Admin"])

ListAdminJobsHandlerDep = Annotated[object, Depends(handler_dependency("list_admin_jobs"))]
ListAdminQueuesHandlerDep = Annotated[
    GetQueueStatusHandler, Depends(handler_dependency("list_admin_queues"))
]
ListAdminProvidersHandlerDep = Annotated[
    GetProviderHealthHandler, Depends(handler_dependency("list_admin_providers"))
]
GetAdminSystemStatusHandlerDep = Annotated[
    GetSystemStatusHandler, Depends(handler_dependency("get_admin_system_status"))
]


@router.get("/jobs", operation_id="listAdminJobs")
async def list_admin_jobs(
    actor: AdminActor,
    _: Annotated[Principal, Depends(require_permission("admin:read"))],
    handler: ListAdminJobsHandlerDep,
    cursor: str | None = None,
    limit: PageLimit = 25,
    state: Annotated[list[str] | None, Query()] = None,
    queue_name: Annotated[list[str] | None, Query(alias="queueName")] = None,
    job_type: Annotated[str | None, Query(alias="jobType")] = None,
    resource_type: Annotated[str | None, Query(alias="resourceType")] = None,
    resource_id: Annotated[str | None, Query(alias="resourceId")] = None,
    created_after: Annotated[datetime | None, Query(alias="createdAfter")] = None,
    created_before: Annotated[datetime | None, Query(alias="createdBefore")] = None,
    sort: str = "-updatedAt",
) -> JSONResponse:
    query = {
        "workspace_id": actor.workspace_id,
        "cursor": cursor,
        "limit": limit,
        "states": frozenset(state or ()),
        "queue_names": frozenset(queue_name or ()),
        "job_type": job_type,
        "resource_type": resource_type,
        "resource_id": parse_uuid(resource_id, field="resourceId") if resource_id else None,
        "created_after": created_after,
        "created_before": created_before,
        "sort": sort.replace("updatedAt", "updated_at").replace("createdAt", "created_at"),
    }
    page: PagedResultDto[JobDto] = await handler.handle(actor, query)
    return JSONResponse(
        paged_success(items=page.items, page=page.page, message="Jobs retrieved.").model_dump(
            by_alias=True, mode="json"
        )
    )


@router.get("/queues", operation_id="listAdminQueues")
async def list_admin_queues(
    actor: AdminActor,
    _: Annotated[Principal, Depends(require_permission("admin:read"))],
    handler: ListAdminQueuesHandlerDep,
    queue_name: Annotated[list[str] | None, Query(alias="queueName")] = None,
) -> JSONResponse:
    names = frozenset(AdminQueueName(value) for value in (queue_name or ()))
    query = GetQueueStatusQuery(workspace_id=actor.workspace_id, queue_names=names)
    result = await handler.handle(actor, query)
    return JSONResponse(
        list_success(items=result, message="Queue summaries retrieved.").model_dump(
            by_alias=True, mode="json"
        )
    )


@router.get("/providers", operation_id="listAdminProviders")
async def list_admin_providers(
    actor: AdminActor,
    _: Annotated[Principal, Depends(require_permission("admin:read"))],
    handler: ListAdminProvidersHandlerDep,
    provider_type: Annotated[list[str] | None, Query(alias="providerType")] = None,
    status: Annotated[list[str] | None, Query()] = None,
) -> JSONResponse:
    query = GetProviderHealthQuery(
        workspace_id=actor.workspace_id,
        provider_types=frozenset(ProviderType(value) for value in (provider_type or ())),
        statuses=frozenset(
            ProviderOperationalStatus(value) for value in (status or ())
        ),
    )
    result = await handler.handle(actor, query)
    return JSONResponse(
        list_success(items=result, message="Provider statuses retrieved.").model_dump(
            by_alias=True, mode="json"
        )
    )


@router.get("/system", operation_id="getAdminSystemStatus")
async def get_admin_system_status(
    actor: AdminActor,
    _: Annotated[Principal, Depends(require_permission("admin:read"))],
    handler: GetAdminSystemStatusHandlerDep,
) -> JSONResponse:
    result = await handler.handle(actor, GetSystemStatusQuery())
    body = success(data=result, message="System status retrieved.").model_dump(
        by_alias=True, mode="json"
    )
    return JSONResponse(body)
