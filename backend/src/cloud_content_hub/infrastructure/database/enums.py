"""Central Python vocabulary for stable text-backed database states.

Models must persist these values with ``Text`` plus named ``CHECK``
constraints. They must not map these classes with SQLAlchemy ``Enum`` because
the database design intentionally prohibits PostgreSQL enum types.
"""

from enum import StrEnum


class DatabaseTextEnum(StrEnum):
    """Base for lowercase values stored as constrained database text."""

    @classmethod
    def values(cls) -> tuple[str, ...]:
        """Return values in declaration order for deterministic checks."""

        return tuple(member.value for member in cls)


class AssetType(DatabaseTextEnum):
    """Supported first-class content asset subtypes."""

    ARTICLE = "article"
    VIDEO = "video"
    POSTER = "poster"
    THUMBNAIL = "thumbnail"


class ContentLifecycle(DatabaseTextEnum):
    """Content lifecycle independent of publishing workflows."""

    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class UserStatus(DatabaseTextEnum):
    """Global user account states."""

    ACTIVE = "active"
    DISABLED = "disabled"
    ANONYMIZED = "anonymized"


class OrganizationStatus(DatabaseTextEnum):
    """Commercial organization lifecycle states."""

    TRIAL = "trial"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class OrganizationRole(DatabaseTextEnum):
    """Organization membership roles."""

    OWNER = "owner"
    BILLING_ADMIN = "billing_admin"
    ADMIN = "admin"
    MEMBER = "member"


class MembershipStatus(DatabaseTextEnum):
    """Invitation and membership states."""

    INVITED = "invited"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class WorkspaceStatus(DatabaseTextEnum):
    """Operational workspace lifecycle states."""

    PROVISIONING = "provisioning"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSING = "closing"
    CLOSED = "closed"


class PermissionRiskLevel(DatabaseTextEnum):
    """Permission risk classification."""

    NORMAL = "normal"
    SENSITIVE = "sensitive"
    DESTRUCTIVE = "destructive"


class ProjectStatus(DatabaseTextEnum):
    """Project lifecycle states."""

    ACTIVE = "active"
    ARCHIVED = "archived"


class CollectionVisibility(DatabaseTextEnum):
    """Collection visibility scopes."""

    PRIVATE = "private"
    WORKSPACE = "workspace"


class ArticleSourceKind(DatabaseTextEnum):
    """Article content origin."""

    COMPOSE = "compose"
    PASTE = "paste"
    IMPORT = "import"
    UPLOAD = "upload"


class TranscriptStatus(DatabaseTextEnum):
    """Video transcript pipeline states."""

    NONE = "none"
    PENDING = "pending"
    READY = "ready"
    FAILED = "failed"


class StorageObjectPurpose(DatabaseTextEnum):
    """Asset blob attachment purposes."""

    SOURCE = "source"
    RENDITION = "rendition"
    POSTER = "poster"
    THUMBNAIL = "thumbnail"
    TRANSCRIPT = "transcript"
    CAPTION = "caption"
    ATTACHMENT = "attachment"


class ContentVersionOrigin(DatabaseTextEnum):
    """Immutable content version provenance."""

    USER = "user"
    AI = "ai"
    IMPORT = "import"
    REGENERATION = "regeneration"


class SavedViewType(DatabaseTextEnum):
    """Persisted filter view kinds."""

    CONTENT = "content"
    CALENDAR = "calendar"
    ANALYTICS = "analytics"
    ACTIVITY = "activity"


class ProjectRole(DatabaseTextEnum):
    """Project-level responsibility roles."""

    OWNER = "owner"
    EDITOR = "editor"
    REVIEWER = "reviewer"
    VIEWER = "viewer"


class ContentRelationType(DatabaseTextEnum):
    """Typed links among content assets."""

    THUMBNAIL_FOR = "thumbnail_for"
    POSTER_FOR = "poster_for"
    DERIVED_FROM = "derived_from"
    TRANSLATION_OF = "translation_of"
    RELATED_TO = "related_to"


class AIProviderStatus(DatabaseTextEnum):
    """Global AI provider catalog states."""

    ENABLED = "enabled"
    DISABLED = "disabled"
    DEGRADED = "degraded"


class AIModelStatus(DatabaseTextEnum):
    """Global AI model catalog states."""

    ENABLED = "enabled"
    DISABLED = "disabled"
    DEPRECATED = "deprecated"


