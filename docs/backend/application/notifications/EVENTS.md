# Notification Events

## Overview

Notification command handlers raise domain events that are persisted through `INotificationEventPublisher` in the same database transaction as the originating change. Events follow past-tense naming and contain stable identifiers only—no raw message bodies beyond what is already stored on the notification aggregate.

## Event types

| Event                  | Trigger                       | Key payload                                                                                                |
| ---------------------- | ----------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `NotificationCreated`  | `CreateNotificationHandler`   | `workspace_id`, `notification_id`, `recipient_user_id`, `type_code`, `severity`, `actor_id`, `occurred_at` |
| `NotificationRead`     | `MarkNotificationReadHandler` | `workspace_id`, `notification_id`, `recipient_user_id`, `read_at`, `actor_id`, `occurred_at`               |
| `NotificationArchived` | `ArchiveNotificationHandler`  | `workspace_id`, `notification_id`, `recipient_user_id`, `actor_id`, `version`, `occurred_at`               |
| `NotificationDeleted`  | `DeleteNotificationHandler`   | `workspace_id`, `notification_id`, `recipient_user_id`, `actor_id`, `version`, `occurred_at`               |
| `PreferencesUpdated`   | `UpdatePreferencesHandler`    | `workspace_id`, `user_id`, `type_codes`, `actor_id`, `occurred_at`                                         |

Union type: `NotificationDomainEvent`.

## Publisher port

```python
class INotificationEventPublisher(Protocol):
    async def publish(
        self,
        event: NotificationDomainEvent,
        *,
        unit_of_work: IUnitOfWork,
    ) -> None: ...
```

Infrastructure writes to the transactional outbox (`outbox_events`) table. Downstream workers on the `notification` queue deliver side effects such as badge count refresh and future email/webhook dispatch.

## Event publishing rules

- Events are optional at composition time (`event_publisher: INotificationEventPublisher | None = None`).
- When wired, handlers publish **before** `unit_of_work.flush()` inside the active transaction.
- `MarkAllReadHandler` does not emit per-notification `NotificationRead` events; bulk read is handled at the repository layer without individual outbox fan-out.
- Event payloads never include secrets, provider credentials, or cross-recipient data.

## Naming and versioning

Outbox records use dotted past-tense names aligned with backend architecture conventions:

| Event class            | Suggested outbox `event_type`      |
| ---------------------- | ---------------------------------- |
| `NotificationCreated`  | `notification.created`             |
| `NotificationRead`     | `notification.read`                |
| `NotificationArchived` | `notification.archived`            |
| `NotificationDeleted`  | `notification.deleted`             |
| `PreferencesUpdated`   | `notification.preferences_updated` |

Set `event_version` independently from aggregate `version` when schema evolves.

## Consumer guidance

- Treat delivery as at-least-once; handlers must be idempotent.
- Use `notification_id` + `event_type` for deduplication where needed.
- Do not infer recipient access from events without verifying workspace membership.
