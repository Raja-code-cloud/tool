# Asset Versioning

## Overview

Assets use optimistic concurrency at the aggregate level. Media replacement creates a new version while preserving asset identity and history.

## Aggregate version

Every `ContentAsset` row carries a `version` integer managed by the repository layer:

- Starts at `1` on create
- Increments on every successful mutation (replace, delete, restore, archive, tag, move)
- Clients must supply the current version via `If-Match` for mutating operations
- Stale versions raise `VersionConflictError` (`409 version_conflict`)

## Media versioning

Replace does not mutate existing blob metadata in place. Instead:

1. Handler validates the asset is `active` and version matches.
2. New media metadata is attached with `scan_status=pending`.
3. Aggregate `version` increments.
4. A media queue job uploads the replacement blob.
5. `AssetReplaced` event is published in the same transaction.

Previous storage objects remain linked for audit and retention policy. The repository implementation manages `storage_objects` and `asset_storage_objects` junction rows.

## Content versions

Immutable `content_versions` snapshots are separate from media versioning. They capture editorial content history for publishing and audit. Asset details expose `version_count` via `GetAssetDetailsQuery`.

Media replace and content version creation are independent workflows:

| Operation           | Affects                | Version field                         |
| ------------------- | ---------------------- | ------------------------------------- |
| Replace source file | Media blob + aggregate | `content_assets.version`              |
| Edit content body   | Content snapshot       | New `content_versions.version_number` |
| Soft delete         | Aggregate lifecycle    | `content_assets.version`              |

## Soft delete and restore

### Delete

- Sets `deleted_at` on the aggregate (soft delete)
- Increments `version`
- Raises `AssetDeleted` event
- Active reads exclude deleted rows (`deleted_at IS NULL`)

### Restore

- Clears `deleted_at` via `IAssetRepository.restore`
- Requires `get_deleted_by_id` (administrative read path)
- Validates asset is currently deleted
- Raises `AssetRestored` event

Deleted assets retain storage objects per retention policy. Blob purge is a separate two-phase maintenance operation.

## Archive lifecycle

Archive transitions `lifecycle_status` to `archived`:

- Archived assets cannot be replaced, deleted, tagged, moved, or copied
- Archive increments aggregate version
- Archive does not delete media or content versions

## Copy semantics

`CopyAssetCommand` creates a new aggregate referencing the source asset's media. The repository implementation decides whether to share storage object references or create new junction rows. The copy receives a new ID, title, and `version=1`.

## Metadata immutability

Extracted upload metadata (checksum, dimensions, extension) is captured once at upload/replace time and stored on the media record. Subsequent reads return the stored snapshot; metadata is never recomputed or patched.

## Concurrency worked example

```
1. Client loads asset → version=2
2. Client sends DELETE with If-Match: "2" → 204, version becomes 3 internally
3. Client sends REPLACE with If-Match: "2" → 409 version_conflict
4. Client reloads → 404 (soft-deleted)
```

## Related

- [Upload flow](UPLOAD.md)
- [Asset module overview](ASSET_MODULE.md)
- [Transactions](../../repositories/TRANSACTIONS.md)