class AIGenerationStatus(DatabaseTextEnum):
    """AI generation request pipeline states."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AIGenerationScope(DatabaseTextEnum):
    """AI generation request scopes."""

    WHOLE = "whole"
    SELECTION = "selection"
    HEADLINE = "headline"
    CTA = "cta"
    HASHTAGS = "hashtags"
    TONE = "tone"
    PLATFORM_VARIANT = "platform_variant"


class AISafetyStatus(DatabaseTextEnum):
    """Generated output safety screening states."""

    UNCHECKED = "unchecked"
    PASSED = "passed"
    FLAGGED = "flagged"
    BLOCKED = "blocked"


class AISuggestionCategory(DatabaseTextEnum):
    """AI suggestion categories."""

    GRAMMAR = "grammar"
    SEO = "seo"
    ENGAGEMENT = "engagement"
    READABILITY = "readability"
    TIMING = "timing"
    WARNING = "warning"


class AISuggestionStatus(DatabaseTextEnum):
    """AI suggestion lifecycle states."""

    OPEN = "open"
    ACCEPTED = "accepted"
    DISMISSED = "dismissed"
    EXPIRED = "expired"


class AISuggestionAction(DatabaseTextEnum):
    """Immutable AI suggestion decision actions."""

    ACCEPTED = "accepted"
    DISMISSED = "dismissed"
    REOPENED = "reopened"
    APPLIED = "applied"


class PlatformStatus(DatabaseTextEnum):
    """Social platform catalog states."""

    ENABLED = "enabled"
    DISABLED = "disabled"
    COMING_SOON = "coming_soon"


class OAuthTokenStatus(DatabaseTextEnum):
    """OAuth token vault lifecycle states."""

    ACTIVE = "active"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    RENEW_REQUIRED = "renew_required"
    REVOKED = "revoked"


class PublicationStatus(DatabaseTextEnum):
    """Publication aggregate workflow states."""

    DRAFT = "draft"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PARTIALLY_FAILED = "partially_failed"
    CANCELLED = "cancelled"


class ApprovalState(DatabaseTextEnum):
    """Approval request and target decisions."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"
    CANCELLED = "cancelled"


class ApprovalStepState(DatabaseTextEnum):
    """Per-reviewer approval step decisions."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"
    SKIPPED = "skipped"


class ScheduleState(DatabaseTextEnum):
    """Publication scheduling workflow states."""

    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PAUSED = "paused"
    DISPATCHED = "dispatched"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class SchedulePriority(DatabaseTextEnum):
    """Publication schedule dispatch priorities."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class ScheduleAmbiguityPolicy(DatabaseTextEnum):
    """Local-time ambiguity resolution policies."""

    REJECT = "reject"
    EARLIER = "earlier"
    LATER = "later"


class JobState(DatabaseTextEnum):
    """Durable background and publishing job states."""

    QUEUED = "queued"
    LEASED = "leased"
    RUNNING = "running"
    RETRY_WAIT = "retry_wait"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    DEAD_LETTERED = "dead_lettered"
    CANCELLED = "cancelled"


class PublishingAttemptOutcome(DatabaseTextEnum):
    """Immutable publishing provider attempt outcomes."""

    SUCCEEDED = "succeeded"
    TRANSIENT_FAILURE = "transient_failure"
    PERMANENT_FAILURE = "permanent_failure"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class PublicationStatusHistoryType(DatabaseTextEnum):
    """Publication status timeline state categories."""

    APPROVAL = "approval"
    SCHEDULE = "schedule"
    JOB = "job"
    PROVIDER = "provider"


class DeadLetterSourceType(DatabaseTextEnum):
    """Dead-letter queue source kinds."""

    PUBLISHING_JOB = "publishing_job"
    NOTIFICATION = "notification"
    OUTBOX = "outbox"
    WEBHOOK = "webhook"
    BACKGROUND_JOB = "background_job"


class DeadLetterReplayState(DatabaseTextEnum):
    """Dead-letter replay workflow states."""

    PENDING = "pending"
    REPLAYED = "replayed"
    DISCARDED = "discarded"


class ConnectionStatus(DatabaseTextEnum):
    """External account connection states."""

    CONNECTED = "connected"
    DISCONNECTED = "disconnected"


class HealthStatus(DatabaseTextEnum):
    """External account health states."""

    HEALTHY = "healthy"
    WARNING = "warning"
    ERROR = "error"
    NEEDS_REAUTH = "needs_reauth"


class ScanStatus(DatabaseTextEnum):
    """Stored-object malware scanning states."""

    PENDING = "pending"
    CLEAN = "clean"
    INFECTED = "infected"
    FAILED = "failed"


class NotificationCategory(DatabaseTextEnum):
    """Notification type categories."""

    TRANSACTIONAL = "transactional"
    PRODUCT = "product"
    SECURITY = "security"


