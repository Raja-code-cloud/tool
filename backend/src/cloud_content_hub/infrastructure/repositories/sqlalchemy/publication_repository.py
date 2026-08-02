"""SQLAlchemy publication repository adapter."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from cloud_content_hub.application.publishing.interfaces.publication_repository import (
    ApprovalState,
    NewPublication,
    PublicationRecord,
    PublicationStatus,
    PublicationTargetRecord,
)
from cloud_content_hub.infrastructure.database.enums import (
    ApprovalState as DbApprovalState,
)
from cloud_content_hub.infrastructure.database.enums import (
    ConnectionStatus,
    HealthStatus,
)
from cloud_content_hub.infrastructure.database.enums import (
    PublicationStatus as DbPublicationStatus,
)
from cloud_content_hub.infrastructure.database.models.approval_request import ApprovalRequest
from cloud_content_hub.infrastructure.database.models.content_version import ContentVersion
from cloud_content_hub.infrastructure.database.models.publication import Publication
from cloud_content_hub.infrastructure.database.models.publication_target import PublicationTarget
from cloud_content_hub.infrastructure.database.models.social_account import SocialAccount
from cloud_content_hub.infrastructure.repositories.sqlalchemy.base import SqlAlchemyRepository
from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import EntityNotFound


class SqlAlchemyPublicationRepository:
    """Persistence adapter for publication aggregates."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._publications = SqlAlchemyRepository(
            session,
            Publication,
            entity_name="Publication",
            workspace_scoped=True,
        )
        self._targets = SqlAlchemyRepository(
            session,
            PublicationTarget,
            entity_name="PublicationTarget",
            workspace_scoped=True,
        )

    async def get_by_id(
        self, *, workspace_id: UUID, publication_id: UUID
    ) -> PublicationRecord | None:
        """Return one active publication."""

        statement = (
            select(Publication)
            .options(selectinload(Publication.targets))
            .where(
                Publication.id == publication_id,
                Publication.workspace_id == workspace_id,
                Publication.deleted_at.is_(None),
            )
        )
        publication = (await self._session.scalars(statement)).first()
        if publication is None:
            return None
        return self._to_record(publication)

    async def create(self, publication: NewPublication) -> PublicationRecord:
        """Persist a new publication aggregate."""

        approval_request_id = await self._resolve_approved_request_id(
            workspace_id=publication.workspace_id,
            content_version_id=publication.content_version_id,
        )
        social_accounts = await self._load_social_accounts(
            workspace_id=publication.workspace_id,
            social_account_ids=frozenset(
                target.social_account_id for target in publication.targets
            ),
        )

        created_publication = await self._publications.create(
            Publication(
                workspace_id=publication.workspace_id,
                asset_id=publication.asset_id,
                version_id=publication.content_version_id,
                approval_request_id=approval_request_id,
                title=publication.title,
                created_by=publication.created_by,
                updated_by=publication.created_by,
            )
        )

        target_entities = [
            PublicationTarget(
                workspace_id=publication.workspace_id,
                publication_id=created_publication.id,
                social_account_id=target.social_account_id,
                platform_id=social_accounts[target.social_account_id].platform_id,
                content_version_id=publication.content_version_id,
                generation_output_id=target.generation_output_id,
                approval_state=DbApprovalState.PENDING,
                created_by=publication.created_by,
                updated_by=publication.created_by,
            )
            for target in publication.targets
        ]
        if target_entities:
            await self._targets.bulk_create(target_entities)

        loaded = await self.get_by_id(
            workspace_id=publication.workspace_id,
            publication_id=created_publication.id,
        )
        if loaded is None:
            raise EntityNotFound(
                f"Publication {created_publication.id} was not found after creation."
            )
        return loaded

    async def update_status(
        self,
        *,
        workspace_id: UUID,
        publication_id: UUID,
        status: PublicationStatus,
        expected_version: int,
        updated_by: UUID,
    ) -> PublicationRecord:
        """Update publication status with optimistic concurrency."""

        publication = await self._publications.get_by_id(
            publication_id,
            workspace_id=workspace_id,
        )
        if publication is None:
            raise EntityNotFound(f"Publication {publication_id} was not found.")

        publication.status = DbPublicationStatus(status.value)
        publication.updated_by = updated_by
        await self._publications.update(publication, expected_version=expected_version)

        updated = await self.get_by_id(
            workspace_id=workspace_id,
            publication_id=publication_id,
        )
        if updated is None:
            raise EntityNotFound(f"Publication {publication_id} was not found.")
        return updated

    async def validate_content_version(
        self,
        *,
        workspace_id: UUID,
        content_id: UUID,
        content_version_id: UUID,
    ) -> tuple[UUID, bool]:
        """Return asset id and whether the version is approved and immutable."""

        statement = select(ContentVersion).where(
            ContentVersion.id == content_version_id,
            ContentVersion.workspace_id == workspace_id,
            ContentVersion.deleted_at.is_(None),
        )
        content_version = (await self._session.scalars(statement)).first()
        if content_version is None or content_version.asset_id != content_id:
            return (content_id, False)

        approval_statement = select(ApprovalRequest.id).where(
            ApprovalRequest.workspace_id == workspace_id,
            ApprovalRequest.version_id == content_version_id,
            ApprovalRequest.status == DbApprovalState.APPROVED.value,
            ApprovalRequest.deleted_at.is_(None),
        )
        approved = (await self._session.scalars(approval_statement)).first() is not None
        return (content_version.asset_id, approved)

    async def validate_social_accounts(
        self,
        *,
        workspace_id: UUID,
        social_account_ids: frozenset[UUID],
    ) -> bool:
        """Return whether all social accounts are healthy and enabled."""

        if not social_account_ids:
            return True

        statement = (
            select(func.count())
            .select_from(SocialAccount)
            .where(
                SocialAccount.workspace_id == workspace_id,
                SocialAccount.id.in_(social_account_ids),
                SocialAccount.deleted_at.is_(None),
                SocialAccount.connection_status == ConnectionStatus.CONNECTED,
                SocialAccount.health_status.in_(
                    (HealthStatus.HEALTHY, HealthStatus.WARNING),
                ),
                SocialAccount.publishing_enabled.is_(True),
            )
        )
        matched_count = await self._session.scalar(statement)
        return matched_count == len(social_account_ids)

    async def _resolve_approved_request_id(
        self,
        *,
        workspace_id: UUID,
        content_version_id: UUID,
    ) -> UUID | None:
        statement = select(ApprovalRequest.id).where(
            ApprovalRequest.workspace_id == workspace_id,
            ApprovalRequest.version_id == content_version_id,
            ApprovalRequest.status == DbApprovalState.APPROVED.value,
            ApprovalRequest.deleted_at.is_(None),
        )
        return (await self._session.scalars(statement)).first()

    async def _load_social_accounts(
        self,
        *,
        workspace_id: UUID,
        social_account_ids: frozenset[UUID],
    ) -> dict[UUID, SocialAccount]:
        if not social_account_ids:
            return {}

        statement = select(SocialAccount).where(
            SocialAccount.workspace_id == workspace_id,
            SocialAccount.id.in_(social_account_ids),
            SocialAccount.deleted_at.is_(None),
        )
        accounts = (await self._session.scalars(statement)).all()
        return {account.id: account for account in accounts}

    def _to_record(self, publication: Publication) -> PublicationRecord:
        return PublicationRecord(
            id=publication.id,
            workspace_id=publication.workspace_id,
            version=publication.version,
            created_at=publication.created_at,
            updated_at=publication.updated_at,
            asset_id=publication.asset_id,
            content_version_id=publication.version_id,
            approval_request_id=publication.approval_request_id,
            title=publication.title,
            status=PublicationStatus(publication.status.value),
            targets=tuple(
                self._to_target_record(target)
                for target in publication.targets
                if target.deleted_at is None
            ),
        )

    @staticmethod
    def _to_target_record(target: PublicationTarget) -> PublicationTargetRecord:
        return PublicationTargetRecord(
            id=target.id,
            social_account_id=target.social_account_id,
            platform_id=target.platform_id,
            approval_state=ApprovalState(target.approval_state.value),
            external_post_id=target.external_post_id,
            external_url=target.external_post_url,
            published_at=target.published_at,
        )
