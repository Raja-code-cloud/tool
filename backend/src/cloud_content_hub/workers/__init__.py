"""Cloud Content Hub Celery worker package."""

from __future__ import annotations

from typing import Any

__all__ = ["celery_app"]


def __getattr__(name: str) -> Any:
    if name == "celery_app":
        from cloud_content_hub.workers.celery_app import celery_app

        return celery_app
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
