"""Operational workspace tenant root model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, Index, Integer, Text, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import CITEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cloud_content_hub.infrastructure.database.base import Base
from cloud_content_hub.infrastructure.database.constraints import check_in
from cloud_content_hub.infrastructure.database.enums import WorkspaceStatus
from cloud_content_hub.infrastructure.database.mixins import (
    OrganizationMixin,
    UACMixin,
    UUIDPrimaryKeyMixin,
)

if TYPE_CHECKING:
    from cloud_content_hub.infrastructure.database.models.activity_log import ActivityLog
    from cloud_content_hub.infrastructure.database.models.ai_generation_output import (
        AIGenerationOutput,
    )
    from cloud_content_hub.infrastructure.database.models.ai_generation_request import (
        AIGenerationRequest,
    )
    from cloud_content_hub.infrastructure.database.models.ai_prompt_template import AIPromptTemplate
    from cloud_content_hub.infrastructure.database.models.ai_suggestion import AISuggestion
    from cloud_content_hub.infrastructure.database.models.ai_suggestion_action import (
        AISuggestionAction,
    )
    from cloud_content_hub.infrastructure.database.models.ai_usage_record import AIUsageRecord
    from cloud_content_hub.infrastructure.database.models.analytics_snapshot import (
        AnalyticsSnapshot,
    )
    from cloud_content_hub.infrastructure.database.models.approval_request import ApprovalRequest
    from cloud_content_hub.infrastructure.database.models.approval_step import ApprovalStep
    from cloud_content_hub.infrastructure.database.models.article import Article
    from cloud_content_hub.infrastructure.database.models.asset_category import AssetCategory
    from cloud_content_hub.infrastructure.database.models.asset_storage_object import (
        AssetStorageObject,
    )
    from cloud_content_hub.infrastructure.database.models.asset_tag import AssetTag
    from cloud_content_hub.infrastructure.database.models.audit_log import AuditLog
    from cloud_content_hub.infrastructure.database.models.background_job import BackgroundJob
    from cloud_content_hub.infrastructure.database.models.brand_profile import BrandProfile
    from cloud_content_hub.infrastructure.database.models.category import Category
    from cloud_content_hub.infrastructure.database.models.collection import Collection
    from cloud_content_hub.infrastructure.database.models.collection_item import CollectionItem
    from cloud_content_hub.infrastructure.database.models.comment import Comment
    from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
    from cloud_content_hub.infrastructure.database.models.content_draft import ContentDraft
    from cloud_content_hub.infrastructure.database.models.content_performance_snapshot import (
        ContentPerformanceSnapshot,
    )
    from cloud_content_hub.infrastructure.database.models.content_relation import ContentRelation
    from cloud_content_hub.infrastructure.database.models.content_version import ContentVersion
    from cloud_content_hub.infrastructure.database.models.data_export import DataExport
    from cloud_content_hub.infrastructure.database.models.dead_letter import DeadLetter
    from cloud_content_hub.infrastructure.database.models.folder import Folder
    from cloud_content_hub.infrastructure.database.models.idempotency_key import IdempotencyKey
    from cloud_content_hub.infrastructure.database.models.inbox_message import InboxMessage
    from cloud_content_hub.infrastructure.database.models.job_lease import JobLease
    from cloud_content_hub.infrastructure.database.models.membership_role import MembershipRole
    from cloud_content_hub.infrastructure.database.models.metric_observation import (
        MetricObservation,
    )
    from cloud_content_hub.infrastructure.database.models.notification import Notification
    from cloud_content_hub.infrastructure.database.models.notification_delivery import (
        NotificationDelivery,
    )
    from cloud_content_hub.infrastructure.database.models.notification_preference import (
        NotificationPreference,
    )
    from cloud_content_hub.infrastructure.database.models.notification_template import (
        NotificationTemplate,
    )
    from cloud_content_hub.infrastructure.database.models.oauth_token_vault import OAuthTokenVault
    from cloud_content_hub.infrastructure.database.models.organization import Organization
    from cloud_content_hub.infrastructure.database.models.outbox_event import OutboxEvent
    from cloud_content_hub.infrastructure.database.models.poster import Poster
    from cloud_content_hub.infrastructure.database.models.project import Project
    from cloud_content_hub.infrastructure.database.models.project_member import ProjectMember
    from cloud_content_hub.infrastructure.database.models.publication import Publication
    from cloud_content_hub.infrastructure.database.models.publication_schedule import (
        PublicationSchedule,
    )
    from cloud_content_hub.infrastructure.database.models.publication_status_history import (
        PublicationStatusHistory,
    )
    from cloud_content_hub.infrastructure.database.models.publication_target import (
        PublicationTarget,
    )
    from cloud_content_hub.infrastructure.database.models.publishing_attempt import (
        PublishingAttempt,
    )
    from cloud_content_hub.infrastructure.database.models.publishing_job import PublishingJob
    from cloud_content_hub.infrastructure.database.models.quota_period import QuotaPeriod
    from cloud_content_hub.infrastructure.database.models.quota_policy import QuotaPolicy
    from cloud_content_hub.infrastructure.database.models.role import Role
    from cloud_content_hub.infrastructure.database.models.saved_view import SavedView
    from cloud_content_hub.infrastructure.database.models.setting import Setting
    from cloud_content_hub.infrastructure.database.models.social_account import SocialAccount
    from cloud_content_hub.infrastructure.database.models.social_account_permission import (
        SocialAccountPermission,
    )
    from cloud_content_hub.infrastructure.database.models.social_account_setting import (
        SocialAccountSetting,
    )
    from cloud_content_hub.infrastructure.database.models.social_account_snapshot import (
        SocialAccountSnapshot,
    )
    from cloud_content_hub.infrastructure.database.models.social_content_template import (
        SocialContentTemplate,
    )
    from cloud_content_hub.infrastructure.database.models.storage_object import StorageObject
    from cloud_content_hub.infrastructure.database.models.tag import Tag
    from cloud_content_hub.infrastructure.database.models.thumbnail import Thumbnail
    from cloud_content_hub.infrastructure.database.models.usage_event import UsageEvent
    from cloud_content_hub.infrastructure.database.models.video import Video
    from cloud_content_hub.infrastructure.database.models.webhook_receipt import WebhookReceipt
    from cloud_content_hub.infrastructure.database.models.workspace_membership import (
        WorkspaceMembership,
    )


class Workspace(UUIDPrimaryKeyMixin, OrganizationMixin, UACMixin, Base):
    """Operational tenant root and RLS context source under an organization."""

    __tablename__ = "workspaces"
    __table_args__ = (
        CheckConstraint(check_in(WorkspaceStatus, name="status"), name="ck_workspaces__status"),
        CheckConstraint(
            "retention_policy_days IS NULL OR retention_policy_days > 0",
            name="ck_workspaces__retention_policy_days",
        ),
        UniqueConstraint("id", "organization_id", name="uq_workspaces__id_organization_id"),
        Index(
            "uq_workspaces__organization_slug_where_active",
            "organization_id",
            "slug",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
        {"comment": "Operational tenant; application commands must scope here explicitly."},
    )

    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(CITEXT, nullable=False)
    status: Mapped[WorkspaceStatus] = mapped_column(
        Text, nullable=False, server_default=text("'active'")
    )
    time_zone: Mapped[str] = mapped_column(Text, nullable=False, server_default=text("'UTC'"))
    retention_policy_days: Mapped[int | None] = mapped_column(Integer, nullable=True)

    organization: Mapped[Organization] = relationship(
        "Organization", back_populates="workspaces", lazy="raise"
    )
    workspace_memberships: Mapped[list[WorkspaceMembership]] = relationship(
        "WorkspaceMembership", back_populates="workspace", lazy="raise"
    )
    roles: Mapped[list[Role]] = relationship("Role", back_populates="workspace", lazy="raise")
    membership_roles: Mapped[list[MembershipRole]] = relationship(
        "MembershipRole",
        back_populates="workspace",
        lazy="raise",
        overlaps="workspace_membership",
    )
    activity_logs: Mapped[list[ActivityLog]] = relationship(
        "ActivityLog", back_populates="workspace", lazy="raise"
    )
    analytics_snapshots: Mapped[list[AnalyticsSnapshot]] = relationship(
        "AnalyticsSnapshot", back_populates="workspace", lazy="raise"
    )
    audit_logs: Mapped[list[AuditLog]] = relationship(
        "AuditLog", back_populates="workspace", lazy="raise"
    )
    background_jobs: Mapped[list[BackgroundJob]] = relationship(
        "BackgroundJob", back_populates="workspace", lazy="raise"
    )
    content_performance_snapshots: Mapped[list[ContentPerformanceSnapshot]] = relationship(
        "ContentPerformanceSnapshot",
        back_populates="workspace",
        lazy="raise",
        overlaps="content_asset,performance_snapshots,performance_snapshots,publication_target",
    )
    idempotency_keys: Mapped[list[IdempotencyKey]] = relationship(
        "IdempotencyKey", back_populates="workspace", lazy="raise"
    )
    inbox_messages: Mapped[list[InboxMessage]] = relationship(
        "InboxMessage", back_populates="workspace", lazy="raise"
    )
    metric_observations: Mapped[list[MetricObservation]] = relationship(
        "MetricObservation",
        back_populates="workspace",
        lazy="raise",
        overlaps="content_asset,metric_observations,metric_observations,metric_observations,publication_target,social_account",
    )
    outbox_events: Mapped[list[OutboxEvent]] = relationship(
        "OutboxEvent", back_populates="workspace", lazy="raise"
    )
    quota_periods: Mapped[list[QuotaPeriod]] = relationship(
        "QuotaPeriod", back_populates="workspace", lazy="raise"
    )
    quota_policies: Mapped[list[QuotaPolicy]] = relationship(
        "QuotaPolicy", back_populates="workspace", lazy="raise"
    )
    social_account_snapshots: Mapped[list[SocialAccountSnapshot]] = relationship(
        "SocialAccountSnapshot",
        back_populates="workspace",
        lazy="raise",
        overlaps="snapshots,social_account",
    )
    usage_events: Mapped[list[UsageEvent]] = relationship(
        "UsageEvent", back_populates="workspace", lazy="raise"
    )
    webhook_receipts: Mapped[list[WebhookReceipt]] = relationship(
        "WebhookReceipt", back_populates="workspace", lazy="raise"
    )
    projects: Mapped[list[Project]] = relationship(
        "Project", back_populates="workspace", lazy="raise"
    )
    folders: Mapped[list[Folder]] = relationship(
        "Folder", back_populates="workspace", lazy="raise", overlaps="child_folders"
    )
    collections: Mapped[list[Collection]] = relationship(
        "Collection", back_populates="workspace", lazy="raise"
    )
    collection_items: Mapped[list[CollectionItem]] = relationship(
        "CollectionItem",
        back_populates="workspace",
        lazy="raise",
        overlaps="asset,collection,collection_items,items",
    )
    tags: Mapped[list[Tag]] = relationship("Tag", back_populates="workspace", lazy="raise")
    asset_tags: Mapped[list[AssetTag]] = relationship(
        "AssetTag",
        back_populates="workspace",
        lazy="raise",
        overlaps="asset,asset_tags,asset_tags,tag",
    )
    categories: Mapped[list[Category]] = relationship(
        "Category",
        back_populates="workspace",
        lazy="raise",
        overlaps="child_categories",
    )
    asset_categories: Mapped[list[AssetCategory]] = relationship(
        "AssetCategory",
        back_populates="workspace",
        lazy="raise",
        overlaps="asset,asset_categories,asset_categories,category",
    )
    content_assets: Mapped[list[ContentAsset]] = relationship(
        "ContentAsset",
        back_populates="workspace",
        lazy="raise",
        overlaps="content_assets,content_assets,folder,project",
    )
    articles: Mapped[list[Article]] = relationship(
        "Article",
        back_populates="workspace",
        lazy="raise",
        overlaps="article,asset",
    )
    videos: Mapped[list[Video]] = relationship(
        "Video", back_populates="workspace", lazy="raise", overlaps="asset,video"
    )
    posters: Mapped[list[Poster]] = relationship(
        "Poster", back_populates="workspace", lazy="raise", overlaps="asset,poster"
    )
    thumbnails: Mapped[list[Thumbnail]] = relationship(
        "Thumbnail",
        back_populates="workspace",
        lazy="raise",
        overlaps="asset,thumbnail",
    )
    storage_objects: Mapped[list[StorageObject]] = relationship(
        "StorageObject", back_populates="workspace", lazy="raise"
    )
    asset_storage_objects: Mapped[list[AssetStorageObject]] = relationship(
        "AssetStorageObject",
        back_populates="workspace",
        lazy="raise",
        overlaps="asset,asset_links,asset_storage_objects,storage_object",
    )
    content_drafts: Mapped[list[ContentDraft]] = relationship(
        "ContentDraft",
        back_populates="workspace",
        lazy="raise",
        overlaps="asset,base_version,draft,drafts",
    )
    content_versions: Mapped[list[ContentVersion]] = relationship(
        "ContentVersion",
        back_populates="workspace",
        lazy="raise",
        overlaps="asset,derived_versions,versions",
    )
    comments: Mapped[list[Comment]] = relationship(
        "Comment",
        back_populates="workspace",
        lazy="raise",
        overlaps="asset,comments,comments,content_version,replies",
    )
    approval_requests: Mapped[list[ApprovalRequest]] = relationship(
        "ApprovalRequest",
        back_populates="workspace",
        lazy="raise",
        overlaps="approval_requests,approval_requests,asset,content_version",
    )
    approval_steps: Mapped[list[ApprovalStep]] = relationship(
        "ApprovalStep",
        back_populates="workspace",
        lazy="raise",
        overlaps="approval_request,steps",
    )
    saved_views: Mapped[list[SavedView]] = relationship(
        "SavedView", back_populates="workspace", lazy="raise"
    )
    brand_profiles: Mapped[list[BrandProfile]] = relationship(
        "BrandProfile", back_populates="workspace", lazy="raise"
    )
    project_members: Mapped[list[ProjectMember]] = relationship(
        "ProjectMember",
        back_populates="workspace",
        lazy="raise",
        overlaps="members,project",
    )
    content_relations: Mapped[list[ContentRelation]] = relationship(
        "ContentRelation", back_populates="workspace", lazy="raise"
    )

    ai_generation_outputs: Mapped[list[AIGenerationOutput]] = relationship(
        "AIGenerationOutput",
        back_populates="workspace",
        lazy="raise",
        overlaps="ai_generation_outputs,generation_request,materialized_version,outputs",
    )
    ai_generation_requests: Mapped[list[AIGenerationRequest]] = relationship(
        "AIGenerationRequest",
        back_populates="workspace",
        lazy="raise",
        overlaps="ai_generation_requests,ai_generation_requests,asset,generation_requests,prompt_template,source_version",
    )
    ai_prompt_templates: Mapped[list[AIPromptTemplate]] = relationship(
        "AIPromptTemplate", back_populates="workspace", lazy="raise"
    )
    ai_suggestions: Mapped[list[AISuggestion]] = relationship(
        "AISuggestion",
        back_populates="workspace",
        lazy="raise",
        overlaps="ai_suggestions,ai_suggestions,asset,content_version,generation_request,suggestions",
    )
    ai_suggestion_actions: Mapped[list[AISuggestionAction]] = relationship(
        "AISuggestionAction",
        back_populates="workspace",
        lazy="raise",
        overlaps="actions,suggestion",
    )
    ai_usage_records: Mapped[list[AIUsageRecord]] = relationship(
        "AIUsageRecord",
        back_populates="workspace",
        lazy="raise",
        overlaps="generation_request,usage_records",
    )
    data_exports: Mapped[list[DataExport]] = relationship(
        "DataExport", back_populates="workspace", lazy="raise"
    )
    dead_letters: Mapped[list[DeadLetter]] = relationship(
        "DeadLetter", back_populates="workspace", lazy="raise"
    )
    job_leases: Mapped[list[JobLease]] = relationship(
        "JobLease",
        back_populates="workspace",
        lazy="raise",
        overlaps="leases,publishing_job",
    )
    notifications: Mapped[list[Notification]] = relationship(
        "Notification", back_populates="workspace", lazy="raise"
    )
    notification_deliveries: Mapped[list[NotificationDelivery]] = relationship(
        "NotificationDelivery", back_populates="workspace", lazy="raise"
    )
    notification_preferences: Mapped[list[NotificationPreference]] = relationship(
        "NotificationPreference", back_populates="workspace", lazy="raise"
    )
    notification_templates: Mapped[list[NotificationTemplate]] = relationship(
        "NotificationTemplate", back_populates="workspace", lazy="raise"
    )
    oauth_token_vaults: Mapped[list[OAuthTokenVault]] = relationship(
        "OAuthTokenVault",
        back_populates="workspace",
        lazy="raise",
        overlaps="oauth_token_vaults,social_account",
    )
    publications: Mapped[list[Publication]] = relationship(
        "Publication",
        back_populates="workspace",
        lazy="raise",
        overlaps="asset,content_version,publications,publications",
    )
    publication_schedules: Mapped[list[PublicationSchedule]] = relationship(
        "PublicationSchedule",
        back_populates="workspace",
        lazy="raise",
        overlaps="publication_target,schedules",
    )
    publication_status_history: Mapped[list[PublicationStatusHistory]] = relationship(
        "PublicationStatusHistory",
        back_populates="workspace",
        lazy="raise",
        overlaps="job,publication_target,schedule,status_history,status_history,status_history",
    )
    publication_targets: Mapped[list[PublicationTarget]] = relationship(
        "PublicationTarget",
        back_populates="workspace",
        lazy="raise",
        overlaps="content_version,generation_output,publication,publication_targets,publication_targets,publication_targets,social_account,targets",
    )
    publishing_attempts: Mapped[list[PublishingAttempt]] = relationship(
        "PublishingAttempt",
        back_populates="workspace",
        lazy="raise",
        overlaps="attempts,publishing_job",
    )
    publishing_jobs: Mapped[list[PublishingJob]] = relationship(
        "PublishingJob",
        back_populates="workspace",
        lazy="raise",
        overlaps="publication_target,publishing_jobs,publishing_jobs,schedule",
    )
    settings: Mapped[list[Setting]] = relationship(
        "Setting", back_populates="workspace", lazy="raise"
    )
    social_accounts: Mapped[list[SocialAccount]] = relationship(
        "SocialAccount", back_populates="workspace", lazy="raise"
    )
    social_account_permissions: Mapped[list[SocialAccountPermission]] = relationship(
        "SocialAccountPermission",
        back_populates="workspace",
        lazy="raise",
        overlaps="permissions,social_account",
    )
    social_account_settings: Mapped[list[SocialAccountSetting]] = relationship(
        "SocialAccountSetting",
        back_populates="workspace",
        lazy="raise",
        overlaps="account_settings,social_account",
    )
    social_content_templates: Mapped[list[SocialContentTemplate]] = relationship(
        "SocialContentTemplate", back_populates="workspace", lazy="raise"
    )

    def __repr__(self) -> str:
        """Return a safe diagnostic representation."""

        return f"Workspace(id={self.id!r}, slug={self.slug!r}, status={self.status!r})"
