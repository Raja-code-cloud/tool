"""Deterministic database seed helpers for end-to-end workflow tests."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from cloud_content_hub.infrastructure.database.enums import (
    AIModelStatus,
    ApprovalState,
    ArticleSourceKind,
    AssetType,
    ConnectionStatus,
    ContentLifecycle,
    ContentVersionOrigin,
    HealthStatus,
    MembershipStatus,
    NotificationCategory,
    OrganizationStatus,
    PermissionRiskLevel,
    PlatformStatus,
    SettingValueType,
    TranscriptStatus,
    UserStatus,
    WorkspaceStatus,
)
from cloud_content_hub.infrastructure.database.models.ai_model import AIModel
from cloud_content_hub.infrastructure.database.models.ai_provider import AIProvider
from cloud_content_hub.infrastructure.database.models.approval_request import ApprovalRequest
from cloud_content_hub.infrastructure.database.models.article import Article
from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
from cloud_content_hub.infrastructure.database.models.content_version import ContentVersion
from cloud_content_hub.infrastructure.database.models.metric_definition import MetricDefinition
from cloud_content_hub.infrastructure.database.models.notification_type import NotificationType
from cloud_content_hub.infrastructure.database.models.organization import Organization
from cloud_content_hub.infrastructure.database.models.permission import Permission
from cloud_content_hub.infrastructure.database.models.poster import Poster
from cloud_content_hub.infrastructure.database.models.publication_target import PublicationTarget
from cloud_content_hub.infrastructure.database.models.role import Role
from cloud_content_hub.infrastructure.database.models.role_permission import RolePermission
from cloud_content_hub.infrastructure.database.models.setting_definition import SettingDefinition
from cloud_content_hub.infrastructure.database.models.social_account import SocialAccount
from cloud_content_hub.infrastructure.database.models.social_platform import SocialPlatform
from cloud_content_hub.infrastructure.database.models.user import User
from cloud_content_hub.infrastructure.database.models.video import Video
from cloud_content_hub.infrastructure.database.models.workspace import Workspace
from cloud_content_hub.infrastructure.database.models.workspace_membership import WorkspaceMembership
from cloud_content_hub.infrastructure.database.enums import ApprovalState as DbApprovalState
from cloud_content_hub.infrastructure.repositories.sqlalchemy.unit_of_work import SqlAlchemyUnitOfWork

from tests.fixtures.constants import PLATFORM_CODES


@dataclass(frozen=True, slots=True)
class E2ESeedBundle:
    """Handles to seeded entities used across workflow tests."""

    organization_id: UUID
    workspace_id: UUID
    user_id: UUID
    membership_id: UUID
    ai_provider_id: UUID
    ai_model_id: UUID
    notification_type_id: UUID
    admin_role_id: UUID
    article_asset_id: UUID
    article_version_id: UUID
    poster_asset_id: UUID
    video_asset_id: UUID
    platform_ids: dict[str, UUID] = field(default_factory=dict)
    social_account_ids: dict[str, UUID] = field(default_factory=dict)
    metric_definition_ids: dict[str, UUID] = field(default_factory=dict)


def _utc_now() -> datetime:
    return datetime.now(tz=UTC)


def _content_hash(text: str) -> bytes:
    return hashlib.sha256(text.encode("utf-8")).digest()


async def seed_e2e_environment(
    session_factory: async_sessionmaker[AsyncSession],
) -> E2ESeedBundle:
    """Seed tenant, catalog, content, and social accounts for workflow tests."""

    organization_id = uuid4()
    workspace_id = uuid4()
    user_id = uuid4()
    membership_id = uuid4()
    ai_provider_id = uuid4()
    ai_model_id = uuid4()
    notification_type_id = uuid4()
    admin_role_id = uuid4()
    article_asset_id = uuid4()
    article_version_id = uuid4()
    poster_asset_id = uuid4()
    video_asset_id = uuid4()
    suffix = uuid4().hex[:8]
    now = _utc_now()

    platform_ids: dict[str, UUID] = {}
    social_account_ids: dict[str, UUID] = {}
    metric_definition_ids: dict[str, UUID] = {}

    async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
        session = unit_of_work.session

        session.add(
            Organization(
                id=organization_id,
                name=f"E2E Org {suffix}",
                slug=f"e2e-org-{suffix}",
                status=OrganizationStatus.ACTIVE,
                created_by=None,
                updated_by=None,
            )
        )
        session.add(
            User(
                id=user_id,
                email=f"e2e-{suffix}@example.test",
                display_name="E2E User",
                status=UserStatus.ACTIVE,
                created_by=None,
                updated_by=None,
            )
        )
        session.add(
            Workspace(
                id=workspace_id,
                organization_id=organization_id,
                name=f"E2E Workspace {suffix}",
                slug=f"e2e-ws-{suffix}",
                status=WorkspaceStatus.ACTIVE,
                created_by=user_id,
                updated_by=user_id,
            )
        )
        session.add(
            WorkspaceMembership(
                id=membership_id,
                workspace_id=workspace_id,
                user_id=user_id,
                status=MembershipStatus.ACTIVE,
                created_by=user_id,
                updated_by=user_id,
            )
        )

        session.add(
            AIProvider(
                id=ai_provider_id,
                code="mock",
                name="Mock AI Provider",
                status="enabled",
                capabilities={"generation": True},
                created_by=user_id,
                updated_by=user_id,
            )
        )
        session.add(
            AIModel(
                id=ai_model_id,
                provider_id=ai_provider_id,
                model_code="mock-gpt",
                display_name="Mock GPT",
                capabilities={"chat": True},
                status=AIModelStatus.ENABLED.value,
                created_by=user_id,
                updated_by=user_id,
            )
        )

        session.add(
            NotificationType(
                id=notification_type_id,
                code="content.approved",
                name="Content Approved",
                description="Content approval notification",
                category=NotificationCategory.TRANSACTIONAL.value,
                default_channels=["in_app"],
                created_by=user_id,
                updated_by=user_id,
            )
        )

        session.add(
            SettingDefinition(
                id=uuid4(),
                key="feature.ai_generation",
                value_type=SettingValueType.BOOLEAN.value,
                allowed_scopes=["global", "workspace"],
                default_value={"value": True},
                description="Enable AI generation",
                created_by=user_id,
                updated_by=user_id,
            )
        )
        session.add(
            SettingDefinition(
                id=uuid4(),
                key="system.maintenance_mode",
                value_type=SettingValueType.BOOLEAN.value,
                allowed_scopes=["global"],
                default_value={"value": False},
                description="Global maintenance mode",
                created_by=user_id,
                updated_by=user_id,
            )
        )

        admin_permission_id = uuid4()
        session.add(
            Permission(
                id=admin_permission_id,
                code="admin:write",
                module="administration",
                description="Admin write access",
                risk_level=PermissionRiskLevel.DESTRUCTIVE.value,
                created_by=user_id,
                updated_by=user_id,
            )
        )
        session.add(
            Role(
                id=admin_role_id,
                code="workspace_admin",
                name="Workspace Admin",
                description="Workspace administrator",
                is_system=False,
                workspace_id=workspace_id,
                created_by=user_id,
                updated_by=user_id,
            )
        )
        session.add(
            RolePermission(
                role_id=admin_role_id,
                permission_id=admin_permission_id,
                workspace_id=workspace_id,
                created_by=user_id,
                updated_by=user_id,
            )
        )

        for code in PLATFORM_CODES:
            platform_id = uuid4()
            platform_ids[code] = platform_id
            session.add(
                SocialPlatform(
                    id=platform_id,
                    code=code,
                    name=code.title(),
                    status=PlatformStatus.ENABLED.value,
                    capability_metadata={"publish": True},
                    created_by=user_id,
                    updated_by=user_id,
                )
            )
            metric_id = uuid4()
            metric_definition_ids[code] = metric_id
            session.add(
                MetricDefinition(
                    id=metric_id,
                    code=f"{code}.impressions",
                    name=f"{code.title()} Impressions",
                    description="Impression count",
                    unit="count",
                    aggregation="sum",
                    value_kind="integer",
                    methodology_version=1,
                    platform_id=platform_id,
                    created_by=user_id,
                    updated_by=user_id,
                )
            )
            account_id = uuid4()
            social_account_ids[code] = account_id
            session.add(
                SocialAccount(
                    id=account_id,
                    workspace_id=workspace_id,
                    platform_id=platform_id,
                    external_account_id=f"ext-{code}-{suffix}",
                    account_name=f"{code}-account",
                    display_name=f"{code.title()} Account",
                    username=f"@{code}-e2e",
                    connection_status=ConnectionStatus.CONNECTED.value,
                    health_status=HealthStatus.HEALTHY.value,
                    publishing_enabled=True,
                    connected_at=now,
                    created_by=user_id,
                    updated_by=user_id,
                )
            )

        session.add(
            ContentAsset(
                id=article_asset_id,
                workspace_id=workspace_id,
                asset_type=AssetType.ARTICLE.value,
                title="Master Article",
                lifecycle_status=ContentLifecycle.ACTIVE.value,
                owner_id=user_id,
                created_by=user_id,
                updated_by=user_id,
            )
        )
        session.add(
            Article(
                workspace_id=workspace_id,
                asset_id=article_asset_id,
                source_kind=ArticleSourceKind.UPLOAD.value,
                language_code="en",
                word_count=120,
                reading_minutes=1,
                created_by=user_id,
                updated_by=user_id,
            )
        )
        session.add(
            ContentVersion(
                id=article_version_id,
                workspace_id=workspace_id,
                asset_id=article_asset_id,
                version_number=1,
                title="Master Article v1",
                body_text="Deterministic master article body for E2E tests.",
                origin=ContentVersionOrigin.USER.value,
                content_hash=_content_hash("master-article-v1"),
                created_at=now,
                updated_at=now,
                created_by=user_id,
                updated_by=user_id,
                version=1,
            )
        )
        session.add(
            ApprovalRequest(
                id=uuid4(),
                workspace_id=workspace_id,
                asset_id=article_asset_id,
                version_id=article_version_id,
                status=ApprovalState.APPROVED.value,
                requested_by=user_id,
                requested_at=now,
                decided_at=now,
                created_by=user_id,
                updated_by=user_id,
            )
        )

        session.add(
            ContentAsset(
                id=poster_asset_id,
                workspace_id=workspace_id,
                asset_type=AssetType.POSTER.value,
                title="Launch Poster",
                lifecycle_status=ContentLifecycle.ACTIVE.value,
                owner_id=user_id,
                created_by=user_id,
                updated_by=user_id,
            )
        )
        session.add(
            Poster(
                workspace_id=workspace_id,
                asset_id=poster_asset_id,
                width=1200,
                height=630,
                aspect_ratio=1.9047619047619047,
                created_by=user_id,
                updated_by=user_id,
            )
        )

        session.add(
            ContentAsset(
                id=video_asset_id,
                workspace_id=workspace_id,
                asset_type=AssetType.VIDEO.value,
                title="Product Video",
                lifecycle_status=ContentLifecycle.ACTIVE.value,
                owner_id=user_id,
                created_by=user_id,
                updated_by=user_id,
            )
        )
        session.add(
            Video(
                workspace_id=workspace_id,
                asset_id=video_asset_id,
                duration_ms=30_000,
                width=1920,
                height=1080,
                transcript_status=TranscriptStatus.NONE.value,
                created_by=user_id,
                updated_by=user_id,
            )
        )

    return E2ESeedBundle(
        organization_id=organization_id,
        workspace_id=workspace_id,
        user_id=user_id,
        membership_id=membership_id,
        ai_provider_id=ai_provider_id,
        ai_model_id=ai_model_id,
        notification_type_id=notification_type_id,
        admin_role_id=admin_role_id,
        article_asset_id=article_asset_id,
        article_version_id=article_version_id,
        poster_asset_id=poster_asset_id,
        video_asset_id=video_asset_id,
        platform_ids=platform_ids,
        social_account_ids=social_account_ids,
        metric_definition_ids=metric_definition_ids,
    )


async def approve_publication_target(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    workspace_id: UUID,
    publication_target_id: UUID,
) -> None:
    """Mark a publication target approved so scheduling validation passes."""

    async with session_factory() as session:
        statement = select(PublicationTarget).where(
            PublicationTarget.id == publication_target_id,
            PublicationTarget.workspace_id == workspace_id,
        )
        target = (await session.scalars(statement)).first()
        if target is None:
            msg = f"Publication target {publication_target_id} was not found."
            raise RuntimeError(msg)
        target.approval_state = DbApprovalState.APPROVED.value
        await session.commit()
