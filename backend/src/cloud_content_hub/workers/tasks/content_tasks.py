"""Content Celery tasks."""

from __future__ import annotations

from cloud_content_hub.workers.tasks._registry import register_worker_task


@register_worker_task("cloud_content_hub.tasks.generate_content")
def generate_content(**payload: object) -> None:
    """Process an AI content generation background job."""


@register_worker_task("cloud_content_hub.tasks.regenerate_content")
def regenerate_content(**payload: object) -> None:
    """Process an AI content regeneration background job."""


@register_worker_task("cloud_content_hub.tasks.duplicate_content")
def duplicate_content(**payload: object) -> None:
    """Process a content duplication background job."""


@register_worker_task("cloud_content_hub.tasks.archive_content")
def archive_content(**payload: object) -> None:
    """Process a content archival background job."""
