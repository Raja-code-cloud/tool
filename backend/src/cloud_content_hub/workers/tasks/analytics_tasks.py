"""Analytics Celery tasks."""

from __future__ import annotations

from cloud_content_hub.workers.tasks._registry import register_worker_task


@register_worker_task("cloud_content_hub.tasks.import_analytics")
def import_analytics(**payload: object) -> None:
    """Import analytics observations."""


@register_worker_task("cloud_content_hub.tasks.refresh_dashboard")
def refresh_dashboard(**payload: object) -> None:
    """Refresh dashboard cache aggregates."""


@register_worker_task("cloud_content_hub.tasks.archive_snapshot")
def archive_snapshot(**payload: object) -> None:
    """Archive an analytics snapshot."""
