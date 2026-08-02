"""Publishing Celery tasks."""

from __future__ import annotations

from cloud_content_hub.workers.tasks._registry import register_worker_task


@register_worker_task("cloud_content_hub.tasks.publish_content")
def publish_content(**payload: object) -> None:
    """Create and dispatch a publication."""


@register_worker_task("cloud_content_hub.tasks.retry_publish")
def retry_publish(**payload: object) -> None:
    """Retry a failed publication dispatch."""


@register_worker_task("cloud_content_hub.tasks.cancel_publish")
def cancel_publish(**payload: object) -> None:
    """Cancel an in-flight publication."""


@register_worker_task("cloud_content_hub.tasks.verify_publish_status")
def verify_publish_status(**payload: object) -> None:
    """Verify external publication status."""
