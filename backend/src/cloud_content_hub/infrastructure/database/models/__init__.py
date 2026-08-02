"""ORM business models."""

from __future__ import annotations

from cloud_content_hub.infrastructure.database.models.activity_log import ActivityLog
from cloud_content_hub.infrastructure.database.models.ai_generation_output import AIGenerationOutput
from cloud_content_hub.infrastructure.database.models.ai_generation_request import (
    AIGenerationRequest,
)
from cloud_content_hub.infrastructure.database.models.ai_model import AIModel
from cloud_content_hub.infrastructure.database.models.ai_prompt_template import AIPromptTemplate
from cloud_content_hub.infrastructure.database.models.ai_provider import AIProvider
from cloud_content_hub.infrastructure.database.models.ai_suggestion import AISuggestion
from cloud_content_hub.infrastructure.database.models.ai_suggestion_action import AISuggestionAction
from cloud_content_hub.infrastructure.database.models.ai_usage_record import AIUsageRecord
from cloud_content_hub.infrastructure.database.models.analytics_snapshot import AnalyticsSnapshot
from cloud_content_hub.infrastructure.database.models.approval_request import ApprovalRequest
from cloud_content_hub.infrastructure.database.models.approval_step import ApprovalStep
from cloud_content_hub.infrastructure.database.models.article import Article
from cloud_content_hub.infrastructure.database.models.asset_category import AssetCategory
from cloud_content_hub.infrastructure.database.models.asset_storage_object import AssetStorageObject
from cloud_content_hub.infrastructure.database.models.asset_tag import AssetTag
from cloud_content_hub.infrastructure.database.models.audit_log import AuditLog
from cloud_content_hub.infrastructure.database.models.background_job import BackgroundJob
from cloud_content_hub.infrastructure.database.models.billing_customer import BillingCustomer
from cloud_content_hub.infrastructure.database.models.billing_event import BillingEvent
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
from cloud_content_hub.infrastructure.database.models.external_identity import ExternalIdentity
from cloud_content_hub.infrastructure.database.models.folder import Folder
from cloud_content_hub.infrastructure.database.models.idempotency_key import IdempotencyKey
from cloud_content_hub.infrastructure.database.models.inbox_message import InboxMessage
from cloud_content_hub.infrastructure.database.models.job_lease import JobLease
from cloud_content_hub.infrastructure.database.models.membership_role import MembershipRole
from cloud_content_hub.infrastructure.database.models.metric_definition import MetricDefinition
from cloud_content_hub.infrastructure.database.models.metric_observation import MetricObservation
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
from cloud_content_hub.infrastructure.database.models.notification_type import NotificationType
from cloud_content_hub.infrastructure.database.models.oauth_token_vault import OAuthTokenVault
from cloud_content_hub.infrastructure.database.models.organization import Organization
from cloud_content_hub.infrastructure.database.models.organization_membership import (
    OrganizationMembership,
)
from cloud_content_hub.infrastructure.database.models.outbox_event import OutboxEvent
from cloud_content_hub.infrastructure.database.models.permission import Permission
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
from cloud_content_hub.infrastructure.database.models.publication_target import PublicationTarget
from cloud_content_hub.infrastructure.database.models.publishing_attempt import PublishingAttempt
from cloud_content_hub.infrastructure.database.models.publishing_job import PublishingJob
from cloud_content_hub.infrastructure.database.models.quota_period import QuotaPeriod
from cloud_content_hub.infrastructure.database.models.quota_policy import QuotaPolicy
from cloud_content_hub.infrastructure.database.models.role import Role
from cloud_content_hub.infrastructure.database.models.role_permission import RolePermission
from cloud_content_hub.infrastructure.database.models.saved_view import SavedView
from cloud_content_hub.infrastructure.database.models.setting import Setting
from cloud_content_hub.infrastructure.database.models.setting_definition import SettingDefinition
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
from cloud_content_hub.infrastructure.database.models.social_platform import SocialPlatform
from cloud_content_hub.infrastructure.database.models.social_platform_capability import (
    SocialPlatformCapability,
)
from cloud_content_hub.infrastructure.database.models.storage_object import StorageObject
from cloud_content_hub.infrastructure.database.models.subscription import Subscription
from cloud_content_hub.infrastructure.database.models.subscription_item import SubscriptionItem
from cloud_content_hub.infrastructure.database.models.tag import Tag
from cloud_content_hub.infrastructure.database.models.thumbnail import Thumbnail
from cloud_content_hub.infrastructure.database.models.usage_dimension import UsageDimension
from cloud_content_hub.infrastructure.database.models.usage_event import UsageEvent
from cloud_content_hub.infrastructure.database.models.user import User
from cloud_content_hub.infrastructure.database.models.user_session import UserSession
from cloud_content_hub.infrastructure.database.models.video import Video
from cloud_content_hub.infrastructure.database.models.webhook_receipt import WebhookReceipt
from cloud_content_hub.infrastructure.database.models.workspace import Workspace
from cloud_content_hub.infrastructure.database.models.workspace_membership import (
    WorkspaceMembership,
)

__all__ = [
    "AIGenerationOutput",
    "AIGenerationRequest",
    "AIModel",
    "AIPromptTemplate",
    "AIProvider",
    "AISuggestion",
    "AISuggestionAction",
    "AIUsageRecord",
    "ActivityLog",
    "AnalyticsSnapshot",
    "ApprovalRequest",
    "ApprovalStep",
    "Article",
    "AssetCategory",
    "AssetStorageObject",
    "AssetTag",
    "AuditLog",
    "BackgroundJob",
    "BillingCustomer",
    "BillingEvent",
    "BrandProfile",
    "Category",
    "Collection",
    "CollectionItem",
    "Comment",
    "ContentAsset",
    "ContentDraft",
    "ContentPerformanceSnapshot",
    "ContentRelation",
    "ContentVersion",
    "DataExport",
    "DeadLetter",
    "ExternalIdentity",
    "Folder",
    "IdempotencyKey",
    "InboxMessage",
    "JobLease",
    "MembershipRole",
    "MetricDefinition",
    "MetricObservation",
    "Notification",
    "NotificationDelivery",
    "NotificationPreference",
    "NotificationTemplate",
    "NotificationType",
    "OAuthTokenVault",
    "Organization",
    "OrganizationMembership",
    "OutboxEvent",
    "Permission",
    "Poster",
    "Project",
    "ProjectMember",
    "Publication",
    "PublicationSchedule",
    "PublicationStatusHistory",
    "PublicationTarget",
    "PublishingAttempt",
    "PublishingJob",
    "QuotaPeriod",
    "QuotaPolicy",
    "Role",
    "RolePermission",
    "SavedView",
    "Setting",
    "SettingDefinition",
    "SocialAccount",
    "SocialAccountPermission",
    "SocialAccountSetting",
    "SocialAccountSnapshot",
    "SocialContentTemplate",
    "SocialPlatform",
    "SocialPlatformCapability",
    "StorageObject",
    "Subscription",
    "SubscriptionItem",
    "Tag",
    "Thumbnail",
    "UsageDimension",
    "UsageEvent",
    "User",
    "UserSession",
    "Video",
    "WebhookReceipt",
    "Workspace",
    "WorkspaceMembership",
]
