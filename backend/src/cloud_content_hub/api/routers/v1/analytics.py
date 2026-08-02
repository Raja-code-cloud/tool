"""Analytics HTTP routes."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from cloud_content_hub.api.dependencies import Actor, handler_dependency, require_permission
from cloud_content_hub.api.pagination import PageLimit
from cloud_content_hub.api.responses import etag_for_version, list_success, paged_success, success
from cloud_content_hub.api.validators import parse_uuid
from cloud_content_hub.application.analytics.handlers.get_dashboard_handler import (
    GetDashboardHandler,
)
from cloud_content_hub.application.analytics.handlers.get_platform_analytics_handler import (
    GetPlatformAnalyticsHandler,
)
from cloud_content_hub.application.analytics.handlers.get_post_analytics_handler import (
    GetPostAnalyticsHandler,
)
from cloud_content_hub.application.analytics.handlers.get_top_posts_handler import (
    GetTopPostsHandler,
)
from cloud_content_hub.application.analytics.queries import (
    GetDashboardQuery,
    GetPlatformAnalyticsQuery,
    GetPostAnalyticsQuery,
    GetTopPostsQuery,
)
from cloud_content_hub.infrastructure.identity.principal import Principal

router = APIRouter(tags=["Analytics"])

GetDashboardHandlerDep = Annotated[
    GetDashboardHandler, Depends(handler_dependency("get_analytics_dashboard"))
]
ListAnalyticsPostsHandlerDep = Annotated[
    GetTopPostsHandler, Depends(handler_dependency("list_analytics_posts"))
]
ListAnalyticsPlatformsHandlerDep = Annotated[
    GetPlatformAnalyticsHandler, Depends(handler_dependency("list_analytics_platforms"))
]
GetAnalyticsPostHandlerDep = Annotated[
    GetPostAnalyticsHandler, Depends(handler_dependency("get_analytics_post"))
]


@router.get("/dashboard", operation_id="getAnalyticsDashboard")
async def get_analytics_dashboard(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("analytics:read"))],
    handler: GetDashboardHandlerDep,
    period_start: Annotated[datetime, Query(alias="periodStart")],
    period_end: Annotated[datetime, Query(alias="periodEnd")],
    time_zone: Annotated[str, Query(alias="timeZone")] = "UTC",
    metric: Annotated[list[str] | None, Query()] = None,
    platform_id: Annotated[list[str] | None, Query(alias="platformId")] = None,
) -> JSONResponse:
    query = GetDashboardQuery(
        period_start=period_start,
        period_end=period_end,
        time_zone=time_zone,
        metric_codes=frozenset(metric or ()),
        platform_ids=frozenset(
            parse_uuid(value, field="platformId") for value in (platform_id or ())
        ),
    )
    result = await handler.handle(actor, query)
    return JSONResponse(
        success(data=result, message="Dashboard retrieved.").model_dump(by_alias=True, mode="json")
    )


@router.get("/posts", operation_id="listAnalyticsPosts")
async def list_analytics_posts(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("analytics:read"))],
    handler: ListAnalyticsPostsHandlerDep,
    period_start: Annotated[datetime | None, Query(alias="periodStart")] = None,
    period_end: Annotated[datetime | None, Query(alias="periodEnd")] = None,
    cursor: str | None = None,
    limit: PageLimit = 25,
    platform_id: Annotated[list[str] | None, Query(alias="platformId")] = None,
    social_account_id: Annotated[list[str] | None, Query(alias="socialAccountId")] = None,
    sort: str = "-snapshotAt",
) -> JSONResponse:
    now = datetime.now(tz=UTC)
    start = period_start or (now - timedelta(days=30))
    end = period_end or now
    query = GetTopPostsQuery(
        period_start=start,
        period_end=end,
        platform_ids=frozenset(
            parse_uuid(value, field="platformId") for value in (platform_id or ())
        ),
        social_account_ids=frozenset(
            parse_uuid(value, field="socialAccountId") for value in (social_account_id or ())
        ),
        cursor=cursor,
        limit=limit,
        sort=sort.replace("snapshotAt", "snapshot_at").replace("engagementRate", "engagement_rate"),
    )
    page = await handler.handle(actor, query)
    return JSONResponse(
        paged_success(
            items=page.items, page=page.page, message="Post analytics retrieved."
        ).model_dump(by_alias=True, mode="json")
    )


@router.get("/platforms", operation_id="listAnalyticsPlatforms")
async def list_analytics_platforms(
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("analytics:read"))],
    handler: ListAnalyticsPlatformsHandlerDep,
    period_start: Annotated[datetime, Query(alias="periodStart")],
    period_end: Annotated[datetime, Query(alias="periodEnd")],
    platform_id: Annotated[list[str] | None, Query(alias="platformId")] = None,
    metric: Annotated[list[str] | None, Query()] = None,
    sort: str = "platformCode",
) -> JSONResponse:
    query = GetPlatformAnalyticsQuery(
        period_start=period_start,
        period_end=period_end,
        platform_ids=frozenset(
            parse_uuid(value, field="platformId") for value in (platform_id or ())
        ),
        metric_codes=frozenset(metric or ()),
        sort=sort.replace("platformCode", "platform_code"),
    )
    result = await handler.handle(actor, query)
    return JSONResponse(
        list_success(items=result, message="Platform analytics retrieved.").model_dump(
            by_alias=True, mode="json"
        )
    )


@router.get("/post/{content_id}", operation_id="getAnalyticsPost")
async def get_analytics_post(
    content_id: UUID,
    actor: Actor,
    _: Annotated[Principal, Depends(require_permission("analytics:read"))],
    handler: GetAnalyticsPostHandlerDep,
    period_start: Annotated[datetime | None, Query(alias="periodStart")] = None,
    period_end: Annotated[datetime | None, Query(alias="periodEnd")] = None,
    publication_target_id: Annotated[str | None, Query(alias="publicationTargetId")] = None,
    metric: Annotated[list[str] | None, Query()] = None,
) -> JSONResponse:
    now = datetime.now(tz=UTC)
    start = period_start or (now - timedelta(days=30))
    end = period_end or now
    query = GetPostAnalyticsQuery(
        content_id=content_id,
        publication_target_id=(
            parse_uuid(publication_target_id, field="publicationTargetId")
            if publication_target_id
            else None
        ),
        period_start=start,
        period_end=end,
        metric_codes=frozenset(metric or ()),
    )
    result = await handler.handle(actor, query)
    body = success(data=result, message="Post analytics retrieved.").model_dump(
        by_alias=True, mode="json"
    )
    return JSONResponse(body, headers={"ETag": etag_for_version(1)})
