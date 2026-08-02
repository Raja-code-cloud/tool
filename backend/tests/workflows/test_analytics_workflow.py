"""End-to-end analytics workflow tests."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from cloud_content_hub.application.analytics.commands import ImportAnalyticsCommand
from cloud_content_hub.application.analytics.dto.requests import (
    ImportAnalyticsRequestDto,
    MetricImportDto,
)
from cloud_content_hub.application.analytics.queries import (
    GetDashboardQuery,
    GetPlatformAnalyticsQuery,
)
from cloud_content_hub.bootstrap.handlers import wire_handlers
from tests.e2e.conftest import WorkflowContext
from tests.fixtures.auth import workflow_actor

pytestmark = pytest.mark.e2e


@pytest.mark.asyncio
async def test_analytics_import_dashboard_and_aggregations(workflow_context: WorkflowContext) -> None:
    """Analytics import → dashboard → aggregations."""

    registry = wire_handlers(workflow_context.container)
    actor = workflow_actor(
        user_id=workflow_context.seed.user_id,
        workspace_id=workflow_context.seed.workspace_id,
    )
    now = datetime.now(tz=UTC)

    # Import handler is worker-only; invoke the underlying application handler directly.
    from cloud_content_hub.application.analytics.handlers.import_analytics_handler import (
        ImportAnalyticsHandler,
    )

    handler = ImportAnalyticsHandler(
        unit_of_work_factory=workflow_context.container.repositories.unit_of_work_factory,
        analytics_repository_factory=workflow_context.container.repositories.analytics_repository_factory,
    )
    result = await handler.handle(
        actor,
        ImportAnalyticsCommand(
            request=ImportAnalyticsRequestDto(
                platform_id=workflow_context.seed.platform_ids["linkedin"],
                period_start=now - timedelta(days=7),
                period_end=now,
                observations=(
                    MetricImportDto(
                        code="linkedin.impressions",
                        value="1500",
                        unit="count",
                    ),
                ),
            ),
            idempotency_key="e2e-analytics-import-0001",
        ),
    )

    assert result.observation_count == 1

    dashboard_handler = registry.resolve("get_analytics_dashboard")
    dashboard = await dashboard_handler.handle(
        actor,
        GetDashboardQuery(
            period_start=now - timedelta(days=7),
            period_end=now,
            platform_ids=frozenset({workflow_context.seed.platform_ids["linkedin"]}),
        ),
    )

    assert dashboard is not None

    platforms_handler = registry.resolve("list_analytics_platforms")
    platforms = await platforms_handler.handle(
        actor,
        GetPlatformAnalyticsQuery(
            period_start=now - timedelta(days=7),
            period_end=now,
            platform_ids=frozenset({workflow_context.seed.platform_ids["linkedin"]}),
        ),
    )

    assert platforms is not None
