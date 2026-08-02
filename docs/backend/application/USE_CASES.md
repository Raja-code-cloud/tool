# Use Cases

Application use cases are implemented as command handlers (mutations) and query handlers (reads). Each handler represents exactly one use case.

## Assets

| Use case           | Handler               | Permission      |
| ------------------ | --------------------- | --------------- |
| Upload asset       | `UploadAssetHandler`  | `assets:write`  |
| Replace asset file | `ReplaceAssetHandler` | `assets:write`  |
| Delete asset       | `DeleteAssetHandler`  | `assets:delete` |
| Get asset          | `GetAssetHandler`     | `assets:read`   |
| Search assets      | `SearchAssetsHandler` | `assets:read`   |
| List assets        | `ListAssetsHandler`   | `assets:read`   |

**Upload flow:** validate media rules → create asset record → attach pending media metadata → enqueue media background job → return `OperationDto`.

**Replace flow:** load asset → verify version → validate replacement rules → update media metadata → enqueue replace job → return `OperationDto`.

## Content

| Use case           | Handler                    | Permission         |
| ------------------ | -------------------------- | ------------------ |
| Generate content   | `GenerateContentHandler`   | `content:generate` |
| Regenerate content | `RegenerateContentHandler` | `content:generate` |
| Get content        | `GetContentHandler`        | `content:read`     |
| Search content     | `SearchContentHandler`     | `content:read`     |
| List content       | `ListContentHandler`       | `content:read`     |

**Generation flow:** validate source version → verify model enabled → persist generation request → enqueue AI job → return `OperationDto`.

## Publishing

| Use case             | Handler                      | Permission          |
| -------------------- | ---------------------------- | ------------------- |
| Create publication   | `CreatePublicationHandler`   | `publishing:write`  |
| Dispatch publication | `DispatchPublicationHandler` | `publishing:write`  |
| Cancel publication   | `CancelPublicationHandler`   | `publishing:delete` |

**Create flow:** validate approved immutable version → verify social accounts healthy → create publication with targets → return `PublicationDto`.

**Dispatch flow:** verify publication state → transition to in-progress → enqueue publishing job → return `OperationDto`.

## Scheduler

| Use case             | Handler                 | Permission        |
| -------------------- | ----------------------- | ----------------- |
| Schedule publication | `CreateScheduleHandler` | `schedule:write`  |
| Cancel schedule      | `CancelScheduleHandler` | `schedule:delete` |
| Get schedule         | `GetScheduleHandler`    | `schedule:read`   |

**Schedule flow:** resolve local wall time via `IScheduleTimeResolver` → validate target and future instant → persist schedule → return `ScheduleDto`.

## Analytics

| Use case         | Handler                  | Permission       |
| ---------------- | ------------------------ | ---------------- |
| Get dashboard    | `GetDashboardHandler`    | `analytics:read` |
| Import analytics | `ImportAnalyticsHandler` | `analytics:read` |

## Notifications

| Use case               | Handler                       | Permission            |
| ---------------------- | ----------------------------- | --------------------- |
| List notifications     | `GetNotificationsHandler`     | `notifications:read`  |
| Mark notification read | `MarkNotificationReadHandler` | `notifications:write` |

Notifications are recipient-scoped; handlers always filter by `actor.user_id`.

## Cross-cutting orchestration

All mutating use cases:

1. Authenticate actor context (delivery layer)
2. Authorize permission
3. Validate business rules
4. Open unit of work
5. Execute repository operations
6. Flush (commit on exit)
7. Map to response DTO

Asynchronous operations (upload, generation, dispatch) return an `OperationDto` referencing a background job. Workers complete the external I/O and update job state separately.
