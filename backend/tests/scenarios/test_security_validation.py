"""Security validation scenarios for end-to-end workflows."""

from __future__ import annotations

from uuid import uuid4

import pytest

from cloud_content_hub.application.shared.actor import ActorContext
from cloud_content_hub.bootstrap.handlers import wire_handlers
from cloud_content_hub.core.errors import AuthorizationError
from cloud_content_hub.infrastructure.identity.testing.fixtures import identity_factory
from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import ConcurrencyConflict
from cloud_content_hub.infrastructure.repositories.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork

from tests.e2e.conftest import WorkflowContext
from tests.fixtures.auth import workflow_actor
from tests.fixtures.seed import seed_e2e_environment

pytestmark = pytest.mark.e2e


@pytest.mark.asyncio
async def test_workspace_isolation_rejects_foreign_workspace(
    session_factory,
    workflow_context: WorkflowContext,
) -> None:
    """Workspace isolation prevents cross-tenant reads."""

    foreign = await seed_e2e_environment(session_factory)
    registry = wire_handlers(workflow_context.container)
    handler = registry.resolve("get_asset")
    actor = workflow_actor(
        user_id=workflow_context.seed.user_id,
        workspace_id=workflow_context.seed.workspace_id,
    )

    from cloud_content_hub.application.assets.exceptions.asset_errors import AssetNotFoundError
    from cloud_content_hub.application.assets.queries import GetAssetQuery

    with pytest.raises(AssetNotFoundError):
        await handler.handle(actor, GetAssetQuery(asset_id=foreign.poster_asset_id))


@pytest.mark.asyncio
async def test_permission_enforcement_on_mutations(workflow_context: WorkflowContext) -> None:
    """Permission enforcement blocks publishing without write scope."""

    readonly = ActorContext(
        user_id=workflow_context.seed.user_id,
        workspace_id=workflow_context.seed.workspace_id,
        permissions=frozenset({"publishing:read"}),
    )
    registry = wire_handlers(workflow_context.container)
    handler = registry.resolve("create_publication")

    from cloud_content_hub.application.publishing.commands import PublishContentCommand
    from cloud_content_hub.application.publishing.dto.requests import (
        CreatePublicationRequestDto,
        PublicationTargetRequestDto,
    )

    with pytest.raises(AuthorizationError):
        await handler.handle(
            readonly,
            PublishContentCommand(
                request=CreatePublicationRequestDto(
                    content_id=workflow_context.seed.article_asset_id,
                    content_version_id=workflow_context.seed.article_version_id,
                    title="Forbidden",
                    targets=(
                        PublicationTargetRequestDto(
                            social_account_id=workflow_context.seed.social_account_ids["linkedin"],
                        ),
                    ),
                ),
                idempotency_key="e2e-security-publish",
            ),
        )


@pytest.mark.asyncio
async def test_jwt_validation_rejects_expired_or_invalid_signature() -> None:
    """JWT validation rejects invalid signatures."""

    factory = identity_factory()
    token = factory.jwt_service.create_access_token(
        "user",
        provider="mock",
        permissions=frozenset({"profile:read"}),
    )

    with pytest.raises(Exception):
        await factory.jwt_service.decode_and_verify(f"{token}invalid")


@pytest.mark.asyncio
async def test_oauth_validation_requires_matching_state() -> None:
    """OAuth validation requires matching authorization state."""

    from cloud_content_hub.infrastructure.identity.testing.fixtures import identity_factory

    factory = identity_factory()
    provider = factory.build_registry().get("mock")
    auth = await provider.authenticate("http://localhost:3000/callback")
    code = provider.issue_mock_code("security-user")  # type: ignore[attr-defined]

    with pytest.raises(Exception):
        await provider.exchange_code(
            code,
            "http://localhost:3000/callback",
            state=auth.state,
            expected_state="mismatch",
            nonce=auth.nonce,
            code_verifier=auth.code_verifier,
        )


