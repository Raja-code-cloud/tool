"""Notification business validation."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID

from cloud_content_hub.application.notifications.dto.requests import (
    NotificationPreferenceItemRequestDto,
    NotificationRequestDto,
    RetentionPolicyRequestDto,
)
from cloud_content_hub.application.notifications.exceptions.notification_errors import (
    InvalidRecipientError,
    NotificationAlreadyArchivedError,
    NotificationTypeNotFoundError,
    ReadTimestampImmutableError,
)
from cloud_content_hub.application.notifications.interfaces.notification_repository import (
    NotificationCategory,
    NotificationPriority,
    NotificationRecord,
    NotificationSeverity,
    NotificationTypeRecord,
    RetentionPolicy,
)
from cloud_content_hub.core.errors import AuthorizationError, ValidationError

STANDARD_RETENTION_DAYS = 90
EXTENDED_RETENTION_DAYS = 365

KNOWN_TYPE_CODES: frozenset[str] = frozenset(
    {
        "system",
        "publishing",
        "generation",
        "scheduler",
        "analytics",
        "security",
        "administration",
    }
)

TYPE_CODE_CATEGORY_MAP: dict[str, NotificationCategory] = {
    "system": NotificationCategory.TRANSACTIONAL,
    "publishing": NotificationCategory.PRODUCT,
    "generation": NotificationCategory.PRODUCT,
    "scheduler": NotificationCategory.PRODUCT,
    "analytics": NotificationCategory.PRODUCT,
    "security": NotificationCategory.SECURITY,
    "administration": NotificationCategory.TRANSACTIONAL,
}

PRIORITY_SEVERITY_FLOOR: dict[NotificationPriority, NotificationSeverity] = {
    NotificationPriority.LOW: NotificationSeverity.INFO,
    NotificationPriority.NORMAL: NotificationSeverity.INFO,
    NotificationPriority.HIGH: NotificationSeverity.WARNING,
}


def validate_recipient_ownership(
    notification: NotificationRecord,
    *,
    recipient_user_id: UUID,
) -> None:
    """Ensure the notification belongs to the requesting recipient."""

    if notification.recipient_user_id != recipient_user_id:
        raise AuthorizationError(detail="Notification is not accessible to the current user.")


def validate_recipient_in_workspace(*, recipient_valid: bool, recipient_user_id: UUID) -> None:
    """Ensure the recipient is an active workspace member."""

    if not recipient_valid:
        raise InvalidRecipientError(parameters={"recipientUserId": str(recipient_user_id)})


def validate_notification_type(
    notification_type: NotificationTypeRecord | None,
    *,
    type_code: str,
) -> NotificationCategory:
    """Validate that the notification type exists and return its category."""

    if notification_type is None and type_code not in KNOWN_TYPE_CODES:
        raise NotificationTypeNotFoundError(parameters={"typeCode": type_code})

    if notification_type is not None:
        return notification_type.category

    return TYPE_CODE_CATEGORY_MAP[type_code]


def validate_notification_category(
    *,
    type_code: str,
    category: NotificationCategory,
) -> None:
    """Ensure the resolved category matches the type code mapping."""

    expected = TYPE_CODE_CATEGORY_MAP.get(type_code)
    if expected is not None and expected != category:
        raise ValidationError(
            detail="Notification category does not match the type code.",
            parameters={"typeCode": type_code, "category": category.value},
        )


def validate_priority(
    *,
    priority: NotificationPriority,
    severity: NotificationSeverity,
) -> None:
    """Ensure severity meets the minimum floor for the requested priority."""

    floor = PRIORITY_SEVERITY_FLOOR[priority]
    severity_order = (
        NotificationSeverity.INFO,
        NotificationSeverity.SUCCESS,
        NotificationSeverity.WARNING,
        NotificationSeverity.ERROR,
    )
    if severity_order.index(severity) < severity_order.index(floor):
        raise ValidationError(
            detail="Notification severity is too low for the requested priority.",
            parameters={"priority": priority.value, "severity": severity.value},
        )


def resolve_retention_expiry(
    *,
    retention_policy: RetentionPolicy,
    reference_time: datetime | None = None,
) -> datetime | None:
    """Resolve expires_at from a retention policy."""

    if retention_policy == RetentionPolicy.PERMANENT:
        return None

    now = reference_time or datetime.now(tz=UTC)
    days = (
        EXTENDED_RETENTION_DAYS
        if retention_policy == RetentionPolicy.EXTENDED
        else STANDARD_RETENTION_DAYS
    )
    return now + timedelta(days=days)


def validate_retention_policy(retention_policy: RetentionPolicyRequestDto) -> RetentionPolicy:
    """Convert and validate a retention policy request value."""

    return RetentionPolicy(retention_policy.value)


def validate_read_state_transition(
    notification: NotificationRecord,
    *,
    read: bool,
) -> None:
    """Ensure read-state transitions respect immutable read timestamps."""

    if not read and notification.read_at is not None:
        raise ReadTimestampImmutableError(
            parameters={"notificationId": str(notification.id)},
        )


def validate_not_archived(notification: NotificationRecord) -> None:
    """Ensure the notification is not already archived."""

    if notification.archived_at is not None:
        raise NotificationAlreadyArchivedError(
            parameters={"notificationId": str(notification.id)},
        )


def validate_preference_item(item: NotificationPreferenceItemRequestDto) -> None:
    """Validate quiet-hours and time-zone business rules for a preference row."""

    if item.quiet_hours_start is not None and item.quiet_hours_end is None:
        raise ValidationError(detail="quietHoursEnd is required when quietHoursStart is set.")
    if item.quiet_hours_end is not None and item.quiet_hours_start is None:
        raise ValidationError(detail="quietHoursStart is required when quietHoursEnd is set.")


def validate_create_request(
    request: NotificationRequestDto,
) -> tuple[NotificationSeverity, RetentionPolicy]:
    """Validate create-notification business rules from the request DTO."""

    severity = NotificationSeverity(request.severity.value)
    priority = NotificationPriority(request.priority.value)
    validate_priority(priority=priority, severity=severity)
    retention_policy = validate_retention_policy(request.retention_policy)
    return severity, retention_policy


def build_dedupe_key(request: NotificationRequestDto) -> str:
    """Build a stable dedupe key when one is not supplied."""

    if request.dedupe_key is not None:
        return request.dedupe_key

    resource_part = (
        f"{request.resource_type}:{request.resource_id}"
        if request.resource_type is not None and request.resource_id is not None
        else "none"
    )
    return f"{request.type_code}:{resource_part}:{request.title}"
