"""Pagination helpers for repository queries."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PageMetadata:
    """Metadata describing a paginated result set."""

    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


@dataclass(frozen=True, slots=True)
class Page[ItemT]:
    """Page of repository results with metadata."""

    items: Sequence[ItemT]
    metadata: PageMetadata


def build_page_metadata(page: int, page_size: int, total_items: int) -> PageMetadata:
    """Build pagination metadata from page parameters and total count."""

    if page < 1:
        raise ValueError("page must be >= 1")
    if page_size < 1:
        raise ValueError("page_size must be >= 1")

    total_pages = math.ceil(total_items / page_size) if total_items else 0
    return PageMetadata(
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_previous=page > 1 and total_pages > 0,
    )


def page_to_offset(page: int, page_size: int) -> int:
    """Convert page-based pagination to a zero-based offset."""

    return (page - 1) * page_size
