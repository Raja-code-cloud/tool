"""Aggregate v1 API routers."""

from fastapi import APIRouter

from cloud_content_hub.api.routers.v1 import (
    administration,
    analytics,
    assets,
    auth,
    content,
    health,
    notifications,
    publishing,
    scheduler,
    users,
    workspace,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(assets.router, prefix="/assets")
api_router.include_router(content.router, prefix="/content")
api_router.include_router(publishing.router, prefix="/publish")
api_router.include_router(scheduler.router, prefix="/schedule")
api_router.include_router(analytics.router, prefix="/analytics")
api_router.include_router(notifications.router, prefix="/notifications")
api_router.include_router(administration.router, prefix="/admin")
api_router.include_router(users.router, prefix="/users")
api_router.include_router(workspace.router, prefix="/workspace")

root_router = APIRouter()
root_router.include_router(health.router)
root_router.include_router(api_router)

__all__ = ["api_router", "root_router"]
