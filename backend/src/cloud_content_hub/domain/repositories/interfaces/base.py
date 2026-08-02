"""Generic repository port for persistence adapters."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol, TypeVar
from uuid import UUID

EntityT = TypeVar("EntityT")
IdT = TypeVar("IdT", bound=UUID)
SpecificationT = TypeVar("SpecificationT")
FilterT = TypeVar("FilterT")
SortT = TypeVar("SortT")
PageT = TypeVar("PageT")


class IRepository(Protocol[EntityT, IdT]):
    """Persistence port for aggregate and read-model access.

    Implementations must not commit transactions. The unit of work owns
    commit and rollback boundaries.
    """

    async def get_by_id(
        self,
        entity_id: IdT,
        *,
        include_deleted: bool = False,
    ) -> EntityT | None:
        """Return one entity by primary key or ``None`` when absent."""

    async def get_all(
        self,
        *,
        include_deleted: bool = False,
        filters: FilterT | None = None,
        sort: Sequence[SortT] | None = None,
    ) -> Sequence[EntityT]:
        """Return all entities matching optional filter and sort criteria."""

    async def find(
        self,
        specification: SpecificationT,
        *,
        include_deleted: bool = False,
        filters: FilterT | None = None,
        sort: Sequence[SortT] | None = None,
    ) -> Sequence[EntityT]:
        """Return entities matching a composable specification."""

    async def exists(
        self,
        entity_id: IdT,
        *,
        include_deleted: bool = False,
    ) -> bool:
        """Return whether an entity exists for the given identifier."""

    async def count(
        self,
        specification: SpecificationT | None = None,
        *,
        include_deleted: bool = False,
        filters: FilterT | None = None,
    ) -> int:
        """Return the number of entities matching optional criteria."""

    async def create(self, entity: EntityT) -> EntityT:
        """Persist a new entity and return the stored instance."""

    async def update(
        self,
        entity: EntityT,
        *,
        expected_version: int,
    ) -> EntityT:
        """Update an entity using optimistic concurrency."""

    async def delete(self, entity_id: IdT) -> None:
        """Hard-delete an entity when supported by the aggregate."""

    async def soft_delete(
        self,
        entity_id: IdT,
        *,
        expected_version: int,
        updated_by: UUID | None = None,
    ) -> None:
        """Soft-delete an entity by setting ``deleted_at``."""

    async def restore(
        self,
        entity_id: IdT,
        *,
        expected_version: int,
        updated_by: UUID | None = None,
    ) -> EntityT:
        """Restore a soft-deleted entity during its grace period."""

    async def bulk_create(self, entities: Sequence[EntityT]) -> Sequence[EntityT]:
        """Persist multiple new entities in one batch."""

    async def bulk_update(
        self,
        entities: Sequence[EntityT],
        *,
        expected_versions: Mapping[IdT, int],
    ) -> Sequence[EntityT]:
        """Update multiple entities with per-entity version checks."""

    async def bulk_delete(self, entity_ids: Sequence[IdT]) -> int:
        """Hard-delete multiple entities and return the affected row count."""

    async def find_paginated(
        self,
        *,
        page: int,
        page_size: int,
        specification: SpecificationT | None = None,
        include_deleted: bool = False,
        filters: FilterT | None = None,
        sort: Sequence[SortT] | None = None,
    ) -> PageT:
        """Return a page of entities with pagination metadata."""

    async def find_offset(
        self,
        *,
        offset: int,
        limit: int,
        specification: SpecificationT | None = None,
        include_deleted: bool = False,
        filters: FilterT | None = None,
        sort: Sequence[SortT] | None = None,
    ) -> Sequence[EntityT]:
        """Return entities using offset/limit pagination."""
