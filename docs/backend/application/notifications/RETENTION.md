# Notification Retention

## Overview

Notifications support configurable retention through `RetentionPolicy` on create requests. Expiry is resolved in the application layer by `RetentionService` and persisted as `expires_at` on the notification aggregate.

## Retention policies

| Policy      | `expires_at`          | Use case                                       |
| ----------- | --------------------- | ---------------------------------------------- |
| `standard`  | Created at + 90 days  | Default product and system notifications       |
| `extended`  | Created at + 365 days | Long-lived operational notices                 |
| `permanent` | `null`                | Security and compliance-critical notifications |

Constants are defined in `notification_validator.py`:

- `STANDARD_RETENTION_DAYS = 90`
- `EXTENDED_RETENTION_DAYS = 365`

## Resolution flow

1. `CreateNotificationHandler` validates the request via `validate_create_request`.
2. `RetentionService.resolve_expires_at` converts `RetentionPolicy` to a UTC `datetime | None`.
3. `NewNotification.expires_at` is passed to `INotificationRepository.create`.
4. Repository implementations persist `expires_at` on the `notifications` row.

## Validation

- `retention_policy` is validated at the DTO layer via `RetentionPolicyRequestDto`.
- Priority and severity validation is independent of retention; high-priority notifications may use any retention policy.
- Expired notifications remain governed by repository search filters; purge of expired rows is a maintenance worker concern outside this module.

## Interaction with archive and delete

| Operation   | Retention impact                                                     |
| ----------- | -------------------------------------------------------------------- |
| Archive     | Does not change `expires_at`; archived items remain searchable       |
| Soft delete | Sets `deleted_at`; item becomes non-disclosable regardless of expiry |
| Mark read   | Does not change `expires_at`                                         |

## Priority and severity

Delivery priority (`low`, `normal`, `high`) does not alter retention duration. Priority affects minimum severity validation:

| Priority | Minimum severity |
| -------- | ---------------- |
| `low`    | `info`           |
| `normal` | `info`           |
| `high`   | `warning`        |

## Future maintenance

A scheduled maintenance job (out of scope for this module) should:

1. Soft-delete or purge notifications where `expires_at < now()` and policy allows disposal.
2. Retain delivery audit rows in `notification_deliveries` per database retention design.
3. Honor legal hold and workspace closure policies from the database documentation.

Application handlers do not perform expiry purge directly.
