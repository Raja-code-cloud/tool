"""Unit tests for worker task routing."""

from __future__ import annotations

from cloud_content_hub.application.shared.interfaces.job_queue import JobQueueName
from cloud_content_hub.workers.routing import (
    build_celery_task_routes,
    list_task_routes,
    resolve_task_route,
)


def test_resolve_task_route_returns_catalog_entry() -> None:
    route = resolve_task_route("cloud_content_hub.tasks.upload_asset")

    assert route.queue == JobQueueName.MEDIA
    assert route.category == "asset"


def test_resolve_task_route_falls_back_to_default_queue() -> None:
    route = resolve_task_route("cloud_content_hub.tasks.unknown_task", default_queue="maintenance")

    assert route.queue == "maintenance"
    assert route.category == "unknown"


def test_build_celery_task_routes_maps_all_catalog_tasks() -> None:
    routes = build_celery_task_routes()
    catalog = list_task_routes()

    assert len(routes) == len(catalog)
    assert routes["cloud_content_hub.tasks.generate_content"] == {"queue": JobQueueName.AI}
    assert routes["cloud_content_hub.deliver_outbox_event"] == {"queue": JobQueueName.MAINTENANCE}


def test_list_task_routes_includes_outbox_delivery_task() -> None:
    names = {route.task_name for route in list_task_routes()}

    assert "cloud_content_hub.deliver_outbox_event" in names
    assert "cloud_content_hub.tasks.cleanup_outbox" in names
