"""Authentication helpers for end-to-end workflow tests."""

from __future__ import annotations

from uuid import UUID

from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.infrastructure.identity.factory import IdentityFactory
from cloud_content_hub.infrastructure.identity.testing.fixtures import identity_factory

from tests.fixtures.constants import ADMIN_PERMISSIONS, WORKFLOW_PERMISSIONS


def all_permissions() -> frozenset[str]:
    """Return the standard permission bundle used across workflow tests."""

    return WORKFLOW_PERMISSIONS


def workflow_actor(*, user_id: UUID, workspace_id: UUID) -> ActorContext:
    """Build an actor context with workflow permissions."""

    return ActorContext(
        user_id=user_id,
        workspace_id=workspace_id,
        permissions=WORKFLOW_PERMISSIONS,
    )


def admin_actor(*, user_id: UUID, workspace_id: UUID) -> ActorContext:
    """Build an actor context with global admin permissions."""

    return ActorContext(
        user_id=user_id,
        workspace_id=workspace_id,
        permissions=ADMIN_PERMISSIONS,
    )


def issue_access_token(
    *,
    user_id: UUID,
    permissions: frozenset[str] | None = None,
    factory: IdentityFactory | None = None,
) -> str:
    """Issue a signed bearer token for HTTP workflow tests."""

    resolved_factory = factory or identity_factory()
    return resolved_factory.jwt_service.create_access_token(
        str(user_id),
        provider="mock",
        permissions=permissions or WORKFLOW_PERMISSIONS,
    )


def auth_headers(
    *,
    token: str,
    workspace_id: UUID,
    idempotency_key: str | None = None,
) -> dict[str, str]:
    """Build standard authenticated request headers."""

    headers = {
        "Authorization": f"Bearer {token}",
        "X-Workspace-ID": str(workspace_id),
    }
    if idempotency_key is not None:
        headers["Idempotency-Key"] = idempotency_key
    return headers
