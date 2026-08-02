"""SQLAlchemy implementation of the asset repository port."""

from __future__ import annotations

from typing import Any, cast
from uuid import UUID, uuid4

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from cloud_content_hub.application.assets.interfaces.asset_repository import (
    AssetDetailsRecord,
    AssetLifecycleStatus,
    AssetMediaRecord,
    AssetRecord,
    AssetSearchCriteria,
    AssetSearchPage,
    AssetType,
    AssetUsageRecord,
    IAssetRepository,
    NewAsset,
    ScanStatus,
)
from cloud_content_hub.infrastructure.database.enums import (
    ContentLifecycle,
    StorageObjectPurpose,
)
from cloud_content_hub.infrastructure.database.enums import (
    ScanStatus as DbScanStatus,
)
from cloud_content_hub.infrastructure.database.models.asset_storage_object import AssetStorageObject
from cloud_content_hub.infrastructure.database.models.asset_tag import AssetTag
from cloud_content_hub.infrastructure.database.models.collection_item import CollectionItem
from cloud_content_hub.infrastructure.database.models.comment import Comment
from cloud_content_hub.infrastructure.database.models.content_asset import ContentAsset
from cloud_content_hub.infrastructure.database.models.content_draft import ContentDraft
from cloud_content_hub.infrastructure.database.models.content_relation import ContentRelation
from cloud_content_hub.infrastructure.database.models.content_version import ContentVersion
from cloud_content_hub.infrastructure.database.models.publication import Publication
from cloud_content_hub.infrastructure.database.models.storage_object import StorageObject
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
)

_SORTABLE_COLUMNS = frozenset({"updated_at", "created_at"})
_SOURCE_PURPOSE = StorageObjectPurpose.SOURCE.value


def _hex_to_bytes(value: str) -> bytes:
    return bytes.fromhex(value)


def _bytes_to_hex(value: bytes) -> str:
    return value.hex()


def _map_scan_status(value: str) -> ScanStatus:
    return ScanStatus(value)


def _map_db_scan_status(value: ScanStatus) -> str:
    return DbScanStatus(value.value).value


def _map_asset_type(value: str) -> AssetType:
    return AssetType(value)


def _map_lifecycle_status(value: str) -> AssetLifecycleStatus:
    return AssetLifecycleStatus(value)


def _build_tsquery(query: str) -> Any:
    terms = [term for term in query.strip().split() if term]
    if not terms:
        return None
    tsquery_text = " & ".join(f"{term}:*" for term in terms)
    return func.to_tsquery("english", tsquery_text)


