# Workflow Matrix

| #   | Workflow                                           | Entry Point                                    | Key Assertions                                       | Test Module                       | Status    |
| --- | -------------------------------------------------- | ---------------------------------------------- | ---------------------------------------------------- | --------------------------------- | --------- |
| 1   | User login → workspace → auth → authorization      | Mock OAuth + JWT                               | Token issued, workspace scoped, permissions enforced | `test_auth_workflow.py`           | Automated |
| 2   | Upload poster → blob → metadata → outbox           | `UploadAssetHandler` / HTTP                    | Job queued, `asset.uploaded` outbox row              | `test_asset_upload_workflow.py`   | Automated |
| 3   | Upload master article → store → generate → approve | `UploadAssetHandler`, `GenerateContentHandler` | Article job queued, generation job queued            | `test_content_workflow.py`        | Automated |
| 4   | Upload video → blob → thumbnail → metadata         | `UploadAssetHandler`                           | Media job queued, video asset readable               | `test_video_upload_workflow.py`   | Automated |
| 5   | Generate content → prompt → AI → version           | `GenerateContentHandler`                       | Generation job queued, `content.generated` event     | `test_content_workflow.py`        | Automated |
| 6   | Schedule publication → scheduler → Celery → outbox | `CreateScheduleHandler`                        | Schedule created, outbox drain succeeds              | `test_publishing_workflow.py`     | Automated |
| 7   | LinkedIn publish                                   | `CreatePublicationHandler` + dispatch          | Publication + dispatch job queued                    | `test_publishing_workflow.py`     | Automated |
| 8   | Facebook publish                                   | Parametrized platform publish                  | Same as #7                                           | `test_publishing_workflow.py`     | Automated |
| 9   | Instagram publish                                  | Parametrized platform publish                  | Same as #7                                           | `test_publishing_workflow.py`     | Automated |
| 10  | X publish                                          | Parametrized platform publish                  | Same as #7                                           | `test_publishing_workflow.py`     | Automated |
| 11  | Medium publish                                     | Parametrized platform publish                  | Same as #7                                           | `test_publishing_workflow.py`     | Automated |
| 12  | YouTube publish                                    | Parametrized platform publish                  | Same as #7                                           | `test_publishing_workflow.py`     | Automated |
| 13  | Analytics import → dashboard → aggregations        | `ImportAnalyticsHandler`, dashboard queries    | Observations imported, dashboard readable            | `test_analytics_workflow.py`      | Automated |
| 14  | Notification delivery → retry → cleanup            | Worker notification task                       | Notification created, outbox event published         | `test_notification_workflow.py`   | Automated |
| 15  | Administration → roles → flags → maintenance       | Admin handlers                                 | Role assigned, flags listed, maintenance enabled     | `test_administration_workflow.py` | Automated |

## Failure Scenario Matrix

| Scenario                          | Validation                       | Test Module                  |
| --------------------------------- | -------------------------------- | ---------------------------- |
| Blob upload failure               | `StorageUnavailableError` raised | `test_failure_scenarios.py`  |
| AI timeout                        | Failing mock provider            | `test_failure_scenarios.py`  |
| OAuth failure                     | Invalid state rejected           | `test_failure_scenarios.py`  |
| Provider outage                   | Outbox retry scheduled           | `test_failure_scenarios.py`  |
| Scheduler/worker retry exhaustion | Retry policy stops               | `test_failure_scenarios.py`  |
| Dead letter queue                 | Poison message moved             | `test_recovery_scenarios.py` |
| Outbox replay                     | Celery task enqueued             | `test_failure_scenarios.py`  |
| Database disconnect               | Connectivity probe               | `test_failure_scenarios.py`  |
| Redis disconnect                  | Ping probe                       | `test_failure_scenarios.py`  |

## Security Matrix

| Control                | Validation                 | Test Module                   |
| ---------------------- | -------------------------- | ----------------------------- |
| Workspace isolation    | Foreign asset not readable | `test_security_validation.py` |
| Permission enforcement | Missing scope rejected     | `test_security_validation.py` |
| JWT validation         | Tampered token rejected    | `test_security_validation.py` |
| OAuth validation       | State mismatch rejected    | `test_security_validation.py` |
| Soft delete visibility | Deleted rows hidden        | `test_security_validation.py` |
| Optimistic locking     | Stale version rejected     | `test_security_validation.py` |
