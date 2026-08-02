"""Integration tests for SQLAlchemy repository adapters against PostgreSQL."""

from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cloud_content_hub.application.administration.interfaces.administration_repository import (
    UserSearchCriteria,
)
from cloud_content_hub.application.assets.interfaces.asset_repository import (
    AssetLifecycleStatus,
    AssetSearchCriteria,
    AssetType,
    NewAsset,
)
from cloud_content_hub.application.notifications.interfaces.notification_repository import (
    NewNotification,
    NotificationSearchCriteria,
    NotificationSeverity,
)
from cloud_content_hub.infrastructure.database.enums import NotificationCategory
from cloud_content_hub.infrastructure.database.models.notification_type import NotificationType
from cloud_content_hub.infrastructure.repositories.sqlalchemy.administration_repository import (
    SqlAlchemyAdministrationRepository,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.asset_repository import (
    SqlAlchemyAssetRepository,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.notification_repository import (
    SqlAlchemyNotificationRepository,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.unit_of_work import (
    SqlAlchemyUnitOfWork,
)
from tests.integration.conftest import TenantContext

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_asset_repository_crud_soft_delete_and_workspace_isolation(
    session_factory: async_sessionmaker[AsyncSession],
    tenant: TenantContext,
) -> None:
    other_workspace_id = uuid4()

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        repository = SqlAlchemyAssetRepository(unit_of_work.session)
        created = await repository.create(
            NewAsset(
                workspace_id=tenant.workspace_id,
                asset_type=AssetType.ARTICLE,
                title="Adapter Integration Asset",
                summary="Repository adapter test asset",
                owner_id=tenant.user_id,
                project_id=None,
                folder_id=None,
                created_by=tenant.user_id,
            )
        )
        assert created.title == "Adapter Integration Asset"
        assert created.lifecycle_status is AssetLifecycleStatus.DRAFT

        fetched = await repository.get_by_id(
            workspace_id=tenant.workspace_id,
            asset_id=created.id,
        )
        assert fetched is not None
        assert fetched.id == created.id

        assert (
            await repository.get_by_id(
                workspace_id=other_workspace_id,
                asset_id=created.id,
            )
            is None
        )

        page = await repository.search(
            AssetSearchCriteria(
                workspace_id=tenant.workspace_id,
                query="Integration",
                limit=10,
            )
        )
        assert any(item.id == created.id for item in page.items)

        await repository.soft_delete(
            workspace_id=tenant.workspace_id,
            asset_id=created.id,
            expected_version=created.version,
            updated_by=tenant.user_id,
        )

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        repository = SqlAlchemyAssetRepository(unit_of_work.session)
        assert (
            await repository.get_by_id(
                workspace_id=tenant.workspace_id,
                asset_id=created.id,
            )
            is None
        )
        deleted = await repository.get_deleted_by_id(
            workspace_id=tenant.workspace_id,
            asset_id=created.id,
        )
        assert deleted is not None
        assert deleted.is_deleted is True

        restored = await repository.restore(
            workspace_id=tenant.workspace_id,
            asset_id=created.id,
            expected_version=deleted.version,
            updated_by=tenant.user_id,
        )
        assert restored.is_deleted is False


@pytest.mark.asyncio
async def test_notification_repository_create_search_and_mark_read(
    session_factory: async_sessionmaker[AsyncSession],
    tenant: TenantContext,
) -> None:
    type_code = f"adapter.test.{uuid4().hex[:8]}"

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        session = unit_of_work.session
        session.add(
            NotificationType(
                code=type_code,
                name="Adapter Test Notification",
                description="Integration test notification type",
                category=NotificationCategory.PRODUCT,
                created_by=tenant.user_id,
                updated_by=tenant.user_id,
            )
        )

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        repository = SqlAlchemyNotificationRepository(unit_of_work.session)
        created = await repository.create(
            NewNotification(
                workspace_id=tenant.workspace_id,
                recipient_user_id=tenant.user_id,
                type_code=type_code,
                title="Adapter notification",
                body="Repository adapter integration test",
                severity=NotificationSeverity.INFO,
                resource_type="content_asset",
                resource_id=None,
                dedupe_key=f"adapter-{uuid4()}",
                expires_at=None,
                created_by=tenant.user_id,
            )
        )
        assert created.title == "Adapter notification"
        assert created.read_at is None

        page = await repository.search(
            NotificationSearchCriteria(
                workspace_id=tenant.workspace_id,
                recipient_user_id=tenant.user_id,
                query="Adapter",
                limit=10,
            )
        )
        assert any(item.id == created.id for item in page.items)

        marked = await repository.mark_read(
            workspace_id=tenant.workspace_id,
            notification_id=created.id,
            recipient_user_id=tenant.user_id,
            read=True,
            expected_version=created.version,
            updated_by=tenant.user_id,
        )
        assert marked.read_at is not None


@pytest.mark.asyncio
async def test_administration_repository_lists_workspace_users(
    session_factory: async_sessionmaker[AsyncSession],
    tenant: TenantContext,
) -> None:
    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        repository = SqlAlchemyAdministrationRepository(unit_of_work.session)
        page = await repository.list_users(
            UserSearchCriteria(
                workspace_id=tenant.workspace_id,
                query="Adapter",
                limit=10,
            )
        )
        assert any(user.id == tenant.user_id for user in page.items)

        user = await repository.get_user(tenant.user_id)
        assert user is not None
        assert user.email is not None
        assert user.email.endswith("@example.com")
