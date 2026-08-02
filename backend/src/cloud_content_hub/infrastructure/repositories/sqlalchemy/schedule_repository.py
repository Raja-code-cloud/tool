"""SQLAlchemy schedule repository adapter."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_content_hub.application.scheduler.interfaces.schedule_repository import (
    AmbiguityPolicy,
    NewSchedule,
    ScheduleListCriteria,
    ScheduleListPage,
    ScheduleListRecord,
    SchedulePriority,
    ScheduleRecord,
    ScheduleState,
    ScheduleUpdate,
)
from cloud_content_hub.infrastructure.database.enums import (
    ApprovalState as DbApprovalState,
)
from cloud_content_hub.infrastructure.database.enums import (
    ScheduleAmbiguityPolicy,
)
from cloud_content_hub.infrastructure.database.enums import (
    SchedulePriority as DbSchedulePriority,
)
from cloud_content_hub.infrastructure.database.enums import (
    ScheduleState as DbScheduleState,
)
from cloud_content_hub.infrastructure.database.models.publication import Publication
from cloud_content_hub.infrastructure.database.models.publication_schedule import (
    PublicationSchedule,
)
from cloud_content_hub.infrastructure.database.models.publication_target import PublicationTarget
from cloud_content_hub.infrastructure.database.models.social_platform import SocialPlatform
from cloud_content_hub.infrastructure.repositories.sqlalchemy.base import SqlAlchemyRepository
from cloud_content_hub.infrastructure.repositories.sqlalchemy.cursor_pagination import (
    apply_keyset_pagination,
    build_keyset_page,
    normalize_sort_token,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import EntityNotFound
from cloud_content_hub.infrastructure.repositories.sqlalchemy.utils import active_row_expression

_SORTABLE_COLUMNS = frozenset({"updated_at", "scheduled_for"})


class SqlAlchemyScheduleRepository:
    """Persistence adapter for publication schedules."""

    _ACTIVE_STATES = (
        DbScheduleState.SCHEDULED,
        DbScheduleState.PAUSED,
        DbScheduleState.DISPATCHED,
    )

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._schedules = SqlAlchemyRepository(
            session,
            PublicationSchedule,
            entity_name="PublicationSchedule",
            workspace_scoped=True,
        )

    async def get_by_id(self, *, workspace_id: UUID, schedule_id: UUID) -> ScheduleRecord | None:
        """Return one active schedule."""

        schedule = await self._schedules.get_by_id(schedule_id, workspace_id=workspace_id)
        if schedule is None:
            return None
        return self._to_record(schedule)

    async def create(self, schedule: NewSchedule) -> ScheduleRecord:
        """Persist a new schedule."""

        created = await self._schedules.create(
            PublicationSchedule(
                workspace_id=schedule.workspace_id,
                publication_target_id=schedule.publication_target_id,
                requested_local_at=schedule.requested_local_at,
                time_zone=schedule.time_zone,
                fold=schedule.fold,
                ambiguity_policy=ScheduleAmbiguityPolicy(schedule.ambiguity_policy.value),
                scheduled_for=schedule.scheduled_for,
                state=DbScheduleState.SCHEDULED,
                priority=DbSchedulePriority(schedule.priority.value),
                created_by=schedule.created_by,
                updated_by=schedule.created_by,
            )
        )
        return self._to_record(created)

    async def cancel(
        self,
        *,
        workspace_id: UUID,
        schedule_id: UUID,
        expected_version: int,
        updated_by: UUID,
    ) -> ScheduleRecord:
        """Cancel a schedule."""

        schedule = await self._schedules.get_by_id(schedule_id, workspace_id=workspace_id)
        if schedule is None:
            raise EntityNotFound(f"PublicationSchedule {schedule_id} was not found.")

        schedule.state = DbScheduleState.CANCELLED
        schedule.updated_by = updated_by
        updated = await self._schedules.update(schedule, expected_version=expected_version)
        return self._to_record(updated)

    async def has_active_schedule(
        self,
        *,
        workspace_id: UUID,
        publication_target_id: UUID,
    ) -> bool:
        """Return whether an active schedule exists for the target."""

        statement = (
            select(func.count())
            .select_from(PublicationSchedule)
            .where(
                PublicationSchedule.workspace_id == workspace_id,
                PublicationSchedule.publication_target_id == publication_target_id,
                PublicationSchedule.deleted_at.is_(None),
                PublicationSchedule.state.in_(self._ACTIVE_STATES),
            )
        )
        matched_count = await self._session.scalar(statement)
        return (matched_count or 0) > 0

    async def validate_publication_target(
        self,
        *,
        workspace_id: UUID,
        publication_target_id: UUID,
    ) -> bool:
        """Return whether the publication target is approved and dispatchable."""

        statement = select(PublicationTarget.id).where(
            PublicationTarget.workspace_id == workspace_id,
            PublicationTarget.id == publication_target_id,
            PublicationTarget.deleted_at.is_(None),
            PublicationTarget.approval_state == DbApprovalState.APPROVED,
        )
        return (await self._session.scalars(statement)).first() is not None

    async def list_schedules(self, criteria: ScheduleListCriteria) -> ScheduleListPage:
        """List schedules with optional calendar filters."""

        sort_column = normalize_sort_token(
            criteria.sort,
            allowed_columns=_SORTABLE_COLUMNS,
            default="-updated_at",
        )
        statement = (
            select(
                PublicationSchedule,
                Publication.id,
                Publication.title,
                Publication.status,
                SocialPlatform.code,
                PublicationTarget.approval_state,
            )
            .join(
                PublicationTarget,
                (PublicationTarget.workspace_id == PublicationSchedule.workspace_id)
                & (PublicationTarget.id == PublicationSchedule.publication_target_id),
            )
            .join(
                Publication,
                (Publication.workspace_id == PublicationTarget.workspace_id)
                & (Publication.id == PublicationTarget.publication_id),
            )
            .join(SocialPlatform, SocialPlatform.id == PublicationTarget.platform_id)
            .where(PublicationSchedule.workspace_id == criteria.workspace_id)
        )
        active_predicate = active_row_expression(PublicationSchedule)
        if active_predicate is not None:
            statement = statement.where(active_predicate)

        if criteria.states:
            statement = statement.where(
                PublicationSchedule.state.in_(tuple(criteria.states)),
            )
        if criteria.priorities:
            statement = statement.where(
                PublicationSchedule.priority.in_(tuple(criteria.priorities)),
            )
        if criteria.publication_target_id is not None:
            statement = statement.where(
                PublicationSchedule.publication_target_id == criteria.publication_target_id,
            )
        if criteria.scheduled_after is not None:
            statement = statement.where(
                PublicationSchedule.scheduled_for >= criteria.scheduled_after,
            )
        if criteria.scheduled_before is not None:
            statement = statement.where(
                PublicationSchedule.scheduled_for <= criteria.scheduled_before,
            )

        statement = apply_keyset_pagination(
            statement,
            PublicationSchedule,
            sort_column=sort_column,
            cursor=criteria.cursor,
            limit=criteria.limit,
        )
        rows = (await self._session.execute(statement)).all()
        items, next_cursor, has_more = build_keyset_page(
            list(rows),
            limit=criteria.limit,
            sort_column=sort_column,
            sort_value_getter=lambda row: getattr(row[0], sort_column.name),
            id_getter=lambda row: row[0].id,
        )
        records = tuple(
            ScheduleListRecord(
                schedule=self._to_record(schedule),
                publication_id=publication_id,
                publication_title=publication_title,
                publication_status=publication_status,
                platform_code=platform_code,
                approval_state=approval_state.value
                if hasattr(approval_state, "value")
                else str(approval_state),
                queue_order=schedule.queue_order,
            )
            for schedule, publication_id, publication_title, publication_status, platform_code, approval_state in items
        )
        return ScheduleListPage(items=records, next_cursor=next_cursor, has_more=has_more)

    async def update(
        self,
        *,
        workspace_id: UUID,
        schedule_id: UUID,
        expected_version: int,
        update: ScheduleUpdate,
        updated_by: UUID,
    ) -> ScheduleRecord:
        """Update a schedule before dispatch."""

        schedule = await self._schedules.get_by_id(schedule_id, workspace_id=workspace_id)
        if schedule is None:
            raise EntityNotFound(f"PublicationSchedule {schedule_id} was not found.")

        if update.requested_local_at is not None:
            schedule.requested_local_at = update.requested_local_at
        if update.time_zone is not None:
            schedule.time_zone = update.time_zone
        if update.fold is not None:
            schedule.fold = update.fold
        if update.ambiguity_policy is not None:
            schedule.ambiguity_policy = ScheduleAmbiguityPolicy(update.ambiguity_policy.value)
        if update.priority is not None:
            schedule.priority = DbSchedulePriority(update.priority.value)
        if update.state is not None:
            schedule.state = DbScheduleState(update.state.value)
        if update.scheduled_for is not None:
            schedule.scheduled_for = update.scheduled_for

        schedule.updated_by = updated_by
        updated = await self._schedules.update(schedule, expected_version=expected_version)
        return self._to_record(updated)

    @staticmethod
    def _to_record(schedule: PublicationSchedule) -> ScheduleRecord:
        return ScheduleRecord(
            id=schedule.id,
            workspace_id=schedule.workspace_id,
            version=schedule.version,
            created_at=schedule.created_at,
            updated_at=schedule.updated_at,
            publication_target_id=schedule.publication_target_id,
            requested_local_at=schedule.requested_local_at,
            time_zone=schedule.time_zone,
            fold=schedule.fold,
            ambiguity_policy=AmbiguityPolicy(schedule.ambiguity_policy.value),
            scheduled_for=schedule.scheduled_for,
            state=ScheduleState(schedule.state.value),
            priority=SchedulePriority(schedule.priority.value),
        )
