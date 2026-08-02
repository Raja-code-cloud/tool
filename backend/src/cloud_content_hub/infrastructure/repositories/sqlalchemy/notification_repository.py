"""SQLAlchemy notification repository adapters."""

from __future__ import annotations

from typing import Any, cast
from uuid import UUID

from sqlalchemy import func, or_, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from cloud_content_hub.application.notifications.interfaces import (
    notification_preference_repository as preference_ports,
)
from cloud_content_hub.application.notifications.interfaces.notification_repository import (
    NewNotification,
    NotificationCategory,
    NotificationRecord,
    NotificationSearchCriteria,
    NotificationSearchPage,
    NotificationSeverity,
    NotificationSummaryRecord,
    NotificationTypeRecord,
)
from cloud_content_hub.infrastructure.database.enums import MembershipStatus
from cloud_content_hub.infrastructure.database.enums import (
    NotificationChannel as DbNotificationChannel,
)
from cloud_content_hub.infrastructure.database.enums import (
    NotificationSeverity as DbNotificationSeverity,
)
from cloud_content_hub.infrastructure.database.models.notification import Notification
from cloud_content_hub.infrastructure.database.models.notification_preference import (
    NotificationPreference,
)
from cloud_content_hub.infrastructure.database.models.notification_type import NotificationType
from cloud_content_hub.infrastructure.database.models.workspace_membership import (
    WorkspaceMembership,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.base import SqlAlchemyRepository
from cloud_content_hub.infrastructure.repositories.sqlalchemy.cursor_pagination import (
    apply_keyset_pagination,
    build_keyset_page,
    normalize_sort_token,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import (
    ConcurrencyConflict,
    EntityNotFound,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.utils import utc_now

_NOTIFICATION_SORT_COLUMNS = frozenset({"updated_at", "created_at"})


class SqlAlchemyNotificationRepository:
    """Persistence adapter for workspace notification inbox operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repository = SqlAlchemyRepository(
            session,
            Notification,
            entity_name="Notification",
            workspace_scoped=True,
        )

    async def get_by_id(
        self,
        *,
        workspace_id: UUID,
        notification_id: UUID,
        recipient_user_id: UUID,
    ) -> NotificationRecord | None:
        """Return one notification for the recipient."""

        row = await self._fetch_notification_row(
            workspace_id=workspace_id,
            notification_id=notification_id,
            recipient_user_id=recipient_user_id,
        )
        if row is None:
            return None
        return self._to_record(row)

    async def search(self, criteria: NotificationSearchCriteria) -> NotificationSearchPage:
        """Search the recipient notification inbox."""

        notification_type = aliased(NotificationType)
        statement = (
            select(Notification, notification_type.code)
            .join(
                notification_type,
                Notification.notification_type_id == notification_type.id,
            )
            .where(
                Notification.workspace_id == criteria.workspace_id,
                Notification.recipient_user_id == criteria.recipient_user_id,
                Notification.deleted_at.is_(None),
            )
        )

        if criteria.query:
            pattern = f"%{criteria.query.strip()}%"
            statement = statement.where(
                or_(Notification.title.ilike(pattern), Notification.body.ilike(pattern))
            )
        if criteria.severities:
            statement = statement.where(
                Notification.severity.in_(
                    tuple(
                        DbNotificationSeverity(severity.value) for severity in criteria.severities
                    )
                )
            )
        if criteria.type_codes:
            statement = statement.where(notification_type.code.in_(tuple(criteria.type_codes)))
        if criteria.read is True:
            statement = statement.where(Notification.read_at.is_not(None))
        elif criteria.read is False:
            statement = statement.where(Notification.read_at.is_(None))
        if not criteria.include_archived:
            statement = statement.where(Notification.archived_at.is_(None))
        if criteria.created_after is not None:
            statement = statement.where(Notification.created_at >= criteria.created_after)
        if criteria.created_before is not None:
            statement = statement.where(Notification.created_at <= criteria.created_before)

        sort_column = normalize_sort_token(
            criteria.sort,
            allowed_columns=_NOTIFICATION_SORT_COLUMNS,
        )
        statement = apply_keyset_pagination(
            statement,
            Notification,
            sort_column=sort_column,
            cursor=criteria.cursor,
            limit=criteria.limit,
        )
        row_list = list(await self._session.execute(statement))
        items, next_cursor, has_more = build_keyset_page(
            row_list,
            limit=criteria.limit,
            sort_column=sort_column,
            sort_value_getter=lambda row: (
                row[0].updated_at if sort_column.name == "updated_at" else row[0].created_at
            ),
            id_getter=lambda row: row[0].id,
        )
        records = tuple(self._to_record(row) for row in items)
        return NotificationSearchPage(items=records, next_cursor=next_cursor, has_more=has_more)

    async def create(self, notification: NewNotification) -> NotificationRecord:
        """Persist a new notification for a recipient."""

        notification_type = await self._get_type_entity(notification.type_code)
        if notification_type is None:
            raise EntityNotFound(
                f"NotificationType with code {notification.type_code!r} was not found."
            )

        entity = Notification(
            workspace_id=notification.workspace_id,
            notification_type_id=notification_type.id,
            recipient_user_id=notification.recipient_user_id,
            title=notification.title,
            body=notification.body,
            severity=DbNotificationSeverity(notification.severity.value),
            resource_type=notification.resource_type,
            resource_id=notification.resource_id,
            dedupe_key=notification.dedupe_key,
            expires_at=notification.expires_at,
            created_by=notification.created_by,
            updated_by=notification.created_by,
        )
        created = await self._repository.create(entity)
        row = await self._fetch_notification_row(
            workspace_id=notification.workspace_id,
            notification_id=created.id,
            recipient_user_id=notification.recipient_user_id,
        )
        if row is None:
            raise EntityNotFound(f"Notification {created.id} was not found after creation.")
        return self._to_record(row)

    async def mark_read(
        self,
        *,
        workspace_id: UUID,
        notification_id: UUID,
        recipient_user_id: UUID,
        read: bool,
        expected_version: int,
        updated_by: UUID,
    ) -> NotificationRecord:
        """Set or clear read state for a notification."""

        entity = await self._get_mutable_notification(
            workspace_id=workspace_id,
            notification_id=notification_id,
            recipient_user_id=recipient_user_id,
        )
        entity.read_at = utc_now() if read else None
        entity.updated_by = updated_by
        await self._repository.update(entity, expected_version=expected_version)
        row = await self._fetch_notification_row(
            workspace_id=workspace_id,
            notification_id=notification_id,
            recipient_user_id=recipient_user_id,
        )
        if row is None:
            raise EntityNotFound(f"Notification {notification_id} was not found.")
        return self._to_record(row)

    async def mark_all_read(
        self,
        *,
        workspace_id: UUID,
        recipient_user_id: UUID,
        updated_by: UUID,
    ) -> int:
        """Mark all unread notifications as read; return count updated."""

        now = utc_now()
        statement = (
            update(Notification)
            .where(
                Notification.workspace_id == workspace_id,
                Notification.recipient_user_id == recipient_user_id,
                Notification.read_at.is_(None),
                Notification.deleted_at.is_(None),
            )
            .values(
                read_at=now,
                updated_at=now,
                updated_by=updated_by,
                version=Notification.version + 1,
            )
        )
        result = await self._session.execute(statement)
        return int(cast(CursorResult[Any], result).rowcount or 0)

    async def archive(
        self,
        *,
        workspace_id: UUID,
        notification_id: UUID,
        recipient_user_id: UUID,
        expected_version: int,
        updated_by: UUID,
    ) -> NotificationRecord:
        """Archive a notification while keeping it searchable."""

        entity = await self._get_mutable_notification(
            workspace_id=workspace_id,
            notification_id=notification_id,
            recipient_user_id=recipient_user_id,
        )
        entity.archived_at = utc_now()
        entity.updated_by = updated_by
        await self._repository.update(entity, expected_version=expected_version)
        row = await self._fetch_notification_row(
            workspace_id=workspace_id,
            notification_id=notification_id,
            recipient_user_id=recipient_user_id,
        )
        if row is None:
            raise EntityNotFound(f"Notification {notification_id} was not found.")
        return self._to_record(row)

    async def soft_delete(
        self,
        *,
        workspace_id: UUID,
        notification_id: UUID,
        recipient_user_id: UUID,
        expected_version: int,
        updated_by: UUID,
    ) -> None:
        """Soft-delete a notification for the recipient."""

        entity = await self._get_mutable_notification(
            workspace_id=workspace_id,
            notification_id=notification_id,
            recipient_user_id=recipient_user_id,
        )
        if entity.version != expected_version:
            raise ConcurrencyConflict(
                f"Notification version mismatch: expected {expected_version}, "
                f"actual {entity.version}."
            )
        await self._repository.soft_delete(
            notification_id,
            expected_version=expected_version,
            updated_by=updated_by,
            workspace_id=workspace_id,
        )

    async def count_unread(
        self,
        *,
        workspace_id: UUID,
        recipient_user_id: UUID,
    ) -> int:
        """Return the unread notification count for a recipient."""

        statement = (
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.workspace_id == workspace_id,
                Notification.recipient_user_id == recipient_user_id,
                Notification.read_at.is_(None),
                Notification.deleted_at.is_(None),
            )
        )
        return int(await self._session.scalar(statement) or 0)

    async def get_summary(
        self,
        *,
        workspace_id: UUID,
        recipient_user_id: UUID,
    ) -> NotificationSummaryRecord:
        """Return aggregated inbox statistics for a recipient."""

        base_filters = (
            Notification.workspace_id == workspace_id,
            Notification.recipient_user_id == recipient_user_id,
            Notification.deleted_at.is_(None),
        )

        total_count = int(
            await self._session.scalar(
                select(func.count()).select_from(Notification).where(*base_filters)
            )
            or 0
        )
        unread_count = int(
            await self._session.scalar(
                select(func.count())
                .select_from(Notification)
                .where(*base_filters, Notification.read_at.is_(None))
            )
            or 0
        )
        archived_count = int(
            await self._session.scalar(
                select(func.count())
                .select_from(Notification)
                .where(*base_filters, Notification.archived_at.is_not(None))
            )
            or 0
        )

        severity_rows = (
            await self._session.execute(
                select(Notification.severity, func.count())
                .where(*base_filters)
                .group_by(Notification.severity)
                .order_by(Notification.severity)
            )
        ).all()
        counts_by_severity = tuple(
            (NotificationSeverity(row[0].value), int(row[1])) for row in severity_rows
        )

        type_rows = (
            await self._session.execute(
                select(NotificationType.code, func.count())
                .join(Notification, Notification.notification_type_id == NotificationType.id)
                .where(*base_filters)
                .group_by(NotificationType.code)
                .order_by(NotificationType.code)
            )
        ).all()
        counts_by_type_code = tuple((str(row[0]), int(row[1])) for row in type_rows)

        return NotificationSummaryRecord(
            total_count=total_count,
            unread_count=unread_count,
            archived_count=archived_count,
            counts_by_severity=counts_by_severity,
            counts_by_type_code=counts_by_type_code,
        )

    async def validate_recipient_in_workspace(
        self,
        *,
        workspace_id: UUID,
        recipient_user_id: UUID,
    ) -> bool:
        """Return whether the recipient is an active workspace member."""

        statement = select(WorkspaceMembership.id).where(
            WorkspaceMembership.workspace_id == workspace_id,
            WorkspaceMembership.user_id == recipient_user_id,
            WorkspaceMembership.status == MembershipStatus.ACTIVE,
            WorkspaceMembership.deleted_at.is_(None),
        )
        return (await self._session.scalars(statement)).first() is not None

    async def get_type_by_code(self, type_code: str) -> NotificationTypeRecord | None:
        """Return catalog metadata for a notification type code."""

        entity = await self._get_type_entity(type_code)
        if entity is None:
            return None
        return NotificationTypeRecord(
            code=entity.code,
            category=NotificationCategory(entity.category.value),
            default_channels=frozenset(entity.default_channels),
        )

    async def _fetch_notification_row(
        self,
        *,
        workspace_id: UUID,
        notification_id: UUID,
        recipient_user_id: UUID,
    ) -> Any | None:
        notification_type = aliased(NotificationType)
        statement = (
            select(Notification, notification_type.code)
            .join(
                notification_type,
                Notification.notification_type_id == notification_type.id,
            )
            .where(
                Notification.id == notification_id,
                Notification.workspace_id == workspace_id,
                Notification.recipient_user_id == recipient_user_id,
                Notification.deleted_at.is_(None),
            )
        )
        return (await self._session.execute(statement)).first()

    async def _get_mutable_notification(
        self,
        *,
        workspace_id: UUID,
        notification_id: UUID,
        recipient_user_id: UUID,
    ) -> Notification:
        entity = await self._repository.get_by_id(
            notification_id,
            workspace_id=workspace_id,
        )
        if entity is None or entity.recipient_user_id != recipient_user_id:
            raise EntityNotFound(f"Notification {notification_id} was not found.")
        return entity

    async def _get_type_entity(self, type_code: str) -> NotificationType | None:
        statement = select(NotificationType).where(
            NotificationType.code == type_code,
            NotificationType.deleted_at.is_(None),
        )
        return (await self._session.scalars(statement)).first()

    @staticmethod
    def _to_record(row: Any) -> NotificationRecord:
        notification = row[0]
        type_code = str(row[1])
        return NotificationRecord(
            id=notification.id,
            workspace_id=notification.workspace_id,
            version=notification.version,
            created_at=notification.created_at,
            updated_at=notification.updated_at,
            type_code=type_code,
            title=notification.title,
            body=notification.body,
            severity=NotificationSeverity(notification.severity.value),
            resource_type=notification.resource_type,
            resource_id=notification.resource_id,
            read_at=notification.read_at,
            archived_at=notification.archived_at,
            expires_at=notification.expires_at,
            recipient_user_id=notification.recipient_user_id,
        )


class SqlAlchemyNotificationPreferenceRepository:
    """Persistence adapter for notification channel preferences."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repository = SqlAlchemyRepository(
            session,
            NotificationPreference,
            entity_name="NotificationPreference",
            workspace_scoped=True,
        )

    async def list_for_user(
        self,
        *,
        workspace_id: UUID,
        user_id: UUID,
    ) -> tuple[preference_ports.NotificationPreferenceRecord, ...]:
        """Return all preferences for a user in a workspace."""

        notification_type = aliased(NotificationType)
        statement = (
            select(NotificationPreference, notification_type.code)
            .join(
                notification_type,
                NotificationPreference.notification_type_id == notification_type.id,
            )
            .where(
                NotificationPreference.workspace_id == workspace_id,
                NotificationPreference.user_id == user_id,
                NotificationPreference.deleted_at.is_(None),
            )
            .order_by(notification_type.code, NotificationPreference.channel)
        )
        rows = (await self._session.execute(statement)).all()
        return tuple(self._to_record(row) for row in rows)

    async def upsert(
        self,
        *,
        workspace_id: UUID,
        user_id: UUID,
        preference: preference_ports.PreferenceUpdate,
        updated_by: UUID,
    ) -> preference_ports.NotificationPreferenceRecord:
        """Create or update one preference row."""

        records = await self.upsert_many(
            workspace_id=workspace_id,
            user_id=user_id,
            preferences=(preference,),
            updated_by=updated_by,
        )
        return records[0]

    async def upsert_many(
        self,
        *,
        workspace_id: UUID,
        user_id: UUID,
        preferences: tuple[preference_ports.PreferenceUpdate, ...],
        updated_by: UUID,
    ) -> tuple[preference_ports.NotificationPreferenceRecord, ...]:
        """Create or update multiple preference rows."""

        results: list[preference_ports.NotificationPreferenceRecord] = []
        for preference in preferences:
            notification_type = await self._get_type_entity(preference.type_code)
            if notification_type is None:
                raise EntityNotFound(
                    f"NotificationType with code {preference.type_code!r} was not found."
                )

            existing = await self._find_preference(
                workspace_id=workspace_id,
                user_id=user_id,
                notification_type_id=notification_type.id,
                channel=DbNotificationChannel(preference.channel.value),
            )
            if existing is None:
                entity = NotificationPreference(
                    workspace_id=workspace_id,
                    user_id=user_id,
                    notification_type_id=notification_type.id,
                    channel=DbNotificationChannel(preference.channel.value),
                    enabled=preference.enabled,
                    quiet_hours_start=preference.quiet_hours_start,
                    quiet_hours_end=preference.quiet_hours_end,
                    time_zone=preference.time_zone,
                    created_by=updated_by,
                    updated_by=updated_by,
                )
                created = await self._repository.create(entity)
                row = await self._fetch_preference_row(
                    workspace_id=workspace_id,
                    preference_id=created.id,
                )
            else:
                existing.enabled = preference.enabled
                existing.quiet_hours_start = preference.quiet_hours_start
                existing.quiet_hours_end = preference.quiet_hours_end
                existing.time_zone = preference.time_zone
                existing.updated_by = updated_by
                updated = await self._repository.update(
                    existing,
                    expected_version=existing.version,
                )
                row = await self._fetch_preference_row(
                    workspace_id=workspace_id,
                    preference_id=updated.id,
                )

            if row is None:
                raise EntityNotFound("NotificationPreference was not found after upsert.")
            results.append(self._to_record(row))
        return tuple(results)

    async def _find_preference(
        self,
        *,
        workspace_id: UUID,
        user_id: UUID,
        notification_type_id: UUID,
        channel: DbNotificationChannel,
    ) -> NotificationPreference | None:
        statement = select(NotificationPreference).where(
            NotificationPreference.workspace_id == workspace_id,
            NotificationPreference.user_id == user_id,
            NotificationPreference.notification_type_id == notification_type_id,
            NotificationPreference.channel == channel,
            NotificationPreference.deleted_at.is_(None),
        )
        return (await self._session.scalars(statement)).first()

    async def _fetch_preference_row(
        self,
        *,
        workspace_id: UUID,
        preference_id: UUID,
    ) -> Any | None:
        notification_type = aliased(NotificationType)
        statement = (
            select(NotificationPreference, notification_type.code)
            .join(
                notification_type,
                NotificationPreference.notification_type_id == notification_type.id,
            )
            .where(
                NotificationPreference.id == preference_id,
                NotificationPreference.workspace_id == workspace_id,
                NotificationPreference.deleted_at.is_(None),
            )
        )
        return (await self._session.execute(statement)).first()

    async def _get_type_entity(self, type_code: str) -> NotificationType | None:
        statement = select(NotificationType).where(
            NotificationType.code == type_code,
            NotificationType.deleted_at.is_(None),
        )
        return (await self._session.scalars(statement)).first()

    @staticmethod
    def _to_record(row: Any) -> preference_ports.NotificationPreferenceRecord:
        preference = row[0]
        type_code = str(row[1])
        return preference_ports.NotificationPreferenceRecord(
            id=preference.id,
            workspace_id=preference.workspace_id,
            version=preference.version,
            created_at=preference.created_at,
            updated_at=preference.updated_at,
            user_id=preference.user_id,
            type_code=type_code,
            channel=preference_ports.NotificationChannel(preference.channel.value),
            enabled=preference.enabled,
            quiet_hours_start=preference.quiet_hours_start,
            quiet_hours_end=preference.quiet_hours_end,
            time_zone=preference.time_zone,
        )
