"""Locust load-test scenarios for API hot paths.

Run locally:

    locust -f tests/load/locustfile.py --host=http://localhost:8000

Environment variables:

    CCH_PERF_TOKEN       Bearer access token (required for authenticated routes)
    CCH_PERF_WORKSPACE   Workspace UUID (default: 01900000-0000-7000-8000-000000000001)
"""

from __future__ import annotations

import os
from uuid import uuid4

from locust import HttpUser, between, task


def _workspace_header() -> dict[str, str]:
    workspace = os.getenv(
        "CCH_PERF_WORKSPACE",
        "01900000-0000-7000-8000-000000000001",
    )
    return {"X-Workspace-ID": workspace}


def _auth_headers() -> dict[str, str]:
    token = os.getenv("CCH_PERF_TOKEN", "")
    headers = _workspace_header()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    headers["X-Correlation-ID"] = f"locust-{uuid4().hex[:12]}"
    return headers


class HealthUser(HttpUser):
    """Single-user health probe baseline."""

    wait_time = between(0.1, 0.3)

    @task(3)
    def health(self) -> None:
        self.client.get("/health", name="GET /health")

    @task(2)
    def live(self) -> None:
        self.client.get("/live", name="GET /live")

    @task(1)
    def ready(self) -> None:
        self.client.get("/ready", name="GET /ready")


class ApiCrudUser(HttpUser):
    """Authenticated CRUD and search load for 10–100 concurrent users."""

    wait_time = between(0.2, 1.0)

    @task(5)
    def list_assets(self) -> None:
        self.client.get(
            "/api/v1/assets?limit=25",
            headers=_auth_headers(),
            name="GET /api/v1/assets",
        )

    @task(3)
    def search_assets(self) -> None:
        self.client.get(
            "/api/v1/assets/search?q=launch&limit=25",
            headers=_auth_headers(),
            name="GET /api/v1/assets/search",
        )

    @task(4)
    def list_content(self) -> None:
        self.client.get(
            "/api/v1/content?limit=25",
            headers=_auth_headers(),
            name="GET /api/v1/content",
        )

    @task(2)
    def analytics_dashboard(self) -> None:
        self.client.get(
            "/api/v1/analytics/dashboard",
            headers=_auth_headers(),
            name="GET /api/v1/analytics/dashboard",
        )

    @task(1)
    def admin_system(self) -> None:
        self.client.get(
            "/api/v1/admin/system",
            headers=_auth_headers(),
            name="GET /api/v1/admin/system",
        )


class PublishingUser(HttpUser):
    """Bulk publishing and schedule inspection load."""

    wait_time = between(0.5, 2.0)

    @task(3)
    def publication_history(self) -> None:
        self.client.get(
            "/api/v1/publish/history?limit=25",
            headers=_auth_headers(),
            name="GET /api/v1/publish/history",
        )

    @task(2)
    def list_schedules(self) -> None:
        self.client.get(
            "/api/v1/schedule?limit=25",
            headers=_auth_headers(),
            name="GET /api/v1/schedule",
        )

    @task(1)
    def list_notifications(self) -> None:
        self.client.get(
            "/api/v1/notifications?limit=25",
            headers=_auth_headers(),
            name="GET /api/v1/notifications",
        )
