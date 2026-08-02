# Task Catalog

All registered Celery tasks, queues, and categories.

## Asset Tasks (`media`)

| Task                                          | Handler                     |
| --------------------------------------------- | --------------------------- |
| `cloud_content_hub.tasks.upload_asset`        | `UploadAssetHandler`        |
| `cloud_content_hub.tasks.replace_asset`       | `ReplaceAssetHandler`       |
| `cloud_content_hub.tasks.delete_asset`        | `DeleteAssetHandler`        |
| `cloud_content_hub.tasks.restore_asset`       | `RestoreAssetHandler`       |
| `cloud_content_hub.tasks.virus_scan`          | Audit-logged worker handler |
| `cloud_content_hub.tasks.metadata_extraction` | Audit-logged worker handler |

## Content Tasks

| Task                                         | Queue         | Handler                    |
| -------------------------------------------- | ------------- | -------------------------- |
| `cloud_content_hub.tasks.generate_content`   | `ai`          | `GenerateContentHandler`   |
| `cloud_content_hub.tasks.regenerate_content` | `ai`          | `RegenerateContentHandler` |
| `cloud_content_hub.tasks.duplicate_content`  | `maintenance` | `DuplicateContentHandler`  |
| `cloud_content_hub.tasks.archive_content`    | `maintenance` | `ArchiveContentHandler`    |

## Publishing Tasks (`maintenance`)

| Task                                            | Handler                                                   |
| ----------------------------------------------- | --------------------------------------------------------- |
| `cloud_content_hub.tasks.publish_content`       | `CreatePublicationHandler` + `DispatchPublicationHandler` |
| `cloud_content_hub.tasks.retry_publish`         | `DispatchPublicationHandler`                              |
| `cloud_content_hub.tasks.cancel_publish`        | `CancelPublicationHandler`                                |
| `cloud_content_hub.tasks.verify_publish_status` | Audit-logged worker handler                               |

## Analytics Tasks (`maintenance`)

| Task                                        | Handler                           |
| ------------------------------------------- | --------------------------------- |
| `cloud_content_hub.tasks.import_analytics`  | `ImportAnalyticsHandler`          |
| `cloud_content_hub.tasks.refresh_dashboard` | `RefreshDashboardCacheHandler`    |
| `cloud_content_hub.tasks.archive_snapshot`  | `ArchiveAnalyticsSnapshotHandler` |

## Notification Tasks (`notification`)

| Task                                            | Handler                     |
| ----------------------------------------------- | --------------------------- |
| `cloud_content_hub.tasks.deliver_notification`  | `CreateNotificationHandler` |
| `cloud_content_hub.tasks.retry_notification`    | Audit-logged worker handler |
| `cloud_content_hub.tasks.cleanup_notifications` | Audit-logged worker handler |

## Maintenance Tasks (`maintenance`)

| Task                                             | Handler                           |
| ------------------------------------------------ | --------------------------------- |
| `cloud_content_hub.tasks.cleanup_temp_files`     | Audit-logged worker handler       |
| `cloud_content_hub.tasks.cleanup_expired_tokens` | Audit-logged worker handler       |
| `cloud_content_hub.tasks.cleanup_soft_deletes`   | Audit-logged worker handler       |
| `cloud_content_hub.tasks.cleanup_outbox`         | `OutboxDispatcher.dispatch_batch` |
| `cloud_content_hub.tasks.cleanup_failed_jobs`    | Audit-logged worker handler       |

## Scheduler Tasks (`maintenance`)

| Task                                                  | Handler                                             |
| ----------------------------------------------------- | --------------------------------------------------- |
| `cloud_content_hub.tasks.execute_scheduled_publish`   | `GetScheduleHandler` + `DispatchPublicationHandler` |
| `cloud_content_hub.tasks.execute_scheduled_analytics` | `RefreshDashboardCacheHandler`                      |
| `cloud_content_hub.tasks.execute_scheduled_cleanup`   | Audit-logged worker handler                         |

## Outbox Tasks (`maintenance`)

| Task                                     | Handler                         |
| ---------------------------------------- | ------------------------------- |
| `cloud_content_hub.deliver_outbox_event` | `OutboxDeliveryService.deliver` |

## Payload Shape

Standard tasks accept a `WorkerTaskPayload` JSON document:

```json
{
  "workspace_id": "uuid",
  "actor_id": "uuid",
  "job_id": "uuid",
  "resource_type": "asset",
  "resource_id": "uuid",
  "idempotency_key": "key",
  "attempt_count": 0,
  "correlation_id": "corr-1",
  "request_id": "req-1",
  "command": {}
}
```

Outbox delivery tasks receive `{ "envelope": { ... EventEnvelope ... } }` instead.
