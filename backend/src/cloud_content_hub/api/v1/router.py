"""Backward-compatible re-exports for legacy import paths."""

from cloud_content_hub.api.routers.v1.health import router as health_router
from cloud_content_hub.api.routers.v1.router import api_router, root_router

__all__ = ["api_router", "health_router", "root_router"]
