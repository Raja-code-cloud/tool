"""SQLAlchemy schedule repository adapter."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_content_hub.application.scheduler.interfaces.schedule_repository import (
    AmbiguityPolicy,
    NewSchedule,
    SchedulePriority,
    ScheduleRecord,
    ScheduleState,
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
from cloud_content_hub.infrastructure.database.models.publication_schedule import (
    PublicationSchedule,
)
from cloud_content_hub.infrastructure.database.models.publication_target import PublicationTarget
from cloud_content_hub.infrastructure.repositories.sqlalchemy.base import SqlAlchemyRepository
from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import EntityNotFound


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
