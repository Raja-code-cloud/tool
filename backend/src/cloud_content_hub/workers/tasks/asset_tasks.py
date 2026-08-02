"""Asset Celery tasks."""

from __future__ import annotations

from cloud_content_hub.workers.tasks._registry import register_worker_task


@register_worker_task("cloud_content_hub.tasks.upload_asset")
def upload_asset(**payload: object) -> None:
    """Process an asset upload background job."""


@register_worker_task("cloud_content_hub.tasks.replace_asset")
def replace_asset(**payload: object) -> None:
    """Process an asset replacement background job."""


@register_worker_task("cloud_content_hub.tasks.delete_asset")
def delete_asset(**payload: object) -> None:
    """Process an asset deletion background job."""


@register_worker_task("cloud_content_hub.tasks.restore_asset")
def restore_asset(**payload: object) -> None:
    """Process an asset restoration background job."""


@register_worker_task("cloud_content_hub.tasks.virus_scan")
def virus_scan(**payload: object) -> None:
    """Run virus scanning for an uploaded asset."""


@register_worker_task("cloud_content_hub.tasks.metadata_extraction")
def metadata_extraction(**payload: object) -> None:
    """Extract metadata for an uploaded asset."""