class SqlAlchemyAssetRepository(IAssetRepository):
    """Persists and queries content assets via SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._assets = SqlAlchemyRepository(
            session,
            ContentAsset,
            entity_name="ContentAsset",
            workspace_scoped=True,
            sortable_columns=_SORTABLE_COLUMNS,
        )

    async def get_by_id(self, *, workspace_id: UUID, asset_id: UUID) -> AssetRecord | None:
        asset = await self._assets.get_by_id(asset_id, workspace_id=workspace_id)
        if asset is None:
            return None
        return await self._to_record(asset)

    async def get_deleted_by_id(self, *, workspace_id: UUID, asset_id: UUID) -> AssetRecord | None:
        asset = await self._assets.get_by_id(
            asset_id,
            workspace_id=workspace_id,
            include_deleted=True,
        )
        if asset is None or asset.deleted_at is None:
            return None
        return await self._to_record(asset, is_deleted=True)

    async def create(self, asset: NewAsset) -> AssetRecord:
        entity = ContentAsset(
            id=uuid4(),
            workspace_id=asset.workspace_id,
            asset_type=asset.asset_type.value,
            title=asset.title,
            summary=asset.summary,
            owner_id=asset.owner_id,
            project_id=asset.project_id,
            folder_id=asset.folder_id,
            lifecycle_status=ContentLifecycle.DRAFT.value,
            created_by=asset.created_by,
            updated_by=asset.created_by,
        )
        created = await self._assets.create(entity)
        return await self._to_record(created)

    async def attach_media(
        self,
        *,
        workspace_id: UUID,
        asset_id: UUID,
        media: AssetMediaRecord,
        expected_version: int,
        updated_by: UUID,
    ) -> AssetRecord:
        asset = await self._assets.get_by_id(asset_id, workspace_id=workspace_id)
        if asset is None:
            raise EntityNotFound(f"ContentAsset {asset_id} was not found.")

        await self._session.execute(
            delete(AssetStorageObject).where(
                AssetStorageObject.workspace_id == workspace_id,
                AssetStorageObject.asset_id == asset_id,
                AssetStorageObject.purpose == _SOURCE_PURPOSE,
            )
        )

        object_key = media.storage_blob_name or (
            f"assets/{asset_id.hex}/{media.filename or media.checksum_sha256}"
        )
        storage_object = StorageObject(
            id=uuid4(),
            workspace_id=workspace_id,
            object_key=object_key,
            container_name=media.storage_container or "assets",
            mime_type=media.mime_type,
            byte_size=media.byte_size,
            checksum_sha256=_hex_to_bytes(media.checksum_sha256),
            scan_status=_map_db_scan_status(media.scan_status),
            created_by=updated_by,
            updated_by=updated_by,
        )
        self._session.add(storage_object)
        await self._session.flush()

        link = AssetStorageObject(
            id=uuid4(),
            workspace_id=workspace_id,
            asset_id=asset_id,
            storage_object_id=storage_object.id,
            purpose=_SOURCE_PURPOSE,
            created_by=updated_by,
            updated_by=updated_by,
        )
        self._session.add(link)

        asset.updated_by = updated_by
        updated = await self._assets.update(asset, expected_version=expected_version)
        return await self._to_record(updated)

    async def soft_delete(
        self,
        *,
        workspace_id: UUID,
        asset_id: UUID,
        expected_version: int,
        updated_by: UUID,
    ) -> None:
        await self._assets.soft_delete(
            asset_id,
            expected_version=expected_version,
            updated_by=updated_by,
            workspace_id=workspace_id,
        )

    async def restore(
        self,
        *,
        workspace_id: UUID,
        asset_id: UUID,
        expected_version: int,
        updated_by: UUID,
    ) -> AssetRecord:
        restored = await self._assets.restore(
            asset_id,
            expected_version=expected_version,
            updated_by=updated_by,
            workspace_id=workspace_id,
        )
        return await self._to_record(restored)

    async def update_lifecycle_status(
        self,
        *,
        workspace_id: UUID,
        asset_id: UUID,
        lifecycle_status: AssetLifecycleStatus,
        expected_version: int,
        updated_by: UUID,
    ) -> AssetRecord:
        asset = await self._assets.get_by_id(asset_id, workspace_id=workspace_id)
        if asset is None:
            raise EntityNotFound(f"ContentAsset {asset_id} was not found.")
        asset.lifecycle_status = lifecycle_status.value
        asset.updated_by = updated_by
        updated = await self._assets.update(asset, expected_version=expected_version)
        return await self._to_record(updated)

    async def move(
        self,
        *,
        workspace_id: UUID,
        asset_id: UUID,
        project_id: UUID | None,
        folder_id: UUID | None,
        expected_version: int,
        updated_by: UUID,
    ) -> AssetRecord:
        asset = await self._assets.get_by_id(asset_id, workspace_id=workspace_id)
        if asset is None:
            raise EntityNotFound(f"ContentAsset {asset_id} was not found.")
        asset.project_id = project_id
        asset.folder_id = folder_id
        asset.updated_by = updated_by
        updated = await self._assets.update(asset, expected_version=expected_version)
        return await self._to_record(updated)

    async def copy(
        self,
        *,
        workspace_id: UUID,
        source_asset_id: UUID,
        title: str,
        project_id: UUID | None,
        folder_id: UUID | None,
        created_by: UUID,
    ) -> AssetRecord:
        source = await self._load_asset_graph(source_asset_id, workspace_id=workspace_id)
        if source is None:
            raise EntityNotFound(f"ContentAsset {source_asset_id} was not found.")

        new_asset_id = uuid4()
        copied = ContentAsset(
            id=new_asset_id,
            workspace_id=workspace_id,
            asset_type=source.asset_type,
            title=title,
            summary=source.summary,
            owner_id=source.owner_id,
            project_id=project_id if project_id is not None else source.project_id,
            folder_id=folder_id if folder_id is not None else source.folder_id,
            lifecycle_status=ContentLifecycle.DRAFT.value,
            is_favorite=False,
            created_by=created_by,
            updated_by=created_by,
        )
        created = await self._assets.create(copied)

        if source.draft is not None:
            draft = ContentDraft(
                id=uuid4(),
                workspace_id=workspace_id,
                asset_id=new_asset_id,
                base_version_id=source.draft.base_version_id,
                body_text=source.draft.body_text,
                body_rich=source.draft.body_rich,
                metadata_=dict(source.draft.metadata_),
                created_by=created_by,
                updated_by=created_by,
            )
            self._session.add(draft)
            await self._session.flush()

        return await self._to_record(created)

    async def set_tags(
        self,
        *,
        workspace_id: UUID,
        asset_id: UUID,
        tag_ids: frozenset[UUID],
        expected_version: int,
        updated_by: UUID,
    ) -> AssetRecord:
        asset = await self._assets.get_by_id(asset_id, workspace_id=workspace_id)
        if asset is None:
            raise EntityNotFound(f"ContentAsset {asset_id} was not found.")

        await self._session.execute(
            delete(AssetTag).where(
                AssetTag.workspace_id == workspace_id,
                AssetTag.asset_id == asset_id,
            )
        )
        if tag_ids:
            self._session.add_all(
                [
                    AssetTag(
                        id=uuid4(),
                        workspace_id=workspace_id,
                        asset_id=asset_id,
                        tag_id=tag_id,
                        created_by=updated_by,
                        updated_by=updated_by,
                    )
                    for tag_id in sorted(tag_ids)
                ]
            )

        asset.updated_by = updated_by
        updated = await self._assets.update(asset, expected_version=expected_version)
        return await self._to_record(updated)

    async def find_by_checksum(
        self,
        *,
        workspace_id: UUID,
        checksum_sha256: str,
        byte_size: int,
    ) -> AssetRecord | None:
        checksum = _hex_to_bytes(checksum_sha256)
        statement = (
            select(ContentAsset)
            .join(
                AssetStorageObject,
                (AssetStorageObject.asset_id == ContentAsset.id)
                & (AssetStorageObject.workspace_id == ContentAsset.workspace_id),
            )
            .join(
                StorageObject,
                (StorageObject.id == AssetStorageObject.storage_object_id)
                & (StorageObject.workspace_id == AssetStorageObject.workspace_id),
            )
            .where(
                ContentAsset.workspace_id == workspace_id,
                AssetStorageObject.purpose == _SOURCE_PURPOSE,
                StorageObject.checksum_sha256 == checksum,
                StorageObject.byte_size == byte_size,
            )
        )
        active = active_row_expression(ContentAsset)
        if active is not None:
            statement = statement.where(active)
        storage_active = active_row_expression(StorageObject)
        if storage_active is not None:
            statement = statement.where(storage_active)

        result = await self._session.scalars(statement)
        asset = result.first()
        if asset is None:
            return None
        return await self._to_record(asset)

    async def find_by_filename(
        self,
        *,
        workspace_id: UUID,
        filename: str,
        asset_type: AssetType,
    ) -> AssetRecord | None:
        statement = (
            select(ContentAsset)
            .join(
                AssetStorageObject,
                (AssetStorageObject.asset_id == ContentAsset.id)
                & (AssetStorageObject.workspace_id == ContentAsset.workspace_id),
            )
            .join(
                StorageObject,
                (StorageObject.id == AssetStorageObject.storage_object_id)
                & (StorageObject.workspace_id == AssetStorageObject.workspace_id),
            )
            .where(
                ContentAsset.workspace_id == workspace_id,
                ContentAsset.asset_type == asset_type.value,
                AssetStorageObject.purpose == _SOURCE_PURPOSE,
                StorageObject.object_key.like(f"%/{filename}"),
            )
        )
        active = active_row_expression(ContentAsset)
        if active is not None:
            statement = statement.where(active)
        storage_active = active_row_expression(StorageObject)
        if storage_active is not None:
            statement = statement.where(storage_active)

        result = await self._session.scalars(statement)
        asset = result.first()
        if asset is None:
            return None
        return await self._to_record(asset)

    async def get_details(self, *, workspace_id: UUID, asset_id: UUID) -> AssetDetailsRecord | None:
        asset = await self.get_by_id(workspace_id=workspace_id, asset_id=asset_id)
        if asset is None:
            return None

        version_count = await self._count_related(
            ContentVersion,
            workspace_id=workspace_id,
            asset_id=asset_id,
        )
        publication_count = await self._count_related(
            Publication,
            workspace_id=workspace_id,
            asset_id=asset_id,
        )
        collection_count = await self._count_related(
            CollectionItem,
            workspace_id=workspace_id,
            asset_id=asset_id,
        )
        comment_count = await self._count_related(
            Comment,
            workspace_id=workspace_id,
            asset_id=asset_id,
        )
        return AssetDetailsRecord(
            asset=asset,
            version_count=version_count,
            publication_count=publication_count,
            collection_count=collection_count,
            comment_count=comment_count,
        )

    async def get_usage(self, *, workspace_id: UUID, asset_id: UUID) -> AssetUsageRecord | None:
        asset = await self._assets.get_by_id(asset_id, workspace_id=workspace_id)
        if asset is None:
            return None

        publication_count = await self._count_related(
            Publication,
            workspace_id=workspace_id,
            asset_id=asset_id,
        )
        collection_count = await self._count_related(
            CollectionItem,
            workspace_id=workspace_id,
            asset_id=asset_id,
        )
        relation_count = await self._count_relations(workspace_id=workspace_id, asset_id=asset_id)

        blocking_reasons: list[str] = []
        if publication_count:
            blocking_reasons.append("Asset is referenced by publications.")
        if collection_count:
            blocking_reasons.append("Asset is referenced by collections.")
        if relation_count:
            blocking_reasons.append("Asset is referenced by content relations.")

        return AssetUsageRecord(
            asset_id=asset_id,
            publication_count=publication_count,
            collection_count=collection_count,
            relation_count=relation_count,
            can_delete=not blocking_reasons,
            blocking_reasons=tuple(blocking_reasons),
        )

    async def search(self, criteria: AssetSearchCriteria) -> AssetSearchPage:
        return await self._search_page(
            workspace_id=criteria.workspace_id,
            query=criteria.query,
            asset_types=criteria.asset_types,
            lifecycle_statuses=criteria.lifecycle_statuses,
            owner_id=criteria.owner_id,
            project_id=criteria.project_id,
            folder_id=criteria.folder_id,
            cursor=criteria.cursor,
            limit=criteria.limit,
            sort=criteria.sort,
        )

    async def list_assets(
        self,
        *,
        workspace_id: UUID,
        asset_types: frozenset[AssetType],
        lifecycle_statuses: frozenset[AssetLifecycleStatus],
        owner_id: UUID | None,
        project_id: UUID | None,
        folder_id: UUID | None,
        cursor: str | None,
        limit: int,
        sort: str,
    ) -> AssetSearchPage:
        return await self._search_page(
            workspace_id=workspace_id,
            query=None,
            asset_types=asset_types,
            lifecycle_statuses=lifecycle_statuses,
            owner_id=owner_id,
            project_id=project_id,
            folder_id=folder_id,
            cursor=cursor,
            limit=limit,
            sort=sort,
        )

    async def _search_page(
        self,
        *,
        workspace_id: UUID,
        query: str | None,
        asset_types: frozenset[AssetType],
        lifecycle_statuses: frozenset[AssetLifecycleStatus],
        owner_id: UUID | None,
        project_id: UUID | None,
        folder_id: UUID | None,
        cursor: str | None,
        limit: int,
        sort: str,
    ) -> AssetSearchPage:
        sort_column = normalize_sort_token(sort, allowed_columns=_SORTABLE_COLUMNS)
        statement = select(ContentAsset)
        statement = apply_workspace_scope(statement, ContentAsset, workspace_id)
        active = active_row_expression(ContentAsset)
        if active is not None:
            statement = statement.where(active)

        if query:
            tsquery = _build_tsquery(query)
            if tsquery is not None:
                statement = statement.where(ContentAsset.search_document.op("@@")(tsquery))

        if asset_types:
            statement = statement.where(
                ContentAsset.asset_type.in_([asset_type.value for asset_type in asset_types])
            )
        if lifecycle_statuses:
            statement = statement.where(
                ContentAsset.lifecycle_status.in_([status.value for status in lifecycle_statuses])
            )
        if owner_id is not None:
            statement = statement.where(ContentAsset.owner_id == owner_id)
        if project_id is not None:
            statement = statement.where(ContentAsset.project_id == project_id)
        if folder_id is not None:
            statement = statement.where(ContentAsset.folder_id == folder_id)

        statement = apply_keyset_pagination(
            statement,
            ContentAsset,
            sort_column=sort_column,
            cursor=cursor,
            limit=limit,
        )
        result = await self._session.scalars(statement)
        rows = list(result.all())
        page_rows, next_cursor, has_more = build_keyset_page(
            rows,
            limit=limit,
            sort_column=sort_column,
            sort_value_getter=lambda row: getattr(row, sort_column.name),
            id_getter=lambda row: cast(UUID, row.id),
        )
        items = tuple([await self._to_record(row) for row in page_rows])
        return AssetSearchPage(items=items, next_cursor=next_cursor, has_more=has_more)

    async def _load_asset_graph(
        self,
        asset_id: UUID,
        *,
        workspace_id: UUID,
    ) -> ContentAsset | None:
        statement = (
            select(ContentAsset)
            .options(selectinload(ContentAsset.draft))
            .where(ContentAsset.id == asset_id, ContentAsset.workspace_id == workspace_id)
        )
        active = active_row_expression(ContentAsset)
        if active is not None:
            statement = statement.where(active)
        result = await self._session.scalars(statement)
        return result.first()

    async def _count_related(
        self,
        model: type[Any],
        *,
        workspace_id: UUID,
        asset_id: UUID,
    ) -> int:
        statement = (
            select(func.count())
            .select_from(model)
            .where(
                model.workspace_id == workspace_id,
                model.asset_id == asset_id,
            )
        )
        active = active_row_expression(model)
        if active is not None:
            statement = statement.where(active)
        result = await self._session.scalar(statement)
        return int(result or 0)

    async def _count_relations(self, *, workspace_id: UUID, asset_id: UUID) -> int:
        outgoing = (
            select(func.count())
            .select_from(ContentRelation)
            .where(
                ContentRelation.workspace_id == workspace_id,
                ContentRelation.source_asset_id == asset_id,
            )
        )
        incoming = (
            select(func.count())
            .select_from(ContentRelation)
            .where(
                ContentRelation.workspace_id == workspace_id,
                ContentRelation.target_asset_id == asset_id,
            )
        )
        active = active_row_expression(ContentRelation)
        if active is not None:
            outgoing = outgoing.where(active)
            incoming = incoming.where(active)
        outgoing_count = int(await self._session.scalar(outgoing) or 0)
        incoming_count = int(await self._session.scalar(incoming) or 0)
        return outgoing_count + incoming_count

    async def _load_tag_ids(self, *, workspace_id: UUID, asset_id: UUID) -> frozenset[UUID]:
        statement = select(AssetTag.tag_id).where(
            AssetTag.workspace_id == workspace_id,
            AssetTag.asset_id == asset_id,
        )
        active = active_row_expression(AssetTag)
        if active is not None:
            statement = statement.where(active)
        result = await self._session.scalars(statement)
        return frozenset(result.all())

    async def _load_source_media(
        self,
        *,
        workspace_id: UUID,
        asset_id: UUID,
    ) -> AssetMediaRecord | None:
        statement = (
            select(StorageObject, AssetStorageObject)
            .join(
                AssetStorageObject,
                (AssetStorageObject.storage_object_id == StorageObject.id)
                & (AssetStorageObject.workspace_id == StorageObject.workspace_id),
            )
            .where(
                AssetStorageObject.workspace_id == workspace_id,
                AssetStorageObject.asset_id == asset_id,
                AssetStorageObject.purpose == _SOURCE_PURPOSE,
            )
            .order_by(AssetStorageObject.position.asc())
            .limit(1)
        )
        storage_active = active_row_expression(StorageObject)
        if storage_active is not None:
            statement = statement.where(storage_active)
        link_active = active_row_expression(AssetStorageObject)
        if link_active is not None:
            statement = statement.where(link_active)

        row = (await self._session.execute(statement)).first()
        if row is None:
            return None

        storage_object, _link = row
        filename = storage_object.object_key.rsplit("/", maxsplit=1)[-1]
        return AssetMediaRecord(
            mime_type=storage_object.mime_type,
            byte_size=storage_object.byte_size,
            checksum_sha256=_bytes_to_hex(storage_object.checksum_sha256),
            scan_status=_map_scan_status(storage_object.scan_status),
            storage_container=storage_object.container_name,
            storage_blob_name=storage_object.object_key,
            filename=filename,
        )

    async def _to_record(self, asset: ContentAsset, *, is_deleted: bool = False) -> AssetRecord:
        media = await self._load_source_media(workspace_id=asset.workspace_id, asset_id=asset.id)
        tag_ids = await self._load_tag_ids(workspace_id=asset.workspace_id, asset_id=asset.id)
        return AssetRecord(
            id=asset.id,
            workspace_id=asset.workspace_id,
            version=asset.version,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
            asset_type=_map_asset_type(asset.asset_type),
            title=asset.title,
            summary=asset.summary,
            lifecycle_status=_map_lifecycle_status(asset.lifecycle_status),
            owner_id=asset.owner_id,
            project_id=asset.project_id,
            folder_id=asset.folder_id,
            is_favorite=asset.is_favorite,
            media=media,
            tag_ids=tag_ids,
            is_deleted=is_deleted or asset.deleted_at is not None,
        )
