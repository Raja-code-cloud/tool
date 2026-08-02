"""SQLAlchemy user repository helper for administration queries."""

from __future__ import annotations

from typing import cast
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_content_hub.application.administration.interfaces.administration_repository import (
    UserRecord,
    UserSearchCriteria,
    UserSearchPage,
    UserStatus,
)
from cloud_content_hub.infrastructure.database.enums import UserStatus as DbUserStatus
from cloud_content_hub.infrastructure.database.models.user import User
from cloud_content_hub.infrastructure.database.models.workspace_membership import (
    WorkspaceMembership,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.base import SqlAlchemyRepository
from cloud_content_hub.infrastructure.repositories.sqlalchemy.cursor_pagination import (
    apply_keyset_pagination,
    build_keyset_page,
    normalize_sort_token,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.utils import active_row_expression

_USER_SORTABLE_COLUMNS = frozenset({"updated_at", "created_at"})


def _map_user_status(value: str) -> UserStatus:
    return UserStatus(value)


def _to_user_record(user: User) -> UserRecord:
    return UserRecord(
        id=user.id,
        version=user.version,
        created_at=user.created_at,
        updated_at=user.updated_at,
        email=user.email,
        display_name=user.display_name,
        locale=user.locale,
        time_zone=user.time_zone,
        status=_map_user_status(user.status),
    )


class SqlAlchemyUserRepository:
    """Lists and loads users for administration read models."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._users = SqlAlchemyRepository(
            session,
            User,
            entity_name="User",
            sortable_columns=_USER_SORTABLE_COLUMNS,
        )

    async def list_users(self, criteria: UserSearchCriteria) -> UserSearchPage:
        """Return cursor-paged users visible to the administrative scope."""

        sort_column = normalize_sort_token(
            criteria.sort,
            allowed_columns=_USER_SORTABLE_COLUMNS,
        )
        statement = select(User)

        if criteria.workspace_id is not None:
            statement = statement.join(
                WorkspaceMembership,
                WorkspaceMembership.user_id == User.id,
            ).where(
                WorkspaceMembership.workspace_id == criteria.workspace_id,
            )
            membership_active = active_row_expression(WorkspaceMembership)
            if membership_active is not None:
                statement = statement.where(membership_active)

        user_active = active_row_expression(User)
        if user_active is not None:
            statement = statement.where(user_active)

        if criteria.query:
            search_term = f"%{criteria.query.strip()}%"
            statement = statement.where(
                or_(
                    User.email.ilike(search_term),
                    User.display_name.ilike(search_term),
                )
            )

        if criteria.statuses:
            statement = statement.where(
                User.status.in_([status.value for status in criteria.statuses])
            )

        statement = apply_keyset_pagination(
            statement,
            User,
            sort_column=sort_column,
            cursor=criteria.cursor,
            limit=criteria.limit,
        )
        result = await self._session.scalars(statement)
        rows = list(result.all())
        page_rows, next_cursor, has_more = build_keyset_page(
            rows,
            limit=criteria.limit,
            sort_column=sort_column,
            sort_value_getter=lambda row: getattr(row, sort_column.name),
            id_getter=lambda row: cast(UUID, row.id),
        )
        return UserSearchPage(
            items=tuple(_to_user_record(user) for user in page_rows),
            next_cursor=next_cursor,
            has_more=has_more,
        )

    async def get_user(self, user_id: UUID) -> UserRecord | None:
        """Return one active user by identifier."""

        user = await self._users.get_by_id(user_id, include_deleted=False)
        if user is None or user.status != DbUserStatus.ACTIVE:
            return None
        return _to_user_record(user)
