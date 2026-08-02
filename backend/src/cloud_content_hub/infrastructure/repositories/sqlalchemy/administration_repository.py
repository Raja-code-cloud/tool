"""SQLAlchemy administration repository adapter."""

from __future__ import annotations

from datetime import datetime
from typing import Any, cast
from uuid import UUID, uuid4

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from cloud_content_hub.application.administration.interfaces.administration_repository import (
    ApplicationConfigRecord,
    AuditActorType,
    AuditLogRecord,
    AuditOutcome,
    AuditSearchCriteria,
    AuditSummaryRecord,
    FeatureFlagRecord,
    IAdministrationRepository,
    MaintenanceModeRecord,
    MaintenanceModeUpdate,
    MembershipRecord,
    MembershipRoleRecord,
    NewAuditLog,
    RoleAssignment,
    RoleRecord,
    RoleRemoval,
    SettingScopeType,
    UserRecord,
    UserSearchCriteria,
    UserSearchPage,
    WorkspaceRecord,
    WorkspaceSearchCriteria,
    WorkspaceSearchPage,
    WorkspaceSettingsUpdate,
    WorkspaceStatus,
)
from cloud_content_hub.infrastructure.database.enums import (
    AuditActorType as DbAuditActorType,
)
from cloud_content_hub.infrastructure.database.enums import (
    AuditOutcome as DbAuditOutcome,
)
from cloud_content_hub.infrastructure.database.enums import (
    SettingScopeType as DbSettingScopeType,
)
from cloud_content_hub.infrastructure.database.enums import (
    SettingValueType,
)
from cloud_content_hub.infrastructure.database.models.audit_log import AuditLog
from cloud_content_hub.infrastructure.database.models.membership_role import MembershipRole
from cloud_content_hub.infrastructure.database.models.role import Role
from cloud_content_hub.infrastructure.database.models.setting import Setting
from cloud_content_hub.infrastructure.database.models.setting_definition import SettingDefinition
from cloud_content_hub.infrastructure.database.models.workspace import Workspace
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
from cloud_content_hub.infrastructure.repositories.sqlalchemy.user_repository import (
    SqlAlchemyUserRepository,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.utils import (
    active_row_expression,
    utc_now,
)

MAINTENANCE_MODE_KEY = "system.maintenance_mode"
FEATURE_FLAG_PREFIX = "feature."

_WORKSPACE_SORTABLE_COLUMNS = frozenset({"updated_at", "created_at"})


def _map_workspace_status(value: str) -> WorkspaceStatus:
    return WorkspaceStatus(value)


def _map_setting_scope_type(value: str) -> SettingScopeType:
    return SettingScopeType(value)


def _map_audit_actor_type(value: str) -> AuditActorType:
    return AuditActorType(value)


def _map_audit_outcome(value: str) -> AuditOutcome:
    return AuditOutcome(value)


def _to_workspace_record(workspace: Workspace) -> WorkspaceRecord:
    return WorkspaceRecord(
        id=workspace.id,
        organization_id=workspace.organization_id,
        version=workspace.version,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
        name=workspace.name,
        slug=workspace.slug,
        status=_map_workspace_status(workspace.status),
        time_zone=workspace.time_zone,
        retention_policy_days=workspace.retention_policy_days,
    )


def _to_role_record(role: Role) -> RoleRecord:
    return RoleRecord(
        id=role.id,
        workspace_id=role.workspace_id,
        code=role.code,
        name=role.name,
        description=role.description,
        is_system=role.is_system,
    )


def _to_audit_log_record(entry: AuditLog) -> AuditLogRecord:
    return AuditLogRecord(
        id=entry.id,
        workspace_id=entry.workspace_id,
        organization_id=entry.organization_id,
        actor_user_id=entry.actor_user_id,
        actor_type=_map_audit_actor_type(entry.actor_type),
        action=entry.action,
        target_type=entry.target_type,
        target_id=entry.target_id,
        outcome=_map_audit_outcome(entry.outcome),
        source=entry.source,
        occurred_at=entry.occurred_at,
    )


def _parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    return None


def _extract_typed_value(value_type: SettingValueType, payload: dict[str, Any]) -> Any:
    if "value" in payload:
        return payload["value"]
    if value_type is SettingValueType.BOOLEAN and "enabled" in payload:
        return payload["enabled"]
    if value_type is SettingValueType.OBJECT:
        return payload
    if len(payload) == 1:
        return next(iter(payload.values()))
    return payload


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "on"}
    return bool(value)


