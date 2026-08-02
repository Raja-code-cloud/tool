# Notification Module

## Overview

The Notification module lives in `backend/src/cloud_content_hub/application/notifications/` and implements workspace-scoped, recipient-scoped notification use cases. Handlers orchestrate validation, repository ports, delivery orchestration, retention resolution, and transactional domain events without exposing ORM models or implementing channel providers directly.

## Supported notification types

| Type code        | Category      | Description                              |
| ---------------- | ------------- | ---------------------------------------- |
| `system`         | transactional | Platform and workspace system events     |
| `publishing`     | product       | Publication lifecycle updates            |
| `generation`     | product       | AI content generation completion         |
| `scheduler`      | product       | Schedule dispatch and conflict alerts    |
| `analytics`      | product       | Analytics import and dashboard freshness |
| `security`       | security      | Authentication and permission events     |
| `administration` | transactional | Admin queue and provider status          |

## Supported channels

| Channel   | Status | Description                         |
| --------- | ------ | ----------------------------------- |
| `in_app`  | Active | User inbox notifications            |
| `email`   | Future | Email delivery orchestration only   |
| `webhook` | Future | Webhook delivery orchestration only |
| `sms`     | Future | Out of scope                        |
| `push`    | Future | Out of scope                        |

Only `in_app` channel resolution is implemented in `NotificationDeliveryService`. Email, webhook, SMS, and push providers are out of scope.

## Module layout

```
application/notifications/
├── commands/          # Mutation command dataclasses
├── queries/           # Read query dataclasses
├── dto/               # Request and response DTOs (Pydantic)
├── handlers/          # One handler per command/query
├── validators/        # Business validation rules
├── mappers/           # Read model → response DTO mapping
├── exceptions/        # Feature-specific application errors
├── interfaces/        # Repository and event publisher ports
├── services/          # Delivery and retention orchestration
└── events/            # Domain events raised by command handlers
```

## Commands

| Command                       | Handler                       | Permission             | Description                                        |
| ----------------------------- | ----------------------------- | ---------------------- | -------------------------------------------------- |
| `CreateNotificationCommand`   | `CreateNotificationHandler`   | `notifications:write`  | Create a notification for a workspace recipient    |
| `MarkNotificationReadCommand` | `MarkNotificationReadHandler` | `notifications:write`  | Set read state with optimistic concurrency         |
| `MarkAllReadCommand`          | `MarkAllReadHandler`          | `notifications:write`  | Mark all unread notifications as read              |
| `ArchiveNotificationCommand`  | `ArchiveNotificationHandler`  | `notifications:write`  | Archive a notification while keeping it searchable |
| `DeleteNotificationCommand`   | `DeleteNotificationHandler`   | `notifications:delete` | Soft-delete a notification                         |
| `UpdatePreferencesCommand`    | `UpdatePreferencesHandler`    | `notifications:write`  | Upsert notification channel preferences            |

## Queries

| Query                         | Handler                         | Permission           | Description                          |
| ----------------------------- | ------------------------------- | -------------------- | ------------------------------------ |
| `GetNotificationsQuery`       | `GetNotificationsHandler`       | `notifications:read` | Cursor-paged inbox list with filters |
| `GetUnreadNotificationsQuery` | `GetUnreadNotificationsHandler` | `notifications:read` | Unread-only inbox list               |
| `SearchNotificationsQuery`    | `SearchNotificationsHandler`    | `notifications:read` | Full-text search with filters        |
| `GetPreferencesQuery`         | `GetPreferencesHandler`         | `notifications:read` | List user notification preferences   |
| `NotificationSummaryQuery`    | `NotificationSummaryHandler`    | `notifications:read` | Aggregated inbox statistics          |

## Business rules

- Notifications belong to exactly one workspace and one recipient user.
- Handlers always scope reads and mutations to `actor.user_id` unless creating for another recipient.
- Delete is soft delete only; deleted items are non-disclosable.
- Archived notifications remain searchable when `includeArchived=true`.
- Read timestamp is immutable once set; clearing read state is rejected.
- Optimistic concurrency is enforced via `expected_version` on mutations.
- Recipient must be an active workspace member at creation time.
- Notification type codes must exist in the catalog or known type map.
- Severity must meet the minimum floor for the requested delivery priority.

## Ports and dependencies

| Port                                | Purpose                                    |
| ----------------------------------- | ------------------------------------------ |
| `INotificationRepository`           | Notification persistence and inbox queries |
| `INotificationPreferenceRepository` | User channel preference persistence        |
| `INotificationEventPublisher`       | Transactional outbox domain events         |
| `IUnitOfWork`                       | Transaction boundary                       |

Infrastructure adapters implement these ports. Handlers receive factory callables at composition time.

## DTOs

| Request                          | Response                              |
| -------------------------------- | ------------------------------------- |
| `NotificationRequestDto`         | `NotificationResponseDto`             |
| `MarkNotificationReadRequestDto` | `NotificationResponseDto`             |
| `UpdatePreferencesRequestDto`    | `NotificationPreferenceResponseDto[]` |
| —                                | `NotificationSummaryResponseDto`      |
| —                                | `UnreadCountResponseDto`              |

`NotificationDto` is a backward-compatible alias for `NotificationResponseDto`.

## Error mapping

| Exception                          | Code                       | When                                 |
| ---------------------------------- | -------------------------- | ------------------------------------ |
| `NotificationNotFoundError`        | `resource_not_found`       | Notification not found for recipient |
| `NotificationTypeNotFoundError`    | `validation_failed`        | Unknown type code                    |
| `InvalidRecipientError`            | `validation_failed`        | Recipient not in workspace           |
| `ReadTimestampImmutableError`      | `invalid_state_transition` | Attempt to clear read timestamp      |
| `NotificationAlreadyArchivedError` | `invalid_state_transition` | Duplicate archive request            |
| `VersionConflictError`             | `version_conflict`         | Stale expected version               |

See [EVENTS.md](./EVENTS.md), [PREFERENCES.md](./PREFERENCES.md), and [RETENTION.md](./RETENTION.md) for related documentation.
