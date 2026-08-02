"""SQLAlchemy social account repository adapter."""

from __future__ import annotations

import hashlib
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from cloud_content_hub.application.social_accounts.interfaces.social_account_repository import (
    ActivityEventRecord,
    ActivityListCriteria,
    ActivityListPage,
    ActivityType,
    ConnectSocialAccountInput,
    DefaultSettingsRecord,
    DefaultSettingsUpdate,
    SocialAccountListCriteria,
    SocialAccountListPage,
    SocialAccountRecord,
    SocialAccountUpdate,
    SocialPlatformRecord,
)
from cloud_content_hub.infrastructure.database.enums import (
    ConnectionStatus,
    HealthStatus,
    OAuthTokenStatus,
    PlatformStatus,
    PublicationStatusHistoryType,
)
from cloud_content_hub.infrastructure.database.models.oauth_token_vault import OAuthTokenVault
from cloud_content_hub.infrastructure.database.models.publication import Publication
from cloud_content_hub.infrastructure.database.models.publication_status_history import (
    PublicationStatusHistory,
)
from cloud_content_hub.infrastructure.database.models.publication_target import PublicationTarget
from cloud_content_hub.infrastructure.database.models.social_account import SocialAccount
from cloud_content_hub.infrastructure.database.models.social_account_permission import (
    SocialAccountPermission,
)
from cloud_content_hub.infrastructure.database.models.social_account_setting import (
    SocialAccountSetting,
)
from cloud_content_hub.infrastructure.database.models.social_platform import SocialPlatform
from cloud_content_hub.infrastructure.repositories.sqlalchemy.base import SqlAlchemyRepository
from cloud_content_hub.infrastructure.repositories.sqlalchemy.cursor_pagination import (
    apply_keyset_pagination,
    build_keyset_page,
    normalize_sort_token,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import EntityNotFound
from cloud_content_hub.infrastructure.repositories.sqlalchemy.utils import active_row_expression, utc_now

_ACCOUNT_SORT_COLUMNS = frozenset({"updated_at", "connected_at"})
_ACTIVITY_SORT_COLUMNS = frozenset({"timestamp"})
_DEFAULT_PERMISSIONS = ("publish", "read_profile", "read_analytics")


class SqlAlchemySocialAccountRepository:
    """Persistence adapter for social account operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._accounts = SqlAlchemyRepository(
            session,
            SocialAccount,
            entity_name="SocialAccount",
            workspace_scoped=True,
        )

    async def list_accounts(self, criteria: SocialAccountListCriteria) -> SocialAccountListPage:
        statement = (
            select(SocialAccount)
            .options(
                selectinload(SocialAccount.platform),
                selectinload(SocialAccount.permissions),
                selectinload(SocialAccount.account_settings),
                selectinload(SocialAccount.oauth_token_vaults),
            )
            .where(
                SocialAccount.workspace_id == criteria.workspace_id,
                active_row_expression(SocialAccount),
            )
        )
        sort_column, sort_direction = normalize_sort_token(
            criteria.sort,
            allowed=_ACCOUNT_SORT_COLUMNS,
            default="-updated_at",
        )
        statement = apply_keyset_pagination(
            statement,
            model=SocialAccount,
            sort_column=sort_column,
            sort_direction=sort_direction,
            cursor=criteria.cursor,
            limit=criteria.limit,
        )
        rows = (await self._session.scalars(statement)).all()
        page = build_keyset_page(
            rows,
            sort_column=sort_column,
            sort_direction=sort_direction,
            limit=criteria.limit,
        )
        return SocialAccountListPage(
            items=tuple(self._to_record(row) for row in page.items),
            next_cursor=page.next_cursor,
            has_more=page.has_more,
        )

    async def get_by_id(
        self, *, workspace_id: UUID, account_id: UUID
    ) -> SocialAccountRecord | None:
        statement = (
            select(SocialAccount)
            .options(
                selectinload(SocialAccount.platform),
                selectinload(SocialAccount.permissions),
                selectinload(SocialAccount.account_settings),
                selectinload(SocialAccount.oauth_token_vaults),
            )
            .where(
                SocialAccount.id == account_id,
                SocialAccount.workspace_id == workspace_id,
                active_row_expression(SocialAccount),
            )
        )
        account = (await self._session.scalars(statement)).first()
        if account is None:
            return None
        return self._to_record(account)

    async def list_enabled_platforms(self) -> tuple[SocialPlatformRecord, ...]:
        statement = (
            select(SocialPlatform)
            .where(
                SocialPlatform.status == PlatformStatus.ENABLED.value,
                active_row_expression(SocialPlatform),
            )
            .order_by(SocialPlatform.name.asc())
        )
        platforms = (await self._session.scalars(statement)).all()
        return tuple(self._to_platform_record(platform) for platform in platforms)

    async def get_platform_by_code(self, platform_code: str) -> SocialPlatformRecord | None:
        statement = select(SocialPlatform).where(
            func.lower(SocialPlatform.code) == platform_code.lower(),
            active_row_expression(SocialPlatform),
        )
        platform = (await self._session.scalars(statement)).first()
        if platform is None:
            return None
        return self._to_platform_record(platform)

    async def connect_account(self, connection: ConnectSocialAccountInput) -> SocialAccountRecord:
        platform = await self._load_platform_entity(connection.platform_code)
        external_account_id = f"mock-{connection.platform_code}-{connection.workspace_id}"
        now = utc_now()

        statement = select(SocialAccount).where(
            SocialAccount.workspace_id == connection.workspace_id,
            SocialAccount.platform_id == platform.id,
            SocialAccount.external_account_id == external_account_id,
            active_row_expression(SocialAccount),
        )
        account = (await self._session.scalars(statement)).first()

        if account is None:
            account = await self._accounts.create(
                SocialAccount(
                    workspace_id=connection.workspace_id,
                    platform_id=platform.id,
                    external_account_id=external_account_id,
                    account_name=f"{platform.name} Account",
                    display_name=f"{platform.name} Account",
                    username=f"@{connection.platform_code}-workspace",
                    account_type="Personal profile",
                    connection_status=ConnectionStatus.CONNECTED.value,
                    health_status=HealthStatus.HEALTHY.value,
                    publishing_enabled=True,
                    connected_at=now,
                    last_sync_at=now,
                    followers_count=0,
                    created_by=connection.connected_by,
                    updated_by=connection.connected_by,
                )
            )
            await self._ensure_token_vault(
                account=account,
                authorization_code=connection.authorization_code,
                created_by=connection.connected_by,
            )
            await self._ensure_permissions(account=account, created_by=connection.connected_by)
            await self._ensure_settings(account=account, created_by=connection.connected_by)
        else:
            account.connection_status = ConnectionStatus.CONNECTED.value
            account.health_status = HealthStatus.HEALTHY.value
            account.connected_at = now
            account.last_sync_at = now
            account.updated_by = connection.connected_by
            await self._ensure_token_vault(
                account=account,
                authorization_code=connection.authorization_code,
                created_by=connection.connected_by,
            )

        await self._session.flush()
        loaded = await self.get_by_id(
            workspace_id=connection.workspace_id,
            account_id=account.id,
        )
        if loaded is None:
            raise EntityNotFound(f"SocialAccount {account.id} was not found after connect.")
        return loaded

    async def disconnect_account(
        self,
        *,
        workspace_id: UUID,
        account_id: UUID,
        updated_by: UUID,
    ) -> SocialAccountRecord:
        account = await self._load_account_entity(workspace_id=workspace_id, account_id=account_id)
        account.connection_status = ConnectionStatus.DISCONNECTED.value
        account.health_status = HealthStatus.NEEDS_REAUTH.value
        account.updated_by = updated_by

        for vault in account.oauth_token_vaults:
            if vault.deleted_at is None:
                vault.status = OAuthTokenStatus.REVOKED.value
                vault.revoked_at = utc_now()
                vault.updated_by = updated_by

        await self._session.flush()
        record = await self.get_by_id(workspace_id=workspace_id, account_id=account_id)
        if record is None:
            raise EntityNotFound(f"SocialAccount {account_id} was not found after disconnect.")
        return record

    async def refresh_account(
        self,
        *,
        workspace_id: UUID,
        account_id: UUID,
        updated_by: UUID,
    ) -> SocialAccountRecord:
        account = await self._load_account_entity(workspace_id=workspace_id, account_id=account_id)
        now = utc_now()
        account.last_sync_at = now
        account.health_status = HealthStatus.HEALTHY.value
        account.updated_by = updated_by

        for vault in account.oauth_token_vaults:
            if vault.deleted_at is None:
                vault.status = OAuthTokenStatus.ACTIVE.value
                vault.rotated_at = now
                vault.updated_by = updated_by

        await self._session.flush()
        record = await self.get_by_id(workspace_id=workspace_id, account_id=account_id)
        if record is None:
            raise EntityNotFound(f"SocialAccount {account_id} was not found after refresh.")
        return record

    async def update_account(
        self,
        *,
        workspace_id: UUID,
        account_id: UUID,
        expected_version: int,
        update: SocialAccountUpdate,
        updated_by: UUID,
    ) -> SocialAccountRecord:
        account = await self._load_account_entity(workspace_id=workspace_id, account_id=account_id)
        if update.publishing_enabled is not None:
            account.publishing_enabled = update.publishing_enabled
        account.updated_by = updated_by

        if update.default_settings is not None:
            settings = await self._load_or_create_settings(account=account, updated_by=updated_by)
            patch = update.default_settings
            if patch.visibility is not None:
                settings.visibility = patch.visibility
            if patch.hashtag_strategy is not None:
                settings.hashtag_strategy = patch.hashtag_strategy
            if patch.auto_publish is not None:
                settings.auto_publish = patch.auto_publish
            if patch.ai_optimization is not None:
                settings.ai_optimization = patch.ai_optimization
            if patch.auto_schedule is not None:
                settings.auto_schedule = patch.auto_schedule
            if patch.url_tracking is not None:
                settings.url_tracking = patch.url_tracking
            settings.updated_by = updated_by

        updated = await self._accounts.update(account, expected_version=expected_version)
        await self._session.flush()
        record = await self.get_by_id(workspace_id=workspace_id, account_id=updated.id)
        if record is None:
            raise EntityNotFound(f"SocialAccount {account_id} was not found after update.")
        return record

    async def list_activity(self, criteria: ActivityListCriteria) -> ActivityListPage:
        events: list[ActivityEventRecord] = []

        account_statement = (
            select(SocialAccount, SocialPlatform.name)
            .join(SocialPlatform, SocialAccount.platform_id == SocialPlatform.id)
            .where(
                SocialAccount.workspace_id == criteria.workspace_id,
                active_row_expression(SocialAccount),
            )
        )
        account_rows = (await self._session.execute(account_statement)).all()
        for account, platform_name in account_rows:
            if account.connected_at is not None:
                events.append(
                    ActivityEventRecord(
                        id=uuid4(),
                        account_id=account.id,
                        platform_name=platform_name,
                        activity_type=ActivityType.CONNECTED,
                        message=f"{platform_name} account connected.",
                        timestamp=account.connected_at,
                    )
                )
            if account.connection_status == ConnectionStatus.DISCONNECTED.value:
                events.append(
                    ActivityEventRecord(
                        id=uuid4(),
                        account_id=account.id,
                        platform_name=platform_name,
                        activity_type=ActivityType.DISCONNECTED,
                        message=f"{platform_name} account disconnected.",
                        timestamp=account.updated_at,
                    )
                )

        history_statement = (
            select(
                PublicationStatusHistory,
                PublicationTarget.social_account_id,
                SocialPlatform.name,
            )
            .join(
                PublicationTarget,
                PublicationStatusHistory.publication_target_id == PublicationTarget.id,
            )
            .join(SocialPlatform, PublicationTarget.platform_id == SocialPlatform.id)
            .where(
                PublicationStatusHistory.workspace_id == criteria.workspace_id,
                PublicationStatusHistory.state_type
                == PublicationStatusHistoryType.JOB.value,
            )
        )
        history_rows = (await self._session.execute(history_statement)).all()
        for history, social_account_id, platform_name in history_rows:
            if history.to_state in {"succeeded", "completed"}:
                activity_type = ActivityType.PUBLISH_SUCCESS
                message = f"Published successfully to {platform_name}."
            elif history.to_state in {"failed", "dead_lettered"}:
                activity_type = ActivityType.PUBLISH_FAILED
                message = f"Publish failed for {platform_name}."
            else:
                continue
            events.append(
                ActivityEventRecord(
                    id=history.id,
                    account_id=social_account_id,
                    platform_name=platform_name,
                    activity_type=activity_type,
                    message=message,
                    timestamp=history.occurred_at,
                )
            )

        permission_statement = (
            select(SocialAccountPermission, SocialPlatform.name)
            .join(SocialAccount, SocialAccountPermission.social_account_id == SocialAccount.id)
            .join(SocialPlatform, SocialAccount.platform_id == SocialPlatform.id)
            .where(
                SocialAccountPermission.workspace_id == criteria.workspace_id,
                active_row_expression(SocialAccountPermission),
            )
        )
        permission_rows = (await self._session.execute(permission_statement)).all()
        for permission, platform_name in permission_rows:
            events.append(
                ActivityEventRecord(
                    id=permission.id,
                    account_id=permission.social_account_id,
                    platform_name=platform_name,
                    activity_type=ActivityType.PERMISSION_CHANGED,
                    message=f"Permission '{permission.permission_code}' granted.",
                    timestamp=permission.granted_at,
                )
            )

        reverse = criteria.sort.startswith("-")
        events.sort(key=lambda event: event.timestamp, reverse=reverse)
        limit = criteria.limit
        items = tuple(events[: limit + 1])
        has_more = len(items) > limit
        page_items = items[:limit]
        next_cursor = str(len(events)) if has_more else None
        return ActivityListPage(
            items=page_items,
            next_cursor=next_cursor,
            has_more=has_more,
        )

    async def _load_platform_entity(self, platform_code: str) -> SocialPlatform:
        statement = select(SocialPlatform).where(
            func.lower(SocialPlatform.code) == platform_code.lower(),
            active_row_expression(SocialPlatform),
        )
        platform = (await self._session.scalars(statement)).first()
        if platform is None:
            raise EntityNotFound(f"SocialPlatform {platform_code} was not found.")
        return platform

    async def _load_account_entity(self, *, workspace_id: UUID, account_id: UUID) -> SocialAccount:
        statement = (
            select(SocialAccount)
            .options(selectinload(SocialAccount.oauth_token_vaults))
            .where(
                SocialAccount.id == account_id,
                SocialAccount.workspace_id == workspace_id,
                active_row_expression(SocialAccount),
            )
        )
        account = (await self._session.scalars(statement)).first()
        if account is None:
            raise EntityNotFound(f"SocialAccount {account_id} was not found.")
        return account

    async def _ensure_token_vault(
        self,
        *,
        account: SocialAccount,
        authorization_code: str,
        created_by: UUID,
    ) -> None:
        fingerprint = hashlib.sha256(authorization_code.encode("utf-8")).digest()
        existing = next(
            (vault for vault in account.oauth_token_vaults if vault.deleted_at is None),
            None,
        )
        if existing is not None:
            existing.ciphertext = authorization_code.encode("utf-8")
            existing.token_fingerprint = fingerprint
            existing.status = OAuthTokenStatus.ACTIVE.value
            existing.revoked_at = None
            existing.updated_by = created_by
            return

        self._session.add(
            OAuthTokenVault(
                workspace_id=account.workspace_id,
                social_account_id=account.id,
                ciphertext=authorization_code.encode("utf-8"),
                key_id="dev-mock",
                key_version="1",
                token_fingerprint=fingerprint,
                status=OAuthTokenStatus.ACTIVE.value,
                created_by=created_by,
                updated_by=created_by,
            )
        )

    async def _ensure_permissions(self, *, account: SocialAccount, created_by: UUID) -> None:
        now = utc_now()
        for permission_code in _DEFAULT_PERMISSIONS:
            self._session.add(
                SocialAccountPermission(
                    workspace_id=account.workspace_id,
                    social_account_id=account.id,
                    permission_code=permission_code,
                    granted_at=now,
                    created_by=created_by,
                    updated_by=created_by,
                )
            )

    async def _ensure_settings(self, *, account: SocialAccount, created_by: UUID) -> None:
        self._session.add(
            SocialAccountSetting(
                workspace_id=account.workspace_id,
                social_account_id=account.id,
                visibility="Public",
                hashtag_strategy="",
                auto_publish=False,
                ai_optimization=False,
                auto_schedule=False,
                url_tracking=False,
                created_by=created_by,
                updated_by=created_by,
            )
        )

    async def _load_or_create_settings(
        self, *, account: SocialAccount, updated_by: UUID
    ) -> SocialAccountSetting:
        statement = select(SocialAccountSetting).where(
            SocialAccountSetting.workspace_id == account.workspace_id,
            SocialAccountSetting.social_account_id == account.id,
            active_row_expression(SocialAccountSetting),
        )
        settings = (await self._session.scalars(statement)).first()
        if settings is not None:
            return settings
        settings = SocialAccountSetting(
            workspace_id=account.workspace_id,
            social_account_id=account.id,
            created_by=updated_by,
            updated_by=updated_by,
        )
        self._session.add(settings)
        return settings

    def _to_record(self, account: SocialAccount) -> SocialAccountRecord:
        platform = account.platform
        active_vault = next(
            (vault for vault in account.oauth_token_vaults if vault.deleted_at is None),
            None,
        )
        token_status = active_vault.status if active_vault is not None else None
        permissions = tuple(
            permission.permission_code
            for permission in account.permissions
            if permission.revoked_at is None and permission.deleted_at is None
        )
        settings_entity = next(
            (settings for settings in account.account_settings if settings.deleted_at is None),
            None,
        )
        default_settings = None
        if settings_entity is not None:
            default_settings = DefaultSettingsRecord(
                visibility=settings_entity.visibility,
                hashtag_strategy=settings_entity.hashtag_strategy,
                auto_publish=settings_entity.auto_publish,
                ai_optimization=settings_entity.ai_optimization,
                auto_schedule=settings_entity.auto_schedule,
                url_tracking=settings_entity.url_tracking,
            )
        return SocialAccountRecord(
            id=account.id,
            workspace_id=account.workspace_id,
            version=account.version,
            created_at=account.created_at,
            updated_at=account.updated_at,
            platform_id=platform.id,
            platform_code=platform.code,
            platform_name=platform.name,
            external_account_id=account.external_account_id,
            account_name=account.account_name,
            display_name=account.display_name,
            username=account.username,
            account_type=account.account_type,
            connection_status=account.connection_status,
            health_status=account.health_status,
            token_status=token_status,
            publishing_enabled=account.publishing_enabled,
            default_audience=account.default_audience,
            time_zone=account.time_zone,
            followers_count=account.followers_count,
            connected_at=account.connected_at,
            last_sync_at=account.last_sync_at,
            permissions=permissions,
            default_settings=default_settings,
        )

    @staticmethod
    def _to_platform_record(platform: SocialPlatform) -> SocialPlatformRecord:
        return SocialPlatformRecord(
            id=platform.id,
            code=platform.code,
            name=platform.name,
            status=platform.status,
            api_version=platform.api_version,
            capability_metadata=dict(platform.capability_metadata or {}),
        )