def _feature_metadata(
    definition: SettingDefinition,
) -> tuple[str | None, str | None, datetime | None]:
    schema = definition.validation_schema or {}
    owner = schema.get("owner")
    purpose = schema.get("purpose")
    expires_at = _parse_datetime(schema.get("expires_at") or schema.get("expiresAt"))
    if owner is not None and not isinstance(owner, str):
        owner = str(owner)
    if purpose is not None and not isinstance(purpose, str):
        purpose = str(purpose)
    return owner, purpose, expires_at


class SqlAlchemyAdministrationRepository(IAdministrationRepository):
    """Persistence adapter for administration read and write operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._users = SqlAlchemyUserRepository(session)
        self._workspaces = SqlAlchemyRepository(
            session,
            Workspace,
            entity_name="Workspace",
            sortable_columns=_WORKSPACE_SORTABLE_COLUMNS,
        )
        self._workspace_memberships = SqlAlchemyRepository(
            session,
            WorkspaceMembership,
            entity_name="WorkspaceMembership",
            workspace_scoped=True,
        )
        self._roles = SqlAlchemyRepository(session, Role, entity_name="Role")
        self._settings = SqlAlchemyRepository(session, Setting, entity_name="Setting")
        self._setting_definitions = SqlAlchemyRepository(
            session,
            SettingDefinition,
            entity_name="SettingDefinition",
        )

    async def list_users(self, criteria: UserSearchCriteria) -> UserSearchPage:
        return await self._users.list_users(criteria)

    async def get_user(self, user_id: UUID) -> UserRecord | None:
        return await self._users.get_user(user_id)

    async def list_workspaces(self, criteria: WorkspaceSearchCriteria) -> WorkspaceSearchPage:
        sort_column = normalize_sort_token(
            criteria.sort,
            allowed_columns=_WORKSPACE_SORTABLE_COLUMNS,
        )
        statement = select(Workspace)
        workspace_active = active_row_expression(Workspace)
        if workspace_active is not None:
            statement = statement.where(workspace_active)

        if criteria.organization_id is not None:
            statement = statement.where(Workspace.organization_id == criteria.organization_id)
        if criteria.workspace_id is not None:
            statement = statement.where(Workspace.id == criteria.workspace_id)
        if criteria.statuses:
            statement = statement.where(
                Workspace.status.in_([status.value for status in criteria.statuses])
            )
        if criteria.query:
            search_term = f"%{criteria.query.strip()}%"
            statement = statement.where(
                or_(
                    Workspace.name.ilike(search_term),
                    Workspace.slug.ilike(search_term),
                )
            )

        statement = apply_keyset_pagination(
            statement,
            Workspace,
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
        return WorkspaceSearchPage(
            items=tuple(_to_workspace_record(workspace) for workspace in page_rows),
            next_cursor=next_cursor,
            has_more=has_more,
        )

    async def get_workspace(self, workspace_id: UUID) -> WorkspaceRecord | None:
        workspace = await self._workspaces.get_by_id(workspace_id, include_deleted=False)
        if workspace is None:
            return None
        return _to_workspace_record(workspace)

    async def update_workspace_settings(self, update: WorkspaceSettingsUpdate) -> WorkspaceRecord:
        workspace = await self._workspaces.get_by_id(update.workspace_id, include_deleted=False)
        if workspace is None:
            raise EntityNotFound(f"Workspace {update.workspace_id} was not found.")

        if update.name is not None:
            workspace.name = update.name
        if update.time_zone is not None:
            workspace.time_zone = update.time_zone
        if update.retention_policy_days is not None:
            workspace.retention_policy_days = update.retention_policy_days
        workspace.updated_by = update.updated_by

        updated = await self._workspaces.update(
            workspace,
            expected_version=update.expected_version,
        )
        return _to_workspace_record(updated)

    async def get_membership(
        self,
        *,
        workspace_id: UUID,
        membership_id: UUID,
    ) -> MembershipRecord | None:
        membership = await self._workspace_memberships.get_by_id(
            membership_id,
            workspace_id=workspace_id,
            include_deleted=False,
        )
        if membership is None:
            return None
        return MembershipRecord(
            id=membership.id,
            workspace_id=membership.workspace_id,
            user_id=membership.user_id,
            status=membership.status,
        )

    async def get_role(
        self,
        *,
        role_id: UUID,
        workspace_id: UUID | None,
    ) -> RoleRecord | None:
        statement = select(Role).where(Role.id == role_id)
        role_active = active_row_expression(Role)
        if role_active is not None:
            statement = statement.where(role_active)
        if workspace_id is not None:
            statement = statement.where(
                or_(Role.is_system.is_(True), Role.workspace_id == workspace_id)
            )
        else:
            statement = statement.where(Role.workspace_id.is_(None))

        role = (await self._session.scalars(statement)).first()
        if role is None:
            return None
        return _to_role_record(role)

    async def list_membership_roles(
        self,
        *,
        workspace_id: UUID,
        membership_id: UUID,
    ) -> tuple[RoleRecord, ...]:
        statement = (
            select(Role)
            .join(
                MembershipRole,
                MembershipRole.role_id == Role.id,
            )
            .where(
                MembershipRole.workspace_id == workspace_id,
                MembershipRole.membership_id == membership_id,
            )
        )
        role_active = active_row_expression(Role)
        if role_active is not None:
            statement = statement.where(role_active)
        statement = statement.order_by(Role.code.asc())

        roles = (await self._session.scalars(statement)).all()
        return tuple(_to_role_record(role) for role in roles)

    async def list_actor_roles(
        self,
        *,
        workspace_id: UUID,
        user_id: UUID,
    ) -> tuple[RoleRecord, ...]:
        statement = (
            select(Role)
            .join(MembershipRole, MembershipRole.role_id == Role.id)
            .join(
                WorkspaceMembership,
                (WorkspaceMembership.id == MembershipRole.membership_id)
                & (WorkspaceMembership.workspace_id == MembershipRole.workspace_id),
            )
            .where(
                MembershipRole.workspace_id == workspace_id,
                WorkspaceMembership.user_id == user_id,
            )
        )
        role_active = active_row_expression(Role)
        if role_active is not None:
            statement = statement.where(role_active)
        membership_active = active_row_expression(WorkspaceMembership)
        if membership_active is not None:
            statement = statement.where(membership_active)
        statement = statement.order_by(Role.code.asc())

        roles = (await self._session.scalars(statement)).all()
        return tuple(_to_role_record(role) for role in roles)

    async def assign_role(self, assignment: RoleAssignment) -> MembershipRoleRecord:
        entity = MembershipRole(
            workspace_id=assignment.workspace_id,
            membership_id=assignment.membership_id,
            role_id=assignment.role_id,
            created_by=assignment.assigned_by,
            updated_by=assignment.assigned_by,
        )
        self._session.add(entity)
        await self._session.flush()
        return MembershipRoleRecord(
            workspace_id=assignment.workspace_id,
            membership_id=assignment.membership_id,
            role_id=assignment.role_id,
        )

    async def remove_role(self, removal: RoleRemoval) -> None:
        statement = delete(MembershipRole).where(
            MembershipRole.workspace_id == removal.workspace_id,
            MembershipRole.membership_id == removal.membership_id,
            MembershipRole.role_id == removal.role_id,
        )
        await self._session.execute(statement)

    async def append_audit(self, entry: NewAuditLog) -> AuditLogRecord:
        now = utc_now()
        entity = AuditLog(
            id=uuid4(),
            workspace_id=entry.workspace_id,
            organization_id=entry.organization_id,
            actor_user_id=entry.actor_user_id,
            actor_type=DbAuditActorType(entry.actor_type.value),
            action=entry.action,
            target_type=entry.target_type,
            target_id=entry.target_id,
            outcome=DbAuditOutcome(entry.outcome.value),
            source=entry.source,
            request_id=entry.request_id,
            safe_diff=entry.safe_diff,
            occurred_at=now,
            created_at=now,
            updated_at=now,
            created_by=entry.actor_user_id,
            updated_by=entry.actor_user_id,
            deleted_at=None,
            version=1,
        )
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return _to_audit_log_record(entity)

    async def get_audit_summary(self, criteria: AuditSearchCriteria) -> AuditSummaryRecord:
        filters = self._audit_filters(criteria)
        count_statement = select(
            func.count().label("total_count"),
            func.count()
            .filter(AuditLog.outcome == DbAuditOutcome.SUCCESS.value)
            .label("success_count"),
            func.count()
            .filter(AuditLog.outcome == DbAuditOutcome.FAILURE.value)
            .label("failure_count"),
            func.count()
            .filter(AuditLog.outcome == DbAuditOutcome.DENIED.value)
            .label("denied_count"),
        )
        if filters:
            count_statement = count_statement.where(*filters)
        counts = (await self._session.execute(count_statement)).one()

        recent_statement = select(AuditLog)
        if filters:
            recent_statement = recent_statement.where(*filters)
        recent_statement = recent_statement.order_by(
            AuditLog.occurred_at.desc(),
            AuditLog.id.desc(),
        ).limit(criteria.limit)
        recent_entries = (await self._session.scalars(recent_statement)).all()

        return AuditSummaryRecord(
            total_count=int(counts.total_count or 0),
            success_count=int(counts.success_count or 0),
            failure_count=int(counts.failure_count or 0),
            denied_count=int(counts.denied_count or 0),
            recent_entries=tuple(_to_audit_log_record(entry) for entry in recent_entries),
        )

    async def list_feature_flags(
        self, *, workspace_id: UUID | None
    ) -> tuple[FeatureFlagRecord, ...]:
        definitions = await self._load_feature_flag_definitions()
        records: list[FeatureFlagRecord] = []
        for definition in definitions:
            resolved = await self._resolve_setting(definition, workspace_id=workspace_id)
            if resolved is None:
                continue
            setting, scope_type, scope_workspace_id = resolved
            payload = setting.value if setting is not None else definition.default_value
            enabled = _coerce_bool(
                _extract_typed_value(definition.value_type, payload),
            )
            owner, purpose, expires_at = _feature_metadata(definition)
            records.append(
                FeatureFlagRecord(
                    key=definition.key,
                    enabled=enabled,
                    description=definition.description,
                    owner=owner,
                    purpose=purpose,
                    expires_at=expires_at,
                    scope_type=scope_type,
                    workspace_id=scope_workspace_id,
                )
            )
        return tuple(records)

    async def get_feature_flag(
        self, *, key: str, workspace_id: UUID | None
    ) -> FeatureFlagRecord | None:
        definition = await self._get_setting_definition(key)
        if definition is None or not definition.key.startswith(FEATURE_FLAG_PREFIX):
            return None

        resolved = await self._resolve_setting(definition, workspace_id=workspace_id)
        if resolved is None:
            return None
        setting, scope_type, scope_workspace_id = resolved
        payload = setting.value if setting is not None else definition.default_value
        enabled = _coerce_bool(_extract_typed_value(definition.value_type, payload))
        owner, purpose, expires_at = _feature_metadata(definition)
        return FeatureFlagRecord(
            key=definition.key,
            enabled=enabled,
            description=definition.description,
            owner=owner,
            purpose=purpose,
            expires_at=expires_at,
            scope_type=scope_type,
            workspace_id=scope_workspace_id,
        )

    async def get_maintenance_mode(self) -> MaintenanceModeRecord:
        definition = await self._require_setting_definition(MAINTENANCE_MODE_KEY)
        setting = await self._find_global_setting(definition.id)
        payload = setting.value if setting is not None else definition.default_value
        enabled = _coerce_bool(_extract_typed_value(definition.value_type, payload))
        message = payload.get("message") if isinstance(payload, dict) else None
        if message is not None and not isinstance(message, str):
            message = str(message)
        source = setting if setting is not None else definition
        return MaintenanceModeRecord(
            enabled=enabled,
            message=message,
            updated_at=source.updated_at,
            updated_by=source.updated_by,
        )

    async def set_maintenance_mode(self, update: MaintenanceModeUpdate) -> MaintenanceModeRecord:
        definition = await self._require_setting_definition(MAINTENANCE_MODE_KEY)
        value = {"enabled": update.enabled, "message": update.message}
        setting = await self._find_global_setting(definition.id)

        if setting is not None:
            setting.value = value
            setting.updated_by = update.updated_by
            updated = await self._settings.update(setting, expected_version=setting.version)
            return MaintenanceModeRecord(
                enabled=update.enabled,
                message=update.message,
                updated_at=updated.updated_at,
                updated_by=updated.updated_by,
            )

        definition.default_value = value
        definition.updated_by = update.updated_by
        try:
            updated_definition = await self._setting_definitions.update(
                definition,
                expected_version=definition.version,
            )
        except ConcurrencyConflict:
            refreshed = await self._require_setting_definition(MAINTENANCE_MODE_KEY)
            refreshed.default_value = value
            refreshed.updated_by = update.updated_by
            updated_definition = await self._setting_definitions.update(
                refreshed,
                expected_version=refreshed.version,
            )

        return MaintenanceModeRecord(
            enabled=update.enabled,
            message=update.message,
            updated_at=updated_definition.updated_at,
            updated_by=updated_definition.updated_by,
        )

    async def list_application_config(
        self,
        *,
        workspace_id: UUID | None,
    ) -> tuple[ApplicationConfigRecord, ...]:
        statement = (
            select(SettingDefinition)
            .where(SettingDefinition.is_secret.is_(False))
            .where(SettingDefinition.key.not_like(f"{FEATURE_FLAG_PREFIX}%"))
            .order_by(SettingDefinition.key.asc())
        )
        definition_active = active_row_expression(SettingDefinition)
        if definition_active is not None:
            statement = statement.where(definition_active)

        definitions = (await self._session.scalars(statement)).all()
        records: list[ApplicationConfigRecord] = []
        for definition in definitions:
            if definition.key == MAINTENANCE_MODE_KEY:
                continue
            resolved = await self._resolve_setting(definition, workspace_id=workspace_id)
            if resolved is None:
                continue
            setting, scope_type, _ = resolved
            payload = setting.value if setting is not None else definition.default_value
            records.append(
                ApplicationConfigRecord(
                    key=definition.key,
                    value=_extract_typed_value(definition.value_type, payload),
                    value_type=definition.value_type,
                    scope_type=scope_type,
                    workspace_id=setting.workspace_id if setting is not None else None,
                    description=definition.description,
                )
            )
        return tuple(records)

    def _audit_filters(self, criteria: AuditSearchCriteria) -> list[Any]:
        filters: list[Any] = []
        if criteria.workspace_id is not None:
            filters.append(AuditLog.workspace_id == criteria.workspace_id)
        if criteria.organization_id is not None:
            filters.append(AuditLog.organization_id == criteria.organization_id)
        if criteria.actions:
            filters.append(AuditLog.action.in_(tuple(criteria.actions)))
        if criteria.outcomes:
            filters.append(AuditLog.outcome.in_([outcome.value for outcome in criteria.outcomes]))
        if criteria.occurred_after is not None:
            filters.append(AuditLog.occurred_at >= criteria.occurred_after)
        if criteria.occurred_before is not None:
            filters.append(AuditLog.occurred_at <= criteria.occurred_before)
        return filters

    async def _load_feature_flag_definitions(self) -> list[SettingDefinition]:
        statement = (
            select(SettingDefinition)
            .where(SettingDefinition.key.like(f"{FEATURE_FLAG_PREFIX}%"))
            .order_by(SettingDefinition.key.asc())
        )
        definition_active = active_row_expression(SettingDefinition)
        if definition_active is not None:
            statement = statement.where(definition_active)
        return list((await self._session.scalars(statement)).all())

    async def _get_setting_definition(self, key: str) -> SettingDefinition | None:
        statement = select(SettingDefinition).where(SettingDefinition.key == key)
        definition_active = active_row_expression(SettingDefinition)
        if definition_active is not None:
            statement = statement.where(definition_active)
        return (await self._session.scalars(statement)).first()

    async def _require_setting_definition(self, key: str) -> SettingDefinition:
        definition = await self._get_setting_definition(key)
        if definition is None:
            raise EntityNotFound(f"SettingDefinition {key!r} was not found.")
        return definition

    async def _find_global_setting(self, definition_id: UUID) -> Setting | None:
        statement = (
            select(Setting)
            .where(
                Setting.definition_id == definition_id,
                Setting.workspace_id.is_(None),
            )
            .order_by(Setting.updated_at.desc())
        )
        setting_active = active_row_expression(Setting)
        if setting_active is not None:
            statement = statement.where(setting_active)
        return (await self._session.scalars(statement)).first()

    async def _resolve_setting(
        self,
        definition: SettingDefinition,
        *,
        workspace_id: UUID | None,
    ) -> tuple[Setting | None, SettingScopeType, UUID | None] | None:
        organization_id: UUID | None = None
        if workspace_id is not None:
            workspace = await self._workspaces.get_by_id(workspace_id, include_deleted=False)
            if workspace is None:
                return None
            organization_id = workspace.organization_id

        workspace_setting = await self._find_scoped_setting(
            definition.id,
            scope_type=DbSettingScopeType.WORKSPACE,
            workspace_id=workspace_id,
        )
        if workspace_setting is not None:
            return (
                workspace_setting,
                SettingScopeType.WORKSPACE,
                workspace_setting.workspace_id,
            )

        if organization_id is not None:
            organization_setting = await self._find_scoped_setting(
                definition.id,
                scope_type=DbSettingScopeType.ORGANIZATION,
                organization_id=organization_id,
            )
            if organization_setting is not None:
                return (
                    organization_setting,
                    SettingScopeType.ORGANIZATION,
                    None,
                )

        global_setting = await self._find_global_setting(definition.id)
        if global_setting is not None:
            return (
                global_setting,
                SettingScopeType.ORGANIZATION,
                None,
            )

        return (None, SettingScopeType.ORGANIZATION, None)

    async def _find_scoped_setting(
        self,
        definition_id: UUID,
        *,
        scope_type: DbSettingScopeType,
        workspace_id: UUID | None = None,
        organization_id: UUID | None = None,
    ) -> Setting | None:
        statement = select(Setting).where(
            Setting.definition_id == definition_id,
            Setting.scope_type == scope_type.value,
        )
        if workspace_id is not None:
            statement = statement.where(Setting.workspace_id == workspace_id)
        if organization_id is not None:
            statement = statement.where(Setting.organization_id == organization_id)
        setting_active = active_row_expression(Setting)
        if setting_active is not None:
            statement = statement.where(setting_active)
        return (await self._session.scalars(statement)).first()
