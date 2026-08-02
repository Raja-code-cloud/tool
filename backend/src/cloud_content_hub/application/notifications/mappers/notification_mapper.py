"""Notification record to DTO mappers."""

from __future__ import annotations

from cloud_content_hub.application.notifications.dto.responses import (
    NotificationChannelDto,
    NotificationPreferenceResponseDto,
    NotificationResponseDto,
    NotificationSeverityDto,
    NotificationSummaryResponseDto,
    SeverityCountDto,
    TypeCodeCountDto,
    UnreadCountResponseDto,
)
from cloud_content_hub.application.notifications.interfaces import NotificationPreferenceRecord
from cloud_content_hub.application.notifications.interfaces.notification_repository import (
    NotificationRecord,
    NotificationSummaryRecord,
)


class NotificationMapper:
    """Maps notification read models to response DTOs."""

    @staticmethod
    def to_dto(record: NotificationRecord) -> NotificationResponseDto:
        return NotificationResponseDto(
            id=record.id,
            version=record.version,
            created_at=record.created_at,
            updated_at=record.updated_at,
            type_code=record.type_code,
            title=record.title,
            body=record.body,
            severity=NotificationSeverityDto(record.severity.value),
            resource_type=record.resource_type,
            resource_id=record.resource_id,
            read_at=record.read_at,
            archived_at=record.archived_at,
            expires_at=record.expires_at,
        )


class NotificationPreferenceMapper:
    """Maps preference read models to response DTOs."""

    @staticmethod
    def to_dto(record: NotificationPreferenceRecord) -> NotificationPreferenceResponseDto:
        return NotificationPreferenceResponseDto(
            id=record.id,
            version=record.version,
            created_at=record.created_at,
            updated_at=record.updated_at,
            type_code=record.type_code,
            channel=NotificationChannelDto(record.channel.value),
            enabled=record.enabled,
            quiet_hours_start=record.quiet_hours_start,
            quiet_hours_end=record.quiet_hours_end,
            time_zone=record.time_zone,
        )


class NotificationSummaryMapper:
    """Maps summary read models to response DTOs."""

    @staticmethod
    def to_dto(record: NotificationSummaryRecord) -> NotificationSummaryResponseDto:
        return NotificationSummaryResponseDto(
            total_count=record.total_count,
            unread_count=record.unread_count,
            archived_count=record.archived_count,
            counts_by_severity=tuple(
                SeverityCountDto(severity=NotificationSeverityDto(severity.value), count=count)
                for severity, count in record.counts_by_severity
            ),
            counts_by_type_code=tuple(
                TypeCodeCountDto(type_code=type_code, count=count)
                for type_code, count in record.counts_by_type_code
            ),
        )

    @staticmethod
    def to_unread_count_dto(unread_count: int) -> UnreadCountResponseDto:
        return UnreadCountResponseDto(unread_count=unread_count)
