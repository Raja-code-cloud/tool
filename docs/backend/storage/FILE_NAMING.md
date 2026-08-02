# File Naming Strategy

## Layout

Blob names follow a deterministic, collision-resistant path:

```text
{tenant-id}/{user-id}/{yyyy}/{mm}/{dd}/{asset-type}/{uuid}/{filename}
```

Example:

```text
tenant-a/user-a/2025/02/03/videos/00000000000040008000000000000001/clip.mp4
```

## Components

| Segment      | Rules                                                                 |
| ------------ | --------------------------------------------------------------------- |
| `tenant-id`  | Lowercase alphanumeric with hyphens; 1–63 chars; validated identifier |
| `user-id`    | Same rules as tenant-id                                               |
| Date path    | UTC `YYYY/MM/DD` from `created_at`                                    |
| `asset-type` | `BlobType` enum value (matches container category)                    |
| `uuid`       | UUID hex without hyphens for uniqueness                               |
| `filename`   | Sanitized base name only; no path segments                            |

## Building names

Use `build_blob_name()` from `utils.py`:

```python
from uuid import uuid7
from datetime import datetime, timezone

blob_name = build_blob_name(
    tenant_id="tenant-a",
    user_id="user-a",
    blob_type=BlobType.ARTICLE,
    object_id=uuid7(),
    filename="report.pdf",
    created_at=datetime.now(timezone.utc),
)
```

## Collision avoidance

- UUID in the path ensures uniqueness even when filenames repeat.
- Date partitioning supports lifecycle policies and operational queries by time range.
- Tenant and user prefixes enforce workspace-scoped isolation at the key level.

## Filename sanitization

`validate_filename()` rejects:

- Path traversal (`../`, embedded slashes)
- Empty or overlong names (>255 chars)
- Characters outside `[A-Za-z0-9._-]`

## Blob name validation

`validate_blob_name()` additionally rejects:

- Empty names or names exceeding 1024 characters
- Leading slashes
- Unsafe segments (`.`, `..`, empty segments)

## Container selection

The blob path `asset-type` segment corresponds to `BlobType` but the **container** is set separately on `StorageLocation`. Application code should align container with content category. See [Container Strategy](CONTAINER_STRATEGY.md).

## Provider portability

This layout is provider-neutral. Alternative adapters (S3, GCS) use the same key structure within their bucket/container model.
