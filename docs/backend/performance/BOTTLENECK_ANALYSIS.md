# Bottleneck Analysis

Identified performance constraints and their mitigation paths for the Cloud Content Hub backend.

## Summary

| Rank | Bottleneck | Severity | Layer | Mitigation |
| --- | --- | --- | --- | --- |
| 1 | Database connection pool under concurrent search | High | DB | PgBouncer, read replica, index tuning |
| 2 | AI provider latency for content generation | High | External | Queue depth scaling, provider failover |
| 3 | Outbox poll batch size vs. transaction duration | Medium | Events | Tune `batch_size`, horizontal pollers |
| 4 | Azure Blob upload for large media | Medium | Storage | Chunked upload, CDN, async worker queue |
| 5 | Social provider rate limits on publish | Medium | External | Retry backoff, staggered scheduler |
| 6 | Serialization overhead on paged responses | Low | API | Response compression (gzip enabled) |

## 1. Database Connection Pool

**Symptom:** P95 latency spikes under 20+ concurrent repository sessions; `database_pool`
gauge approaches configured maximum.

**Root cause:** Each HTTP request and worker task acquires a session from the async pool.
Search queries with ILIKE and sort hold connections longer than simple PK lookups.

**Evidence:** `test_connection_pool_stress.py` — concurrent search at 20 × 5 shows P99 growth
proportional to pool contention.

**Recommendations:**

- Enable PgBouncer in transaction mode for API replicas
- Add composite index on `(workspace_id, updated_at DESC)` for asset/content list queries
- Route analytics reads to a read replica
- Monitor `cloud_content_hub_database_operation_duration_seconds`

## 2. AI Provider Latency

**Symptom:** Content generation P95 exceeds 300 ms at the API accept boundary when provider
latency is included in end-to-end measurement (not the 202 acceptance path).

**Root cause:** External LLM calls (OpenAI, Claude, Gemini) range from 1–30 s. The API returns
202 immediately, but user-perceived latency depends on worker + provider.

**Evidence:** MockProvider baseline ~1 ms; production providers are network-bound.

**Recommendations:**

- Scale `ai` queue workers independently
- Use `cloud_content_hub_ai_request_duration_seconds` for per-provider tracking
- Implement provider circuit breaker (already in retry policy)
- Cap concurrent generations per workspace via quota

## 3. Outbox Dispatch Throughput

**Symptom:** Outbox lag warning (> 60 s) under high write volume.

**Root cause:** Single-threaded poll cycle claims up to `batch_size` rows per transaction.
Large batches increase lock duration; small batches increase poll overhead.

**Evidence:** `OutboxDispatcher.dispatch_batch` P95 scales with batch size in stress tests.

**Recommendations:**

- Tune `EventPublishingConfig.batch_size` (default 100) per environment
- Run multiple worker replicas executing `cleanup_outbox`
- Monitor `cloud_content_hub_queue_latency_seconds`
- See [OUTBOX_PATTERN.md](../events/OUTBOX_PATTERN.md)

## 4. Storage I/O

**Symptom:** Media upload worker tasks queue depth grows during bulk asset imports.

**Root cause:** Large file uploads block worker threads during blob transfer. Azure SDK
retries add latency on transient failures.

**Evidence:** Stress test with ~96 KB payloads shows linear P99 growth at 20 concurrent uploads.

**Recommendations:**

- Keep uploads on dedicated `media` queue with separate worker pool
- Use block/chunk upload for files > 4 MB
- Monitor `cloud_content_hub_blob_bytes_total` and operation counters
- See [UPLOAD_FLOW.md](../storage/UPLOAD_FLOW.md)

## 5. Social Provider Rate Limits

**Symptom:** Publication dispatch retries increase; `retries_total{component="provider"}` rises.

**Root cause:** LinkedIn, Facebook, Instagram, X, Medium, and YouTube enforce per-app rate limits.
Bulk scheduled publishing creates spikes.

**Evidence:** Platform constraints validated in `test_provider_benchmarks.py`; live limits
are external.

**Recommendations:**

- Stagger scheduled publishes via scheduler jitter
- Use `retry_publish` task with exponential backoff
- Monitor per-platform health via admin `/api/v1/admin/providers`
- Respect `ProviderRateLimitError` in worker retry policy

## 6. API Serialization

**Symptom:** Marginal P95 increase on large paged responses (> 100 items).

**Root cause:** Pydantic serialization and envelope wrapping for each item in page.

**Evidence:** Mocked handler tests show sub-15 ms P95; full-stack with large pages may differ.

**Recommendations:**

- Gzip middleware already enabled in bootstrap
- Enforce `limit` max of 100 per [PAGINATION.md](../repositories/PAGINATION.md)
- Consider field projection for list endpoints in future optimization (out of scope)

## Non-Bottlenecks (Validated)

| Component | Observation |
| --- | --- |
| JWT authentication | Sub-ms principal resolution in mock tests |
| Task route resolution | Sub-0.2 ms for all 30+ registered tasks |
| Retry classification | Sub-0.02 ms P95 |
| Health probes | Sub-10 ms P95 |
| In-memory outbox fetch | Sub-1 ms P95 for 100 rows |

## Monitoring Dashboards

Prioritize these metrics for bottleneck detection:

1. HTTP P95 by route (`http_request_duration_seconds`)
2. Worker job duration by task (`worker_job_duration_seconds`)
3. Queue depth and latency by queue name
4. Database operation duration and pool utilization
5. Outbox lag (`OutboxHealthCheck`)
6. Scheduler lag (`scheduler_lag_seconds`)

See [PROMETHEUS.md](../observability/PROMETHEUS.md) and [ALERTING.md](../observability/ALERTING.md).

## Next Steps

1. Run staging Locust/k6 scenarios and compare against this analysis
2. Profile top 5 slow SQL queries under load
3. Validate autoscaling rules in Azure Container Apps
4. Document environment-specific tuning in [TUNING_GUIDE.md](./TUNING_GUIDE.md)
