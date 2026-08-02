# Asset Management Module

## Overview

The Asset Management module lives in `backend/src/cloud_content_hub/application/assets/` and implements workspace-scoped content asset use cases. It follows Clean Architecture boundaries: handlers orchestrate validation, repository ports, storage services, and transactional events without exposing ORM models or accessing cloud SDKs directly.

## Supported asset types

| Type              | Container           | Description                            |
| ----------------- | ------------------- | -------------------------------------- |
| `poster`          | `posters`           | Marketing and social poster images     |
| `article`         | `articles`          | Article body assets and attachments    |
| `video`           | `videos`            | Video source files                     |
| `thumbnail`       | `thumbnails`        | Derived preview images                 |
| `generated_image` | `generated-content` | Reserved for future AI-generated media |

## Module layout

```
application/assets/
├── commands/          # Mutation command dataclasses
├── queries/           # Read query dataclasses
├── dto/               # Request and response DTOs (Pydantic)
├── handlers/          # One handler per command/query
├── validators/        # Business validation rules
├── mappers/           # Read model → response DTO mapping
├── exceptions/        # Feature-specific application errors
├── interfaces/        # Repository and port protocols
├── services/          # Orchestration helpers (storage, metadata, duplicates)
└── events/            # Domain events raised by command handlers
```

## Commands

| Command               | Handler               | Permission      | Description                            |
| --------------------- | --------------------- | --------------- | -------------------------------------- |
| `UploadAssetCommand`  | `UploadAssetHandler`  | `assets:write`  | Create asset and queue media ingestion |
| `ReplaceAssetCommand` | `ReplaceAssetHandler` | `assets:write`  | Replace source file, increment version |
| `DeleteAssetCommand`  | `DeleteAssetHandler`  | `assets:delete` | Soft-delete asset                      |
| `RestoreAssetCommand` | `RestoreAssetHandler` | `assets:write`  | Restore soft-deleted asset             |
| `ArchiveAssetCommand` | `ArchiveAssetHandler` | `assets:write`  | Transition asset to archived lifecycle |
| `TagAssetCommand`     | `TagAssetHandler`     | `assets:write`  | Replace asset tag set                  |
| `MoveAssetCommand`    | `MoveAssetHandler`    | `assets:write`  | Move asset to project/folder           |
| `CopyAssetCommand`    | `CopyAssetHandler`    | `assets:write`  | Copy asset within workspace            |

## Queries

| Query                  | Handler                  | Permission    | Description                      |
| ---------------------- | ------------------------ | ------------- | -------------------------------- |
| `GetAssetQuery`        | `GetAssetHandler`        | `assets:read` | Retrieve one active asset        |
| `GetAssetDetailsQuery` | `GetAssetDetailsHandler` | `assets:read` | Extended asset with statistics   |
| `ListAssetsQuery`      | `ListAssetsHandler`      | `assets:read` | Cursor-paged list with filters   |
| `SearchAssetsQuery`    | `SearchAssetsHandler`    | `assets:read` | Full-text search with filters    |
| `AssetUsageQuery`      | `AssetUsageHandler`      | `assets:read` | Dependency and reference summary |

## Business rules

- One asset belongs to exactly one workspace.
- Assets support optimistic concurrency via `version`.
- Delete is soft delete (`deleted_at` set by repository).
- Replace creates a new media version and increments aggregate version.
- Extracted metadata is immutable after upload.
- Duplicate detection rejects uploads with identical checksum within a workspace.
- Archived assets cannot be deleted, tagged, moved, or copied.
- Only active assets can be replaced.

## Ports and dependencies

| Port                       | Purpose                               |
| -------------------------- | ------------------------------------- |
| `IAssetRepository`         | Aggregate persistence and read models |
| `IUnitOfWork`              | Transaction boundary                  |
| `IBackgroundJobRepository` | Async media queue jobs                |
| `IObjectStoragePort`       | Short-lived download URLs             |
| `IAssetEventPublisher`     | Transactional outbox events           |
| `IVirusScanHook`           | Pre-acceptance scan validation hook   |

Infrastructure adapters implement these ports. Handlers receive factory callables at composition time.

## Domain events

Events are persisted through `IAssetEventPublisher` in the same transaction as the originating change:

| Event           | Trigger                                 |
| --------------- | --------------------------------------- |
| `AssetUploaded` | New asset created and upload job queued |
| `AssetReplaced` | Source file replacement queued          |
| `AssetDeleted`  | Asset soft-deleted                      |
| `AssetRestored` | Soft-deleted asset restored             |

Event payloads contain stable identifiers and redacted snapshots only.

## Error mapping

| Exception                    | Code                       | When                            |
| ---------------------------- | -------------------------- | ------------------------------- |
| `AssetNotFoundError`         | `resource_not_found`       | Asset not found in workspace    |
| `AssetMediaTypeError`        | `unsupported_media_type`   | MIME not allowed for asset type |
| `AssetExtensionError`        | `unsupported_extension`    | File extension not allowed      |
| `AssetChecksumMismatchError` | `checksum_mismatch`        | Supplied checksum mismatch      |
| `AssetDuplicateError`        | `duplicate_asset`          | Duplicate content in workspace  |
| `AssetStateError`            | `state_transition_invalid` | Invalid lifecycle transition    |
| `VersionConflictError`       | `version_conflict`         | Stale optimistic version        |

## Related documentation

- [Upload flow](UPLOAD.md)
- [Search](SEARCH.md)
- [Versioning](VERSIONING.md)
- [API contract](../../api/ASSET_API.md)
- [Storage architecture](../../storage/STORAGE_ARCHITECTURE.md)
- [Repository pattern](../../repositories/REPOSITORY_PATTERN.md)
