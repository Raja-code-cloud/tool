"""SQLAlchemy implementations of content repository ports."""

from __future__ import annotations

import hashlib
from typing import Any, cast
from uuid import UUID, uuid4

from sqlalchemy import func, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, selectinload

from cloud_content_hub.application.content.interfaces.content_repository import (
    ContentLifecycleStatus,
    ContentOrigin,
    ContentRecord,
    ContentSearchCriteria,
    ContentSearchPage,
    ContentVersionDetailRecord,
    ContentVersionRecord,
    DuplicateContentInput,
    GenerationOutputRecord,
    GenerationOutputStatus,
    GenerationScope,
    IContentRepository,
    IGenerationOutputRepository,
    IGenerationRequestRepository,
    NewContentVersion,
    NewGenerationRequest,
    VersionComparisonRecord,
)
from cloud_content_hub.infrastructure.database.enums import (
    AIGenerationScope,
    AIGenerationStatus,
    AIModelStatus,
    AIProviderStatus,
    ContentLifecycle,
)
from cloud_content_hub.infrastructure.database.models.ai_generation_output import AIGenerationOutput
from cloud_content_hub.infrastructure.database.models.ai_generation_request import (
    AIGenerationRequest,
)
from cloud_content_hub.infrastructure.database.models.ai_model import AIModel
from cloud_content_hub.infrastructure.database.models.ai_provider import AIProvider
from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
from cloud_content_hub.infrastructure.database.models.content_draft import ContentDraft
from cloud_content_hub.infrastructure.database.models.content_version import ContentVersion
from cloud_content_hub.infrastructure.repositories.sqlalchemy.base import SqlAlchemyRepository
from cloud_content_hub.infrastructure.repositories.sqlalchemy.cursor_pagination import (
    apply_keyset_pagination,
    build_keyset_page,
    normalize_sort_token,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import EntityNotFound
from cloud_content_hub.infrastructure.repositories.sqlalchemy.utils import (
    active_row_expression,
    apply_workspace_scope,
    utc_now,
)

_SORTABLE_COLUMNS = frozenset({"updated_at", "created_at"})
_REVIEW_STATUS_KEY = "status"


def _build_tsquery(query: str) -> Any:
    terms = [term for term in query.strip().split() if term]
    if not terms:
        return None
    tsquery_text = " & ".join(f"{term}:*" for term in terms)
    return func.to_tsquery("english", tsquery_text)


def _content_hash(body_text: str | None) -> bytes:
    payload = (body_text or "").encode("utf-8")
    return hashlib.sha256(payload).digest()


def _map_lifecycle(value: str) -> ContentLifecycleStatus:
    return ContentLifecycleStatus(value)


def _map_origin(value: str) -> ContentOrigin:
    return ContentOrigin(value)


def _map_generation_scope(value: GenerationScope) -> str:
    return AIGenerationScope(value.value).value


def _map_output_status(metadata: dict[str, Any]) -> GenerationOutputStatus:
    raw_status = metadata.get(_REVIEW_STATUS_KEY)
    if raw_status == GenerationOutputStatus.APPROVED.value:
        return GenerationOutputStatus.APPROVED
    if raw_status == GenerationOutputStatus.REJECTED.value:
        return GenerationOutputStatus.REJECTED
    return GenerationOutputStatus.PENDING


class SqlAlchemyContentRepository(IContentRepository):
    """Persists and queries content aggregates via SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._assets = SqlAlchemyRepository(
            session,
            ContentAsset,
            entity_name="ContentAsset",
            workspace_scoped=True,
            sortable_columns=_SORTABLE_COLUMNS,
        )
        self._drafts = SqlAlchemyRepository(
            session,
            ContentDraft,
            entity_name="ContentDraft",
            workspace_scoped=True,
        )
        self._versions = SqlAlchemyRepository(
            session,
            ContentVersion,
            entity_name="ContentVersion",
            workspace_scoped=True,
        )

    async def get_by_id(self, *, workspace_id: UUID, content_id: UUID) -> ContentRecord | None:
        asset = await self._load_content_graph(content_id, workspace_id=workspace_id)
        if asset is None:
            return None
        return await self._to_record(asset)

    async def get_deleted_by_id(
        self, *, workspace_id: UUID, content_id: UUID
    ) -> ContentRecord | None:
        statement = (
            select(ContentAsset)
            .options(selectinload(ContentAsset.draft), selectinload(ContentAsset.versions))
            .where(
                ContentAsset.id == content_id,
                ContentAsset.workspace_id == workspace_id,
                ContentAsset.deleted_at.is_not(None),
            )
        )
        asset = (await self._session.scalars(statement)).first()
        if asset is None:
            return None
        return await self._to_record(asset, is_deleted=True)

    async def get_version_by_id(
        self,
        *,
        workspace_id: UUID,
        version_id: UUID,
    ) -> ContentVersionRecord | None:
        version = await self._versions.get_by_id(version_id, workspace_id=workspace_id)
        if version is None:
            return None
        return self._to_version_record(version)

    async def get_version_detail_by_id(
        self,
        *,
        workspace_id: UUID,
        version_id: UUID,
    ) -> ContentVersionDetailRecord | None:
        version = await self._versions.get_by_id(version_id, workspace_id=workspace_id)
        if version is None:
            return None
        return self._to_version_detail(version)

    async def list_versions(
        self,
        *,
        workspace_id: UUID,
        content_id: UUID,
    ) -> tuple[ContentVersionDetailRecord, ...]:
        statement = (
            select(ContentVersion)
            .where(
                ContentVersion.workspace_id == workspace_id,
                ContentVersion.asset_id == content_id,
            )
            .order_by(ContentVersion.version_number.asc())
        )
        active = active_row_expression(ContentVersion)
        if active is not None:
            statement = statement.where(active)
        result = await self._session.scalars(statement)
        return tuple(self._to_version_detail(version) for version in result.all())

    async def compare_versions(
        self,
        *,
        workspace_id: UUID,
        source_version_id: UUID,
        target_version_id: UUID,
    ) -> VersionComparisonRecord | None:
        source = await self.get_version_detail_by_id(
            workspace_id=workspace_id,
            version_id=source_version_id,
        )
        target = await self.get_version_detail_by_id(
            workspace_id=workspace_id,
            version_id=target_version_id,
        )
        if source is None or target is None:
            return None
        if source.asset_id != target.asset_id:
            return None
        return VersionComparisonRecord(
            source_version_id=source.id,
            target_version_id=target.id,
            title_changed=source.title != target.title,
            body_changed=source.body_text != target.body_text,
            metadata_changed=source.metadata != target.metadata,
            source_title=source.title,
            target_title=target.title,
            source_body_text=source.body_text,
            target_body_text=target.body_text,
        )

    async def search(self, criteria: ContentSearchCriteria) -> ContentSearchPage:
        return await self._search_page(
            workspace_id=criteria.workspace_id,
            query=criteria.query,
            lifecycle_statuses=criteria.lifecycle_statuses,
            origins=criteria.origins,
            cursor=criteria.cursor,
            limit=criteria.limit,
            sort=criteria.sort,
        )

    async def list_content(
        self,
        *,
        workspace_id: UUID,
        lifecycle_statuses: frozenset[ContentLifecycleStatus],
        origins: frozenset[ContentOrigin],
        cursor: str | None,
        limit: int,
        sort: str,
    ) -> ContentSearchPage:
        return await self._search_page(
            workspace_id=workspace_id,
            query=None,
            lifecycle_statuses=lifecycle_statuses,
            origins=origins,
            cursor=cursor,
            limit=limit,
            sort=sort,
        )

    async def soft_delete(
        self,
        *,
        workspace_id: UUID,
        content_id: UUID,
        expected_version: int,
        updated_by: UUID,
    ) -> None:
        await self._assets.soft_delete(
            content_id,
            expected_version=expected_version,
            updated_by=updated_by,
            workspace_id=workspace_id,
        )

    async def restore(
        self,
        *,
        workspace_id: UUID,
        content_id: UUID,
        expected_version: int,
        updated_by: UUID,
    ) -> ContentRecord:
        restored = await self._assets.restore(
            content_id,
            expected_version=expected_version,
            updated_by=updated_by,
            workspace_id=workspace_id,
        )
        asset = await self._load_content_graph(restored.id, workspace_id=workspace_id)
        assert asset is not None
        return await self._to_record(asset)

    async def update_lifecycle_status(
        self,
        *,
        workspace_id: UUID,
        content_id: UUID,
        lifecycle_status: ContentLifecycleStatus,
        expected_version: int,
        updated_by: UUID,
    ) -> ContentRecord:
        asset = await self._assets.get_by_id(content_id, workspace_id=workspace_id)
        if asset is None:
            raise EntityNotFound(f"ContentAsset {content_id} was not found.")
        asset.lifecycle_status = lifecycle_status.value
        asset.updated_by = updated_by
        updated = await self._assets.update(asset, expected_version=expected_version)
        asset = await self._load_content_graph(updated.id, workspace_id=workspace_id)
        assert asset is not None
        return await self._to_record(asset)

    async def duplicate(self, request: DuplicateContentInput) -> ContentRecord:
        source = await self._load_content_graph(
            request.source_content_id,
            workspace_id=request.workspace_id,
        )
        if source is None:
            raise EntityNotFound(f"ContentAsset {request.source_content_id} was not found.")

        new_asset_id = uuid4()
        copied_asset = ContentAsset(
            id=new_asset_id,
            workspace_id=request.workspace_id,
            asset_type=source.asset_type,
            title=request.title or source.title,
            summary=source.summary,
            owner_id=source.owner_id,
            project_id=request.project_id if request.project_id is not None else source.project_id,
            folder_id=request.folder_id if request.folder_id is not None else source.folder_id,
            lifecycle_status=ContentLifecycle.DRAFT.value,
            is_favorite=False,
            created_by=request.created_by,
            updated_by=request.created_by,
        )
        created_asset = await self._assets.create(copied_asset)

        source_draft = source.draft
        draft = ContentDraft(
            id=uuid4(),
            workspace_id=request.workspace_id,
            asset_id=new_asset_id,
            base_version_id=source_draft.base_version_id if source_draft is not None else None,
            body_text=source_draft.body_text if source_draft is not None else None,
            body_rich=source_draft.body_rich if source_draft is not None else None,
            metadata_=dict(source_draft.metadata_) if source_draft is not None else {},
            created_by=request.created_by,
            updated_by=request.created_by,
        )
        self._session.add(draft)
        await self._session.flush()

        created_asset.draft = draft
        return await self._to_record(created_asset)

    async def create_version(self, request: NewContentVersion) -> ContentVersionDetailRecord:
        next_number = await self._next_version_number(
            workspace_id=request.workspace_id,
            asset_id=request.asset_id,
        )
        now = utc_now()
        version = ContentVersion(
            id=uuid4(),
            workspace_id=request.workspace_id,
            asset_id=request.asset_id,
            version_number=next_number,
            title=request.title,
            body_text=request.body_text,
            body_rich=request.body_rich,
            metadata_=dict(request.metadata),
            origin=request.origin.value,
            source_version_id=request.source_version_id,
            content_hash=_content_hash(request.body_text),
            change_summary=request.change_summary,
            created_by=request.created_by,
            updated_by=request.created_by,
            created_at=now,
            updated_at=now,
            version=1,
        )
        created = await self._versions.create(version)
        return self._to_version_detail(created)

    async def set_current_version(
        self,
        *,
        workspace_id: UUID,
        content_id: UUID,
        version_id: UUID,
        expected_version: int,
        updated_by: UUID,
    ) -> ContentRecord:
        asset = await self._assets.get_by_id(content_id, workspace_id=workspace_id)
        if asset is None:
            raise EntityNotFound(f"ContentAsset {content_id} was not found.")

        version = await self._versions.get_by_id(version_id, workspace_id=workspace_id)
        if version is None or version.asset_id != content_id:
            raise EntityNotFound(f"ContentVersion {version_id} was not found.")

        draft = await self._get_active_draft(workspace_id=workspace_id, asset_id=content_id)
        if draft is None:
            draft = ContentDraft(
                id=uuid4(),
                workspace_id=workspace_id,
                asset_id=content_id,
                created_by=updated_by,
                updated_by=updated_by,
            )
            self._session.add(draft)
            await self._session.flush()

        draft.base_version_id = version_id
        draft.updated_by = updated_by
        self._session.add(draft)

        asset.updated_by = updated_by
        updated_asset = await self._assets.update(asset, expected_version=expected_version)
        updated_asset.draft = draft
        return await self._to_record(updated_asset)

    async def _search_page(
        self,
        *,
        workspace_id: UUID,
        query: str | None,
        lifecycle_statuses: frozenset[ContentLifecycleStatus],
        origins: frozenset[ContentOrigin],
        cursor: str | None,
        limit: int,
        sort: str,
    ) -> ContentSearchPage:
        sort_column = normalize_sort_token(sort, allowed_columns=_SORTABLE_COLUMNS)
        origin_version = aliased(ContentVersion)

        statement = (
            select(ContentAsset)
            .outerjoin(
                ContentDraft,
                (ContentDraft.asset_id == ContentAsset.id)
                & (ContentDraft.workspace_id == ContentAsset.workspace_id)
                & ContentDraft.deleted_at.is_(None),
            )
            .outerjoin(
                origin_version,
                (origin_version.id == ContentDraft.base_version_id)
                & (origin_version.workspace_id == ContentDraft.workspace_id)
                & origin_version.deleted_at.is_(None),
            )
        )
        statement = apply_workspace_scope(statement, ContentAsset, workspace_id)
        active = active_row_expression(ContentAsset)
        if active is not None:
            statement = statement.where(active)

        if query:
            tsquery = _build_tsquery(query)
            if tsquery is not None:
                statement = statement.where(ContentAsset.search_document.op("@@")(tsquery))

        if lifecycle_statuses:
            statement = statement.where(
                ContentAsset.lifecycle_status.in_([status.value for status in lifecycle_statuses])
            )
        if origins:
            statement = statement.where(
                origin_version.origin.in_([origin.value for origin in origins])
            )

        statement = apply_keyset_pagination(
            statement,
            ContentAsset,
            sort_column=sort_column,
            cursor=cursor,
            limit=limit,
        )
        result = await self._session.scalars(statement)
        rows = list(result.unique().all())
        page_rows, next_cursor, has_more = build_keyset_page(
            rows,
            limit=limit,
            sort_column=sort_column,
            sort_value_getter=lambda row: getattr(row, sort_column.name),
            id_getter=lambda row: cast(UUID, row.id),
        )
        items = tuple([await self._to_record(row) for row in page_rows])
        return ContentSearchPage(items=items, next_cursor=next_cursor, has_more=has_more)

    async def _load_content_graph(
        self,
        content_id: UUID,
        *,
        workspace_id: UUID,
    ) -> ContentAsset | None:
        statement = (
            select(ContentAsset)
            .options(selectinload(ContentAsset.draft), selectinload(ContentAsset.versions))
            .where(ContentAsset.id == content_id, ContentAsset.workspace_id == workspace_id)
        )
        active = active_row_expression(ContentAsset)
        if active is not None:
            statement = statement.where(active)
        return (await self._session.scalars(statement)).first()

    async def _get_active_draft(
        self,
        *,
        workspace_id: UUID,
        asset_id: UUID,
    ) -> ContentDraft | None:
        statement = select(ContentDraft).where(
            ContentDraft.workspace_id == workspace_id,
            ContentDraft.asset_id == asset_id,
        )
        active = active_row_expression(ContentDraft)
        if active is not None:
            statement = statement.where(active)
        return (await self._session.scalars(statement)).first()

    async def _next_version_number(self, *, workspace_id: UUID, asset_id: UUID) -> int:
        statement = select(func.max(ContentVersion.version_number)).where(
            ContentVersion.workspace_id == workspace_id,
            ContentVersion.asset_id == asset_id,
        )
        active = active_row_expression(ContentVersion)
        if active is not None:
            statement = statement.where(active)
        current = await self._session.scalar(statement)
        return int(current or 0) + 1

    async def _resolve_origin(self, draft: ContentDraft | None) -> ContentOrigin:
        if draft is None or draft.base_version_id is None:
            return ContentOrigin.USER
        statement = select(ContentVersion.origin).where(
            ContentVersion.workspace_id == draft.workspace_id,
            ContentVersion.id == draft.base_version_id,
        )
        active = active_row_expression(ContentVersion)
        if active is not None:
            statement = statement.where(active)
        origin = await self._session.scalar(statement)
        if origin is None:
            return ContentOrigin.USER
        return _map_origin(origin)

    async def _to_record(self, asset: ContentAsset, *, is_deleted: bool = False) -> ContentRecord:
        draft = asset.draft
        if draft is None:
            draft = await self._get_active_draft(workspace_id=asset.workspace_id, asset_id=asset.id)

        origin = await self._resolve_origin(draft)
        metadata = dict(draft.metadata_) if draft is not None else {}
        return ContentRecord(
            id=asset.id,
            workspace_id=asset.workspace_id,
            version=asset.version,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            asset_id=asset.id,
            title=asset.title,
            body_text=draft.body_text if draft is not None else None,
            body_rich=draft.body_rich if draft is not None else None,
            metadata=metadata,
            lifecycle_status=_map_lifecycle(asset.lifecycle_status),
            origin=origin,
            content_version_id=draft.base_version_id if draft is not None else None,
            is_deleted=is_deleted or asset.deleted_at is not None,
        )

    @staticmethod
    def _to_version_record(version: ContentVersion) -> ContentVersionRecord:
        return ContentVersionRecord(
            id=version.id,
            workspace_id=version.workspace_id,
            asset_id=version.asset_id,
            version_number=version.version_number,
            is_immutable=True,
            origin=_map_origin(version.origin),
        )

    @staticmethod
    def _to_version_detail(version: ContentVersion) -> ContentVersionDetailRecord:
        created_by = version.created_by
        if created_by is None:
            raise EntityNotFound(f"ContentVersion {version.id} is missing created_by.")
        return ContentVersionDetailRecord(
            id=version.id,
            workspace_id=version.workspace_id,
            asset_id=version.asset_id,
            version_number=version.version_number,
            title=version.title,
            body_text=version.body_text,
            body_rich=version.body_rich,
            metadata=dict(version.metadata_),
            origin=_map_origin(version.origin),
            source_version_id=version.source_version_id,
            change_summary=version.change_summary,
            created_at=version.created_at,
            created_by=created_by,
        )


class SqlAlchemyGenerationRequestRepository(IGenerationRequestRepository):
    """Persists AI generation requests via SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._requests = SqlAlchemyRepository(
            session,
            AIGenerationRequest,
            entity_name="AIGenerationRequest",
            workspace_scoped=True,
        )

    async def create(self, request: NewGenerationRequest) -> UUID:
        parameters = dict(request.parameters)
        if request.selection_text is not None:
            parameters["selection_text"] = request.selection_text

        entity = AIGenerationRequest(
            id=uuid4(),
            workspace_id=request.workspace_id,
            asset_id=request.asset_id,
            source_version_id=request.source_version_id,
            model_id=request.model_id,
            prompt_template_id=request.prompt_template_id,
            brand_profile_id=request.brand_profile_id,
            status=AIGenerationStatus.QUEUED.value,
            scope=_map_generation_scope(request.scope),
            parameters=parameters,
            idempotency_key=request.idempotency_key or str(uuid4()),
            created_by=request.created_by,
            updated_by=request.created_by,
        )
        created = await self._requests.create(entity)
        return created.id

    async def validate_model_enabled(self, *, workspace_id: UUID, model_id: UUID) -> bool:
        del workspace_id
        statement = (
            select(AIModel.id)
            .join(AIProvider, AIProvider.id == AIModel.provider_id)
            .where(
                AIModel.id == model_id,
                AIModel.status == AIModelStatus.ENABLED.value,
                AIProvider.status == AIProviderStatus.ENABLED.value,
                AIModel.deleted_at.is_(None),
                AIProvider.deleted_at.is_(None),
            )
        )
        result = await self._session.scalar(statement)
        return result is not None


class SqlAlchemyGenerationOutputRepository(IGenerationOutputRepository):
    """Persists AI generation output review state via SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._outputs = SqlAlchemyRepository(
            session,
            AIGenerationOutput,
            entity_name="AIGenerationOutput",
            workspace_scoped=True,
        )

    async def get_by_id(
        self,
        *,
        workspace_id: UUID,
        output_id: UUID,
    ) -> GenerationOutputRecord | None:
        output = await self._outputs.get_by_id(output_id, workspace_id=workspace_id)
        if output is None:
            return None
        return self._to_record(output)

    async def approve(
        self,
        *,
        workspace_id: UUID,
        output_id: UUID,
        updated_by: UUID,
    ) -> GenerationOutputRecord:
        del updated_by
        output = await self._outputs.get_by_id(output_id, workspace_id=workspace_id)
        if output is None:
            raise EntityNotFound(f"AIGenerationOutput {output_id} was not found.")
        metadata = dict(output.output_metadata)
        metadata[_REVIEW_STATUS_KEY] = GenerationOutputStatus.APPROVED.value
        await self._update_review_metadata(
            workspace_id=workspace_id,
            output_id=output_id,
            metadata=metadata,
        )
        output.output_metadata = metadata
        return self._to_record(output)

    async def reject(
        self,
        *,
        workspace_id: UUID,
        output_id: UUID,
        updated_by: UUID,
        reason: str | None,
    ) -> GenerationOutputRecord:
        del updated_by
        output = await self._outputs.get_by_id(output_id, workspace_id=workspace_id)
        if output is None:
            raise EntityNotFound(f"AIGenerationOutput {output_id} was not found.")
        metadata = dict(output.output_metadata)
        metadata[_REVIEW_STATUS_KEY] = GenerationOutputStatus.REJECTED.value
        if reason is not None:
            metadata["rejection_reason"] = reason
        await self._update_review_metadata(
            workspace_id=workspace_id,
            output_id=output_id,
            metadata=metadata,
        )
        output.output_metadata = metadata
        return self._to_record(output)

    async def _update_review_metadata(
        self,
        *,
        workspace_id: UUID,
        output_id: UUID,
        metadata: dict[str, Any],
    ) -> None:
        statement = (
            update(AIGenerationOutput)
            .where(
                AIGenerationOutput.id == output_id,
                AIGenerationOutput.workspace_id == workspace_id,
                AIGenerationOutput.deleted_at.is_(None),
            )
            .values(output_metadata=metadata)
        )
        result = await self._session.execute(statement)
        if int(cast(CursorResult[Any], result).rowcount or 0) == 0:
            raise EntityNotFound(f"AIGenerationOutput {output_id} was not found.")

    @staticmethod
    def _to_record(output: AIGenerationOutput) -> GenerationOutputRecord:
        metadata = dict(output.output_metadata)
        return GenerationOutputRecord(
            id=output.id,
            workspace_id=output.workspace_id,
            generation_request_id=output.generation_request_id,
            sequence_no=output.sequence_no,
            platform_id=output.platform_id,
            output_text=output.output_text,
            output_metadata=metadata,
            safety_status=output.safety_status,
            materialized_version_id=output.materialized_version_id,
            status=_map_output_status(metadata),
            created_at=output.created_at,
        )
