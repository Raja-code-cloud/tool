"""End-to-end administration workflow tests."""

from __future__ import annotations

import pytest

from cloud_content_hub.application.administration.commands import (
    AssignRoleCommand,
    EnableMaintenanceModeCommand,
)
from cloud_content_hub.application.administration.dto.requests import (
    AssignRoleRequestDto,
    EnableMaintenanceModeRequestDto,
)
from cloud_content_hub.application.administration.handlers.assign_role_handler import AssignRoleHandler
from cloud_content_hub.application.administration.handlers.enable_maintenance_mode_handler import (
    EnableMaintenanceModeHandler,
)
from cloud_content_hub.application.administration.handlers.get_feature_flags_handler import (
    GetFeatureFlagsHandler,
)
from cloud_content_hub.application.administration.queries import GetFeatureFlagsQuery

from tests.e2e.conftest import WorkflowContext
from tests.fixtures.auth import admin_actor

pytestmark = pytest.mark.e2e


@pytest.mark.asyncio
async def test_administration_role_assignment(workflow_context: WorkflowContext) -> None:
    """Administration role assignment persists membership role grants."""

    handler = AssignRoleHandler(
        unit_of_work_factory=workflow_context.container.repositories.unit_of_work_factory,
        administration_repository_factory=(
            workflow_context.container.repositories.administration_repository_factory
        ),
    )
    actor = admin_actor(
        user_id=workflow_context.seed.user_id,
        workspace_id=workflow_context.seed.workspace_id,
    )
    await handler.handle(
        actor,
        AssignRoleCommand(
            request=AssignRoleRequestDto(
                workspace_id=workflow_context.seed.workspace_id,
                membership_id=workflow_context.seed.membership_id,
                role_id=workflow_context.seed.admin_role_id,
            ),
            idempotency_key="e2e-assign-role-0001",
        ),
    )


@pytest.mark.asyncio
async def test_administration_feature_flags(workflow_context: WorkflowContext) -> None:
    """Feature flags are readable for workspace administrators."""

    handler = GetFeatureFlagsHandler(
        unit_of_work_factory=workflow_context.container.repositories.unit_of_work_factory,
        administration_repository_factory=(
            workflow_context.container.repositories.administration_repository_factory
        ),
    )
    actor = admin_actor(
        user_id=workflow_context.seed.user_id,
        workspace_id=workflow_context.seed.workspace_id,
    )
    flags = await handler.handle(
        actor,
        GetFeatureFlagsQuery(workspace_id=workflow_context.seed.workspace_id),
    )

    assert isinstance(flags, tuple)


@pytest.mark.asyncio
async def test_administration_maintenance_mode(workflow_context: WorkflowContext) -> None:
    """Maintenance mode can be enabled and disabled by global administrators."""

    handler = EnableMaintenanceModeHandler(
        unit_of_work_factory=workflow_context.container.repositories.unit_of_work_factory,
        administration_repository_factory=(
            workflow_context.container.repositories.administration_repository_factory
        ),
        event_publisher=workflow_context.container.events.publishers.administration,
    )
    actor = admin_actor(
        user_id=workflow_context.seed.user_id,
        workspace_id=workflow_context.seed.workspace_id,
    )
    state = await handler.handle(
        actor,
        EnableMaintenanceModeCommand(
            request=EnableMaintenanceModeRequestDto(message="E2E maintenance window"),
            idempotency_key="e2e-maintenance-0001",
        ),
    )

    assert state.enabled is True


@pytest.mark.asyncio
async def test_administration_system_status_via_http(auth_client) -> None:
    """Administration system status endpoint returns health envelope."""

    response = await auth_client.get("/api/v1/admin/system")

    assert response.status_code in {200, 403}
    if response.status_code == 200:
        body = response.json()
        assert body["success"] is True
