# Pagination

## Purpose

Repository pagination helpers provide page-based and offset-based retrieval with consistent metadata for application DTO mapping.

## Page-based pagination

`find_paginated()` accepts:

- `page`: 1-based page number
- `page_size`: number of items per page

It returns `Page[ModelT]` containing:

- `items`: current page results
- `metadata`: `PageMetadata`

`PageMetadata` includes:

- `page`
- `page_size`
- `total_items`
- `total_pages`
- `has_next`
- `has_previous`

## Offset-based pagination

`find_offset()` accepts:

- `offset`: zero-based row offset
- `limit`: maximum number of rows

Use offset pagination only for internal/admin flows. Public APIs should prefer cursor pagination defined in the HTTP layer.

## Sorting integration

Pagination methods accept optional `sort: Sequence[SortColumn]`. Sort columns must be declared through the repository constructor via `sortable_columns`.

## Example

```python
page = await repository.find_paginated(
    page=2,
    page_size=25,
    workspace_id=workspace_id,
    sort=[SortColumn(name="updated_at", direction=SortDirection.DESC)],
)
```

Application services map `PageMetadata` to API response envelopes without exposing ORM models.

## Validation

`build_page_metadata()` rejects invalid page or page size values. Offset pagination rejects negative offsets and non-positive limits.