@pytest.mark.asyncio
async def test_soft_delete_hides_removed_rows(session_factory, workflow_context: WorkflowContext) -> None:
    """Soft-deleted rows are not visible to workspace-scoped queries."""

    from cloud_content_hub.infrastructure.database.enums import AssetType, ContentLifecycle
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.repositories.sqlalchemy.base import SqlAlchemyRepository
    from cloud_content_hub.infrastructure.repositories.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork
    from sqlalchemy import select

    asset_id = uuid4()
    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        unit_of_work.session.add(
            ContentAsset(
                id=asset_id,
                workspace_id=workflow_context.seed.workspace_id,
                asset_type=AssetType.POSTER.value,
                title="Disposable Poster",
                lifecycle_status=ContentLifecycle.ACTIVE.value,
                owner_id=workflow_context.seed.user_id,
                created_by=workflow_context.seed.user_id,
                updated_by=workflow_context.seed.user_id,
            )
        )

    async with session_factory() as session:
        row = (
            await session.scalars(
                select(ContentAsset).where(
                    ContentAsset.id == asset_id,
                    ContentAsset.workspace_id == workflow_context.seed.workspace_id,
                    ContentAsset.deleted_at.is_(None),
                )
            )
        ).first()
        assert row is not None

        async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
            repository = SqlAlchemyRepository(
                unit_of_work.session,
                ContentAsset,
                workspace_scoped=True,
            )
            await repository.soft_delete(
                asset_id,
                expected_version=row.version,
                workspace_id=workflow_context.seed.workspace_id,
            )

    async with session_factory() as session:
        hidden = (
            await session.scalars(
                select(ContentAsset).where(
                    ContentAsset.id == asset_id,
                    ContentAsset.workspace_id == workflow_context.seed.workspace_id,
                    ContentAsset.deleted_at.is_(None),
                )
            )
        ).first()
        assert hidden is None


@pytest.mark.asyncio
async def test_optimistic_locking_detects_version_conflict(session_factory) -> None:
    """Optimistic locking rejects stale version updates."""

    from tests.integration.conftest import TenantContext
    from cloud_content_hub.infrastructure.database.models.organization import Organization
    from cloud_content_hub.infrastructure.database.enums import OrganizationStatus, UserStatus, WorkspaceStatus, MembershipStatus
    from cloud_content_hub.infrastructure.database.models.user import User
    from cloud_content_hub.infrastructure.database.models.workspace import Workspace
    from cloud_content_hub.infrastructure.database.models.workspace_membership import WorkspaceMembership
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.enums import AssetType, ContentLifecycle
    from cloud_content_hub.infrastructure.repositories.sqlalchemy.base import SqlAlchemyRepository

    org_id = uuid4()
    ws_id = uuid4()
    user_id = uuid4()

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        session = unit_of_work.session
        session.add(
            Organization(
                id=org_id,
                name="Lock Org",
                slug="lock-org",
                status=OrganizationStatus.ACTIVE,
            )
        )
        session.add(User(id=user_id, email="lock@example.test", display_name="Lock", status=UserStatus.ACTIVE))
        session.add(
            Workspace(
                id=ws_id,
                organization_id=org_id,
                name="Lock WS",
                slug="lock-ws",
                status=WorkspaceStatus.ACTIVE,
                created_by=user_id,
                updated_by=user_id,
            )
        )
        session.add(
            WorkspaceMembership(
                id=uuid4(),
                workspace_id=ws_id,
                user_id=user_id,
                status=MembershipStatus.ACTIVE,
                created_by=user_id,
                updated_by=user_id,
            )
        )
        asset_id = uuid4()
        session.add(
            ContentAsset(
                id=asset_id,
                workspace_id=ws_id,
                asset_type=AssetType.POSTER.value,
                title="Lock Asset",
                lifecycle_status=ContentLifecycle.ACTIVE.value,
                owner_id=user_id,
                created_by=user_id,
                updated_by=user_id,
            )
        )

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        repository = SqlAlchemyRepository(
            unit_of_work.session,
            ContentAsset,
            workspace_scoped=True,
        )
        asset = await repository.get_by_id(asset_id, workspace_id=ws_id)
        assert asset is not None
        asset.title = "Updated"
        await repository.update(asset, expected_version=asset.version)

    with pytest.raises(ConcurrencyConflict):
        async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
            repository = SqlAlchemyRepository(
                unit_of_work.session,
                ContentAsset,
                workspace_scoped=True,
            )
            stale = await repository.get_by_id(asset_id, workspace_id=ws_id)
            assert stale is not None
            stale.title = "Stale"
            await repository.update(stale, expected_version=1)


@pytest.mark.asyncio
async def test_http_if_match_required_for_versioned_delete(auth_client, workflow_context: WorkflowContext) -> None:
    """Versioned deletes require If-Match for optimistic concurrency."""

    response = await auth_client.delete(f"/api/v1/assets/{workflow_context.seed.poster_asset_id}")

    assert response.status_code in {400, 404, 409, 412}
