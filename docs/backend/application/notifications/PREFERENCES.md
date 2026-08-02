# Notification Preferences

## Overview

Notification preferences control per-recipient channel enablement for each notification type within a workspace. Preferences are stored in `notification_preferences` and accessed through `INotificationPreferenceRepository`.

## Preference model

Each preference row is keyed by:

- `workspace_id`
- `user_id`
- `notification_type_id` (resolved from `type_code` at the repository layer)
- `channel`

Fields exposed to the application layer:

| Field               | Description                                  |
| ------------------- | -------------------------------------------- |
| `type_code`         | Notification type code from the catalog      |
| `channel`           | `in_app`, `email`, or `webhook`              |
| `enabled`           | Whether the channel is enabled for this type |
| `quiet_hours_start` | Optional quiet-hours start (local time)      |
| `quiet_hours_end`   | Optional quiet-hours end (local time)        |
| `time_zone`         | IANA time zone for quiet-hours evaluation    |

## Update flow

`UpdatePreferencesHandler` accepts `UpdatePreferencesRequestDto` containing one or more `NotificationPreferenceItemRequestDto` rows.

Handler steps:

1. Require `notifications:write` permission.
2. Validate quiet-hours pairs and time zone for each item.
3. Resolve and validate each `type_code` against the notification type catalog.
4. Upsert preference rows via `INotificationPreferenceRepository.upsert_many`.
5. Publish `PreferencesUpdated` when an event publisher is wired.
6. Return updated `NotificationPreferenceResponseDto` projections.

## Query flow

`GetPreferencesHandler` lists all preferences for `actor.user_id` in the current workspace and maps them to `NotificationPreferenceResponseDto`.

## Channel resolution at creation

When `CreateNotificationHandler` creates a notification, `NotificationDeliveryService.resolve_channels`:

1. Loads existing preferences for the recipient.
2. Reads default channels from the notification type catalog.
3. Filters to supported channels (`in_app` only today).
4. Respects user opt-out (`enabled=false`) per type and channel.
5. Falls back to `in_app` when no channel remains enabled.

Future email and webhook providers consume the resolved channel list without changing handler contracts.

## Validation rules

- `quietHoursStart` and `quietHoursEnd` must both be set or both omitted.
- `type_code` must exist in the notification type catalog or known type map.
- Only catalog-defined channels are accepted on preference rows.
- Preferences are recipient-scoped; handlers never expose another user's preferences.

## Default behavior

When no preference row exists for a `(type_code, channel)` pair, the channel defaults to **enabled**. This preserves inbox delivery for new notification types until the user opts out.

## Permissions

| Operation          | Permission            |
| ------------------ | --------------------- |
| List preferences   | `notifications:read`  |
| Update preferences | `notifications:write` |
