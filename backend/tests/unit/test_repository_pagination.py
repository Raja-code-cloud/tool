"""Unit tests for repository pagination helpers."""

import pytest

from cloud_content_hub.infrastructure.repositories.sqlalchemy.pagination import (
    build_page_metadata,
    page_to_offset,
)


def test_page_to_offset_converts_page_numbers() -> None:
    assert page_to_offset(1, 25) == 0
    assert page_to_offset(3, 10) == 20


def test_build_page_metadata_for_empty_result_set() -> None:
    metadata = build_page_metadata(page=1, page_size=25, total_items=0)
    assert metadata.total_items == 0
    assert metadata.total_pages == 0
    assert metadata.has_next is False
    assert metadata.has_previous is False


def test_build_page_metadata_for_multiple_pages() -> None:
    metadata = build_page_metadata(page=2, page_size=10, total_items=25)
    assert metadata.total_pages == 3
    assert metadata.has_next is True
    assert metadata.has_previous is True


@pytest.mark.parametrize("page", [0, -1])
def test_build_page_metadata_rejects_invalid_page(page: int) -> None:
    with pytest.raises(ValueError, match="page"):
        build_page_metadata(page=page, page_size=10, total_items=1)
