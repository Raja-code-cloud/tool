"""Generic SQLAlchemy repository implementation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, cast
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm.exc import StaleDataError

from cloud_content_hub.infrastructure.repositories.sqlalchemy.exceptions import (
    ConcurrencyConflict,
    EntityNotFound,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.filters import RepositoryFilter
from cloud_content_hub.infrastructure.repositories.sqlalchemy.pagination import (
    Page,
    build_page_metadata,
    page_to_offset,
)
from cloud_content_hub.infrastructure.repositories.sqlalchemy.sorting import SortColumn
from cloud_content_hub.infrastructure.repositories.sqlalchemy.specification import Specification
from cloud_content_hub.infrastructure.repositories.sqlalchemy.utils import (
    build_select,
    execute_count,
    has_attribute,
    restore_by_id,
    soft_delete_by_id,
    translate_integrity_error,
    utc_now,
)


class SqlAlchemyRepository[ModelT: DeclarativeBase]:
    """Reusable async repository for SQLAlchemy mapped models."""

    def __init__(
        self,
        session: AsyncSession,
        model: type[ModelT],
        *,
        entity_name: str | None = None,
        workspace_scoped: bool = False,
        search_columns: Sequence[str] = (),
        sortable_columns: frozenset[str] | None = None,
        filterable_columns: Mapping[str, str] | None = None,
    ) -> None:
        self._session = session
        self._model = model
        self._entity_name = entity_name or model.__name__
        self._workspace_scoped = workspace_scoped
        self._search_columns = tuple(search_columns)
        self._sortable_columns = sortable_columns or frozenset()
        self._filterable_columns = dict(filterable_columns or {})

    async def get_by_id(
        self,
        entity_id: UUID,
        *,
        workspace_id: UUID | None = None,
        include_deleted: bool = False,
    ) -> ModelT | None:
        """Return one entity by primary key."""

        self._validate_workspace_scope(workspace_id)
        statement = select(self._model).where(self._model.id == entity_id)  # type: ignore[attr-defined]
        if workspace_id is not None:
            statement = statement.where(self._model.workspace_id == workspace_id)  # type: ignore[attr-defined]
        if not include_deleted and has_attribute(self._model, "deleted_at"):
            statement = statement.where(self._model.deleted_at.is_(None))  # type: ignore[attr-defined]
        result = await self._session.scalars(statement)
        return result.first()

    async def get_all(
        self,
        *,
        workspace_id: UUID | None = None,
        include_deleted: bool = False,
        filters: RepositoryFilter | None = None,
        sort: Sequence[SortColumn] | None = None,
    ) -> Sequence[ModelT]:
        """Return all entities matching optional criteria."""

        statement = self._build_select(
            workspace_id=workspace_id,
            include_deleted=include_deleted,
            filters=filters,
            sort=tuple(sort or ()),
        )
        result = await self._session.scalars(statement)
        return result.all()

    async def find(
        self,
        specification: Specification[ModelT],
        *,
        workspace_id: UUID | None = None,
        include_deleted: bool = False,
        filters: RepositoryFilter | None = None,
        sort: Sequence[SortColumn] | None = None,
    ) -> Sequence[ModelT]:
        """Return entities matching a composable specification."""

        statement = self._build_select(
            workspace_id=workspace_id,
            include_deleted=include_deleted,
            specification=specification,
            filters=filters,
            sort=tuple(sort or ()),
        )
        result = await self._session.scalars(statement)
        return result.all()

    async def exists(
        self,
        entity_id: UUID,
        *,
        workspace_id: UUID | None = None,
        include_deleted: bool = False,
    ) -> bool:
        """Return whether an entity exists."""

        entity = await self.get_by_id(
            entity_id,
            workspace_id=workspace_id,
            include_deleted=include_deleted,
        )
        return entity is not None

    async def count(
        self,
        specification: Specification[ModelT] | None = None,
        *,
        workspace_id: UUID | None = None,
        include_deleted: bool = False,
        filters: RepositoryFilter | None = None,
    ) -> int:
        """Return the number of matching entities."""

        statement = self._build_select(
            workspace_id=workspace_id,
            include_deleted=include_deleted,
            specification=specification,
            filters=filters,
        )
        return await execute_count(self._session, statement)

    async def create(self, entity: ModelT) -> ModelT:
        """Persist a new entity."""

        self._session.add(entity)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise translate_integrity_error(exc, entity_name=self._entity_name) from exc
        await self._session.refresh(entity)
        return entity

    async def update(
        self,
        entity: ModelT,
        *,
        expected_version: int,
    ) -> ModelT:
        """Update an entity with optimistic concurrency."""

        if not has_attribute(self._model, "version"):
            raise ConcurrencyConflict(f"{self._entity_name} does not support optimistic locking.")

        current_version = cast(int, entity.version)  # type: ignore[attr-defined]
        if current_version != expected_version:
            raise ConcurrencyConflict(
                f"{self._entity_name} version mismatch: expected {expected_version}, "
                f"actual {current_version}."
            )

        if has_attribute(self._model, "updated_at"):
            entity.updated_at = utc_now()  # type: ignore[attr-defined]

        self._session.add(entity)
        try:
            await self._session.flush()
        except StaleDataError as exc:
            raise ConcurrencyConflict(f"{self._entity_name} changed after it was loaded.") from exc
        except IntegrityError as exc:
            raise translate_integrity_error(exc, entity_name=self._entity_name) from exc
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity_id: UUID, *, workspace_id: UUID | None = None) -> None:
        """Hard-delete an entity."""

        self._validate_workspace_scope(workspace_id)
        where_clauses = [self._model.id == entity_id]  # type: ignore[attr-defined]
        if workspace_id is not None:
            where_clauses.append(self._model.workspace_id == workspace_id)  # type: ignore[attr-defined]
        statement = delete(self._model).where(*where_clauses)
        result = await self._session.execute(statement)
        if cast(CursorResult[Any], result).rowcount == 0:
            raise EntityNotFound(f"{self._entity_name} {entity_id} was not found.")

    async def soft_delete(
        self,
        entity_id: UUID,
        *,
        expected_version: int,
        updated_by: UUID | None = None,
        workspace_id: UUID | None = None,
    ) -> None:
        """Soft-delete an entity."""

        self._validate_workspace_scope(workspace_id)
        if not has_attribute(self._model, "deleted_at"):
            raise EntityNotFound(f"{self._entity_name} does not support soft delete.")

        affected = await soft_delete_by_id(
            self._session,
            self._model,
            entity_id,
            expected_version=expected_version,
            updated_by=updated_by,
            workspace_id=workspace_id,
        )
        if affected == 0:
            raise self._not_found_or_conflict(entity_id)

    async def restore(
        self,
        entity_id: UUID,
        *,
        expected_version: int,
        updated_by: UUID | None = None,
        workspace_id: UUID | None = None,
    ) -> ModelT:
        """Restore a soft-deleted entity."""

        self._validate_workspace_scope(workspace_id)
        if not has_attribute(self._model, "deleted_at"):
            raise EntityNotFound(f"{self._entity_name} does not support restore.")

        affected = await restore_by_id(
            self._session,
            self._model,
            entity_id,
            expected_version=expected_version,
            updated_by=updated_by,
            workspace_id=workspace_id,
        )
        if affected == 0:
            raise self._not_found_or_conflict(entity_id)

        restored = await self.get_by_id(entity_id, workspace_id=workspace_id, include_deleted=False)
        if restored is None:
            raise EntityNotFound(f"{self._entity_name} {entity_id} was not restored.")
        return restored

    async def bulk_create(self, entities: Sequence[ModelT]) -> Sequence[ModelT]:
        """Persist multiple new entities."""

        self._session.add_all(list(entities))
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise translate_integrity_error(exc, entity_name=self._entity_name) from exc
        for entity in entities:
            await self._session.refresh(entity)
        return list(entities)

    async def bulk_update(
        self,
        entities: Sequence[ModelT],
        *,
        expected_versions: Mapping[UUID, int],
    ) -> Sequence[ModelT]:
        """Update multiple entities with per-entity version checks."""

        updated: list[ModelT] = []
        for entity in entities:
            entity_id = cast(UUID, entity.id)  # type: ignore[attr-defined]
            expected_version = expected_versions[entity_id]
            updated.append(await self.update(entity, expected_version=expected_version))
        return updated

    async def bulk_delete(
        self,
        entity_ids: Sequence[UUID],
        *,
        workspace_id: UUID | None = None,
    ) -> int:
        """Hard-delete multiple entities."""

        self._validate_workspace_scope(workspace_id)
        if not entity_ids:
            return 0

        where_clauses = [self._model.id.in_(entity_ids)]  # type: ignore[attr-defined]
        if workspace_id is not None:
            where_clauses.append(self._model.workspace_id == workspace_id)  # type: ignore[attr-defined]
        statement = delete(self._model).where(*where_clauses)
        result = await self._session.execute(statement)
        return int(cast(CursorResult[Any], result).rowcount or 0)

    async def find_paginated(
        self,
        *,
        page: int,
        page_size: int,
        specification: Specification[ModelT] | None = None,
        workspace_id: UUID | None = None,
        include_deleted: bool = False,
        filters: RepositoryFilter | None = None,
        sort: Sequence[SortColumn] | None = None,
    ) -> Page[ModelT]:
        """Return a page of entities with metadata."""

        base_statement = self._build_select(
            workspace_id=workspace_id,
            include_deleted=include_deleted,
            specification=specification,
            filters=filters,
            sort=tuple(sort or ()),
        )
        total_items = await execute_count(self._session, base_statement)
        metadata = build_page_metadata(page, page_size, total_items)
        statement = base_statement.offset(page_to_offset(page, page_size)).limit(page_size)
        result = await self._session.scalars(statement)
        return Page(items=result.all(), metadata=metadata)

    async def find_offset(
        self,
        *,
        offset: int,
        limit: int,
        specification: Specification[ModelT] | None = None,
        workspace_id: UUID | None = None,
        include_deleted: bool = False,
        filters: RepositoryFilter | None = None,
        sort: Sequence[SortColumn] | None = None,
    ) -> Sequence[ModelT]:
        """Return entities using offset/limit pagination."""

        if offset < 0:
            raise ValueError("offset must be >= 0")
        if limit < 1:
            raise ValueError("limit must be >= 1")

        statement = (
            self._build_select(
                workspace_id=workspace_id,
                include_deleted=include_deleted,
                specification=specification,
                filters=filters,
                sort=tuple(sort or ()),
            )
            .offset(offset)
            .limit(limit)
        )
        result = await self._session.scalars(statement)
        return result.all()

    def _build_select(
        self,
        *,
        workspace_id: UUID | None = None,
        include_deleted: bool = False,
        specification: Specification[ModelT] | None = None,
        filters: RepositoryFilter | None = None,
        sort: tuple[SortColumn, ...] = (),
    ) -> Any:
        self._validate_workspace_scope(workspace_id)
        return build_select(
            self._model,
            include_deleted=include_deleted,
            specification=specification,
            filters=filters,
            sort=sort,
            allowed_sort_columns=self._sortable_columns,
            search_columns=self._search_columns,
            filterable_columns=self._filterable_columns,
            workspace_id=workspace_id,
        )

    def _validate_workspace_scope(self, workspace_id: UUID | None) -> None:
        if self._workspace_scoped and workspace_id is None:
            raise ValueError(f"{self._entity_name} requires an explicit workspace_id.")

    def _not_found_or_conflict(self, entity_id: UUID) -> ConcurrencyConflict | EntityNotFound:
        if has_attribute(self._model, "version"):
            return ConcurrencyConflict(
                f"{self._entity_name} {entity_id} was not found or changed concurrently."
            )
        return EntityNotFound(f"{self._entity_name} {entity_id} was not found.")