class NotificationChannel(DatabaseTextEnum):
    """Supported notification delivery channels."""

    IN_APP = "in_app"
    EMAIL = "email"
    WEBHOOK = "webhook"


class NotificationSeverity(DatabaseTextEnum):
    """User-visible notification severities."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class NotificationDeliveryStatus(DatabaseTextEnum):
    """Per-channel notification delivery states."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    SUPPRESSED = "suppressed"


class SettingValueType(DatabaseTextEnum):
    """Typed setting definition value kinds."""

    BOOLEAN = "boolean"
    INTEGER = "integer"
    DECIMAL = "decimal"
    STRING = "string"
    STRING_LIST = "string_list"
    OBJECT = "object"


class SettingScopeType(DatabaseTextEnum):
    """Scoped setting inheritance targets."""

    ORGANIZATION = "organization"
    WORKSPACE = "workspace"
    USER = "user"
    PROJECT = "project"
    SOCIAL_ACCOUNT = "social_account"


class MetricAggregation(DatabaseTextEnum):
    """Metric definition aggregation semantics."""

    SUM = "sum"
    LAST = "last"
    MAX = "max"
    MIN = "min"
    AVERAGE = "average"
    RATIO = "ratio"


class MetricValueKind(DatabaseTextEnum):
    """Metric value representation kinds."""

    INTEGER = "integer"
    DECIMAL = "decimal"
    PERCENTAGE = "percentage"
    CURRENCY = "currency"


class AnalyticsSnapshotType(DatabaseTextEnum):
    """Analytics snapshot aggregate kinds."""

    WORKSPACE_KPI = "workspace_kpi"
    PLATFORM_COMPARISON = "platform_comparison"
    GROWTH_TREND = "growth_trend"
    PUBLISHING_FREQUENCY = "publishing_frequency"


class UsageAggregation(DatabaseTextEnum):
    """Usage dimension aggregation semantics."""

    SUM = "sum"
    MAX = "max"
    LAST = "last"


class QuotaPeriodKind(DatabaseTextEnum):
    """Quota policy period kinds."""

    DAY = "day"
    MONTH = "month"
    BILLING_CYCLE = "billing_cycle"
    LIFETIME = "lifetime"


class SubscriptionStatus(DatabaseTextEnum):
    """External subscription lifecycle states."""

    TRIALING = "trialing"
    ACTIVE = "active"
    PAST_DUE = "past_due"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    ENDED = "ended"


class BillingCustomerStatus(DatabaseTextEnum):
    """External billing customer states."""

    ACTIVE = "active"
    DELINQUENT = "delinquent"
    CLOSED = "closed"


class IdempotencyState(DatabaseTextEnum):
    """Request idempotency record states."""

    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class InboxOutcome(DatabaseTextEnum):
    """Inbox consumer processing outcomes."""

    PROCESSED = "processed"
    IGNORED = "ignored"
    FAILED = "failed"


class WebhookProcessingStatus(DatabaseTextEnum):
    """Inbound webhook processing states."""

    RECEIVED = "received"
    PROCESSED = "processed"
    IGNORED = "ignored"
    FAILED = "failed"


class BackgroundJobQueue(DatabaseTextEnum):
    """Background worker queue names."""

    AI = "ai"
    MEDIA = "media"
    NOTIFICATION = "notification"
    MAINTENANCE = "maintenance"


class DataExportType(DatabaseTextEnum):
    """Tenant export package kinds."""

    WORKSPACE_EXPORT = "workspace_export"
    USER_EXPORT = "user_export"
    ERASURE_EVIDENCE = "erasure_evidence"


class DataExportState(DatabaseTextEnum):
    """Data export workflow states."""

    QUEUED = "queued"
    RUNNING = "running"
    READY = "ready"
    FAILED = "failed"
    EXPIRED = "expired"
    PURGED = "purged"


class AuditActorType(DatabaseTextEnum):
    """Kinds of principals represented in security audit events."""

    USER = "user"
    SERVICE = "service"
    SYSTEM = "system"
    PROVIDER = "provider"


class AuditOutcome(DatabaseTextEnum):
    """Security audit outcomes."""

    SUCCESS = "success"
    FAILURE = "failure"
    DENIED = "denied"


# Backward-compatible aliases referenced in task specifications.
ContentStatus = ContentLifecycle
PublishStatus = PublicationStatus
JobStatus = JobState
NotificationStatus = NotificationDeliveryStatus
ProviderType = AIProviderStatus
UserRole = OrganizationRole
Platform = PlatformStatus
