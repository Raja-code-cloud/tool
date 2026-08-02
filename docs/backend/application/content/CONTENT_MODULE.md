# Content Module

The content application module orchestrates AI-assisted content generation, immutable version
management, and content lifecycle operations for workspace-scoped aggregates.

## Scope

Implemented under `backend/src/cloud_content_hub/application/content/`:

| Layer         | Responsibility                                                  |
| ------------- | --------------------------------------------------------------- |
| `commands/`   | Mutation intents (`GenerateContent`, `ArchiveContent`, …)       |
| `queries/`    | Read intents (`GetContent`, `PreviewContent`, …)                |
| `handlers/`   | One handler per use case                                        |
| `dto/`        | Request/response projections (never ORM models)                 |
| `validators/` | Business validation and workspace rules                         |
| `mappers/`    | Read model → DTO translation                                    |
| `services/`   | AI orchestration, prompt building, platform mapping, versioning |
| `interfaces/` | Repository and event publisher ports                            |
| `events/`     | Domain events persisted through the transactional outbox        |
| `exceptions/` | Module-specific application errors                              |

## Commands

| Command                | Handler                       | Permission         |
| ---------------------- | ----------------------------- | ------------------ |
| `GenerateContent`      | `GenerateContentHandler`      | `content:generate` |
| `RegenerateContent`    | `RegenerateContentHandler`    | `content:generate` |
| `DuplicateContent`     | `DuplicateContentHandler`     | `content:write`    |
| `ArchiveContent`       | `ArchiveContentHandler`       | `content:write`    |
| `DeleteContent`        | `DeleteContentHandler`        | `content:delete`   |
| `RestoreContent`       | `RestoreContentHandler`       | `content:write`    |
| `CreateContentVersion` | `CreateContentVersionHandler` | `content:write`    |
| `ApproveContent`       | `ApproveContentHandler`       | `content:write`    |
| `RejectContent`        | `RejectContentHandler`        | `content:write`    |

## Queries

| Query               | Handler                    | Permission         |
| ------------------- | -------------------------- | ------------------ |
| `GetContent`        | `GetContentHandler`        | `content:read`     |
| `GetContentVersion` | `GetContentVersionHandler` | `content:read`     |
| `SearchContent`     | `SearchContentHandler`     | `content:read`     |
| `ListContent`       | `ListContentHandler`       | `content:read`     |
| `CompareVersions`   | `CompareVersionsHandler`   | `content:read`     |
| `PreviewContent`    | `PreviewContentHandler`    | `content:generate` |

## Business rules

- Every accepted generation creates a new generation request; acceptance of output creates a new
  immutable version.
- Generated versions are immutable and never overwritten.
- Regeneration always creates a new candidate; it never replaces prior outputs.
- Version history is preserved indefinitely.
- Deletes are soft-only (`deleted_at`); restore is supported.
- All reads and writes are workspace-scoped through `ActorContext.workspace_id`.

## Dependencies

Handlers depend on:

- `IContentRepository`, `IGenerationRequestRepository`, `IGenerationOutputRepository`
- `IBackgroundJobRepository` for async AI work
- `IContentEventPublisher` for outbox events
- `AIGenerationPort` (via `ContentGenerationService`) for preview and worker orchestration
- `IUnitOfWork` for transactional boundaries

Handlers never import provider SDKs or SQLAlchemy.

## DTOs

Primary transport-facing DTOs:

- `GenerateContentRequest` / `GenerateContentResponse`
- `ContentVersionResponse`
- `ContentPreviewResponse`
- `SearchContentResponse` (paged via `PagedResultDto[ContentDto]`)

See `dto/requests.py` and `dto/responses.py`.

## Events

| Event                | Raised by                  |
| -------------------- | -------------------------- |
| `ContentGenerated`   | `GenerateContentHandler`   |
| `ContentRegenerated` | `RegenerateContentHandler` |
| `ContentArchived`    | `ArchiveContentHandler`    |
| `ContentDeleted`     | `DeleteContentHandler`     |
| `ContentApproved`    | `ApproveContentHandler`    |
| `ContentRejected`    | `RejectContentHandler`     |

Events are published in the same unit-of-work transaction as the originating mutation.
