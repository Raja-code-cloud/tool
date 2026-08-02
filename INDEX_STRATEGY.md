# Index Strategy

PostgreSQL 17 baseline for the **86-table** schema. Indexes support explicit tenant predicates first, integrity second, and measured product queries third. Names follow `ix_<table>__<columns>[_where_<predicate>]` and `uq_<table>__...`.

## Mandatory rules

1. Primary keys create `pk_<table>` B-trees on `id`, but workspace queries must not rely on the global PK alone.
2. Every WS table gets `uq_<table>__workspace_id_id UNIQUE (workspace_id,id)`. Every composite child FK gets a matching child index beginning with `(workspace_id,<fk_column>)`; PostgreSQL does not create FK indexes automatically.
3. Every soft-deletable parent referenced by a tenant-safe FK retains the non-partial `(workspace_id,id)` unique constraint. Business-key uniqueness is partial on active rows.
4. Default cursor order is `(updated_at DESC,id DESC)` for mutable resources and `(occurred_at DESC,id DESC)` for events. Queries use matching tuple comparisons, never large `OFFSET`.
5. Use `CREATE INDEX CONCURRENTLY`; add unique constraints with a concurrently built unique index where supported. Do not run concurrent index DDL inside a transaction.
6. `INCLUDE` columns are projection-only. Keep wide text/jsonb out of B-trees. GIN is deliberate; no blanket indexing of JSON.
7. Every table has all six universal audit columns. Their presence does not imply indexing all six: mutable cursor indexes use `updated_at`; active-row uniqueness uses `deleted_at`; immutable retention uses partition time/`created_at` or the domain occurrence time while fixed `updated_at`, null `deleted_at`, and constant `version` are intentionally not indexed.

## Universal audit and retention indexes

- For every high-volume mutable soft-delete table, add `ix_<table>__purge_deleted_at ON <table> (deleted_at,id) WHERE deleted_at IS NOT NULL` only when the privileged purge plan demonstrates need; avoid 86 low-value duplicate indexes.
- For nonpartitioned immutable tables, retention scans use `ix_<table>__created_at ON <table> (created_at,id)` unless a more accurate indexed domain time (`occurred_at`, `received_at`, `finished_at`) is the retention key.
- Immutable audit-shape enforcement is a check/trigger/privilege concern, not an index. Do not index fixed `updated_at = created_at`, `deleted_at IS NULL`, or `version = 1`.
- Junctions keep their relationship indexes and all six audit columns. Add `(deleted_at,id)` only if policy changes from immediate hard-delete to deferred purge.

## Identity and tenancy

- `uq_external_identities__issuer_subject ON external_identities (issuer,subject)` — permanent subject mapping.
- `uq_users__email_where_active ON users (email) WHERE deleted_at IS NULL AND email IS NOT NULL`.
- `ix_user_sessions__user_expires ON user_sessions (user_id,expires_at DESC)` and `uq_user_sessions__session_hash ON user_sessions (session_hash)`.
- `uq_organizations__slug_where_active ON organizations (slug) WHERE deleted_at IS NULL`.
- `ix_organization_memberships__organization_user ON organization_memberships (organization_id,user_id) WHERE deleted_at IS NULL`.
- `uq_workspaces__organization_slug_where_active ON workspaces (organization_id,slug) WHERE deleted_at IS NULL`.
- `ix_workspace_memberships__workspace_status_user ON workspace_memberships (workspace_id,status,user_id) WHERE deleted_at IS NULL`.
- `uq_workspace_memberships__workspace_user_where_active ON workspace_memberships (workspace_id,user_id) WHERE deleted_at IS NULL`.
- `uq_roles__workspace_code_where_active ON roles (workspace_id,code) NULLS NOT DISTINCT WHERE deleted_at IS NULL`; global/system and WS names remain collision-safe.
- `ix_role_permissions__role_id ON role_permissions (role_id)`; `ix_role_permissions__permission_id ON role_permissions (permission_id)`.
- `ix_membership_roles__workspace_membership ON membership_roles (workspace_id,membership_id)` and `ix_membership_roles__workspace_role ON membership_roles (workspace_id,role_id)`.

## Projects, content, and collaboration

- `uq_projects__workspace_slug_where_active ON projects (workspace_id,slug) WHERE deleted_at IS NULL`.
- `ix_projects__workspace_updated_cursor ON projects (workspace_id,updated_at DESC,id DESC) WHERE deleted_at IS NULL`.
- `ix_folders__workspace_parent_name ON folders (workspace_id,parent_folder_id,name) WHERE deleted_at IS NULL`; use `NULLS NOT DISTINCT` unique form for roots.
- `ix_collections__workspace_updated_cursor ON collections (workspace_id,updated_at DESC,id DESC) WHERE deleted_at IS NULL`.
- `ix_collection_items__workspace_collection_position ON collection_items (workspace_id,collection_id,position,id)`; reverse FK `ix_collection_items__workspace_asset ON ... (workspace_id,asset_id)`.
- `uq_tags__workspace_name_where_active`, `uq_categories__workspace_slug_where_active`; self-FK indexes on `(workspace_id,parent_category_id)`.
- Bridge indexes: `ix_asset_tags__workspace_tag_asset`, `ix_asset_categories__workspace_category_asset`, plus PK/unique asset-first forms.
- `ix_content_assets__workspace_updated_cursor ON content_assets (workspace_id,updated_at DESC,id DESC) INCLUDE (title,asset_type,lifecycle_status,owner_id) WHERE deleted_at IS NULL`.
- `ix_content_assets__workspace_type_status_updated ON content_assets (workspace_id,asset_type,lifecycle_status,updated_at DESC,id DESC) WHERE deleted_at IS NULL`.
- `ix_content_assets__workspace_owner_updated ON content_assets (workspace_id,owner_id,updated_at DESC,id DESC) WHERE deleted_at IS NULL`.
- `ix_content_assets__workspace_project_updated` and `ix_content_assets__workspace_folder_updated` on corresponding FK plus cursor columns.
- `ix_content_assets__search_gin ON content_assets USING gin (search_document)` for weighted title/summary/tag search. Maintain a normalized `tsvector`; do not GIN arbitrary content JSON.
- Subtype tables: unique tenant-safe `(workspace_id,asset_id)` plus `ix_videos__workspace_transcript_status`, used only if transcript operations are measured.
- `uq_storage_objects__workspace_object_key_where_active ON storage_objects (workspace_id,object_key) WHERE deleted_at IS NULL`.
- `ix_storage_objects__workspace_scan_due ON storage_objects (workspace_id,created_at,id) WHERE deleted_at IS NULL AND scan_status IN ('pending','failed')`.
- `ix_storage_objects__workspace_checksum ON storage_objects (workspace_id,checksum_sha256,byte_size) WHERE deleted_at IS NULL`.
- `ix_asset_storage_objects__workspace_asset_purpose ON asset_storage_objects (workspace_id,asset_id,purpose,variant_key,position)` and reverse object index.
- `uq_content_drafts__workspace_asset_where_active ON content_drafts (workspace_id,asset_id) WHERE deleted_at IS NULL`.
- `ix_content_versions__workspace_asset_version_desc ON content_versions (workspace_id,asset_id,version_number DESC) INCLUDE (created_at,origin,content_hash)`.
- `uq_content_versions__workspace_asset_number`; content hash uniqueness as specified.
- `ix_comments__workspace_asset_created_cursor ON comments (workspace_id,asset_id,created_at DESC,id DESC) WHERE deleted_at IS NULL`; `ix_comments__workspace_parent` for threads.
- `ix_approval_requests__workspace_pending ON approval_requests (workspace_id,requested_at,id) WHERE deleted_at IS NULL AND status='pending'`.
- `ix_approval_steps__workspace_reviewer_pending ON approval_steps (workspace_id,reviewer_user_id,created_at,id) WHERE deleted_at IS NULL AND status='pending'`.
- `uq_asset_categories__one_primary ON asset_categories (workspace_id,asset_id) WHERE is_primary`.
- `uq_brand_profiles__one_default ON brand_profiles (workspace_id) WHERE deleted_at IS NULL AND is_default`.
- `ix_saved_views__workspace_owner_type ON saved_views (workspace_id,owner_id,view_type,name) WHERE deleted_at IS NULL`.
- Project members and content relations receive both directional FK indexes: `(workspace_id,project_id)`, `(workspace_id,user_id)`, `(workspace_id,source_asset_id)`, `(workspace_id,target_asset_id)`.

## AI

- `uq_ai_providers__code`, `uq_ai_models__provider_model_code`, and `ix_ai_models__provider_status ON ai_models (provider_id,status)`.
- `ix_ai_prompt_templates__workspace_name_version_desc ON ai_prompt_templates (workspace_id,name,template_version DESC) WHERE deleted_at IS NULL`.
- `uq_ai_generation_requests__workspace_idempotency ON ai_generation_requests (workspace_id,idempotency_key)`.
- `ix_ai_generation_requests__workspace_due ON ai_generation_requests (workspace_id,created_at,id) WHERE deleted_at IS NULL AND status='queued'`.
- `ix_ai_generation_requests__workspace_asset_cursor ON ai_generation_requests (workspace_id,asset_id,created_at DESC,id DESC) WHERE deleted_at IS NULL`.
- `ix_ai_generation_requests__provider_request ON ai_generation_requests (model_id,provider_request_id) WHERE provider_request_id IS NOT NULL`.
- `ix_ai_generation_outputs__workspace_request_sequence`; `ix_ai_generation_outputs__materialized_version` where non-null.
- `ix_ai_usage_records__workspace_created ON ai_usage_records (workspace_id,created_at DESC,id DESC)` and provider/model/date indexes for reconciliation.
- `ix_ai_suggestions__workspace_asset_open ON ai_suggestions (workspace_id,asset_id,created_at DESC,id DESC) WHERE deleted_at IS NULL AND status='open'`.
- `ix_ai_suggestion_actions__workspace_suggestion_created ON ai_suggestion_actions (workspace_id,suggestion_id,created_at,id)`.

## Social

- Catalog uniques: `uq_social_platforms__code`, `uq_social_platform_capabilities__platform_code_effective`, `uq_social_content_templates__scope_platform_name_version`.
- `uq_social_accounts__workspace_platform_external_where_active ON social_accounts (workspace_id,platform_id,external_account_id) WHERE deleted_at IS NULL`.
- `ix_social_accounts__workspace_health ON social_accounts (workspace_id,connection_status,health_status,updated_at DESC,id DESC) WHERE deleted_at IS NULL`.
- `ix_social_accounts__workspace_sync_due ON social_accounts (workspace_id,last_sync_at,id) WHERE deleted_at IS NULL AND connection_status='connected'`.
- `uq_oauth_token_vaults__workspace_account_where_active`; `ix_oauth_token_vaults__expiry_due ON oauth_token_vaults (expires_at,social_account_id) WHERE deleted_at IS NULL AND status IN ('active','expiring_soon')` with restricted ownership.
- Permission and settings FKs use `(workspace_id,social_account_id)`; permissions additionally unique on permission code.

## Publishing, due work, and jobs

- `ix_publications__workspace_asset_cursor ON publications (workspace_id,asset_id,updated_at DESC,id DESC) WHERE deleted_at IS NULL`.
- `ix_publication_targets__workspace_publication ON publication_targets (workspace_id,publication_id,id) WHERE deleted_at IS NULL`.
- `ix_publication_targets__workspace_account_published ON publication_targets (workspace_id,social_account_id,published_at DESC,id DESC) WHERE deleted_at IS NULL`.
- `ix_publication_targets__external_post ON publication_targets (platform_id,external_post_id) WHERE external_post_id IS NOT NULL`.
- `ix_publication_schedules__due ON publication_schedules (scheduled_for,priority DESC,id) INCLUDE (workspace_id,publication_target_id) WHERE deleted_at IS NULL AND state='scheduled'` — dispatcher global due scan under a dedicated role.
- `ix_publication_schedules__workspace_calendar ON publication_schedules (workspace_id,scheduled_for,id) INCLUDE (state,publication_target_id) WHERE deleted_at IS NULL AND state IN ('scheduled','paused','dispatched','completed','failed')`.
- `uq_publication_schedules__active_target ON publication_schedules (workspace_id,publication_target_id) WHERE deleted_at IS NULL AND state IN ('scheduled','paused','dispatched')`.
- `uq_publishing_jobs__workspace_idempotency`; `ix_publishing_jobs__claim ON publishing_jobs (available_at,priority DESC,id) INCLUDE (workspace_id) WHERE deleted_at IS NULL AND state IN ('queued','retry_wait')`.
- `ix_publishing_jobs__workspace_status_cursor ON publishing_jobs (workspace_id,state,updated_at DESC,id DESC) WHERE deleted_at IS NULL`.
- `ix_publishing_attempts__workspace_job_attempt ON publishing_attempts (workspace_id,publishing_job_id,attempt_no DESC)`.
- `ix_publication_status_history__workspace_target_time ON publication_status_history (workspace_id,publication_target_id,occurred_at DESC,id DESC)`.
- `ix_job_leases__expired ON job_leases (leased_until,id)` and `uq_job_leases__lease_token`; expired-row deletion is frequent.
- `ix_dead_letters__workspace_pending ON dead_letters (workspace_id,failed_at,id) WHERE deleted_at IS NULL AND replay_state='pending'`.

## Notifications and settings

- Catalog/template unique indexes match scope/type/channel/locale/version; active template lookup additionally indexes `(notification_type_id,channel,locale,is_active)`.
- `uq_notification_preferences__workspace_user_type_channel_where_active`.
- `ix_notifications__workspace_recipient_unread ON notifications (workspace_id,recipient_user_id,created_at DESC,id DESC) WHERE deleted_at IS NULL AND read_at IS NULL`.
- `ix_notifications__workspace_recipient_cursor` supports full inbox.
- `ix_notification_deliveries__due ON notification_deliveries (created_at,id) INCLUDE (workspace_id,channel) WHERE deleted_at IS NULL AND status IN ('pending','failed')`.
- `uq_notification_deliveries__notification_recipient_channel_where_active`.
- `uq_setting_definitions__key`.
- Scope-specific partial uniques for `settings`, e.g. `uq_settings__workspace_definition ON settings (workspace_id,definition_id) WHERE deleted_at IS NULL AND scope_type='workspace'`; equivalent organization/user/project/social-account indexes avoid a polymorphic COALESCE index.
- Resolution indexes put target first, then definition; never scan all settings JSON. Optional `gin (value jsonb_path_ops)` is allowed only for an evidenced administrative query.

## Analytics

- `uq_metric_definitions__code_version_platform` uses `NULLS NOT DISTINCT`.
- Partition-local `uq_metric_observations__workspace_metric_fingerprint`.
- `ix_metric_observations__workspace_metric_time ON metric_observations (workspace_id,metric_definition_id,observed_at DESC,id DESC)`.
- `ix_metric_observations__workspace_target_time` variants for `(publication_target_id,metric_definition_id,observed_at)` and `(social_account_id,metric_definition_id,observed_at)`.
- `brin_metric_observations__observed_at ON metric_observations USING brin (observed_at) WITH (pages_per_range=64)` per large partition.
- Snapshot indexes: `(workspace_id,snapshot_type,period_end DESC,id DESC)`, `(workspace_id,content_asset_id,snapshot_at DESC)`, `(workspace_id,social_account_id,snapshot_at DESC)`.
- JSON snapshot payloads are not indexed by default; dashboard lookup keys are relational.

## Usage and billing

- `uq_usage_dimensions__code`.
- Partition-local `uq_usage_events__workspace_dedupe`; `ix_usage_events__workspace_dimension_time`; `ix_usage_events__organization_dimension_time`.
- `brin_usage_events__occurred_at USING brin (occurred_at) WITH (pages_per_range=64)`.
- `ix_quota_policies__workspace_dimension_effective` and organization equivalent, active rows first.
- `uq_quota_periods__scope_dimension_period` with scope-specific partial indexes; this is the lock target for atomic reserve/consume updates.
- `uq_subscriptions__provider_external`; partial `uq_subscriptions__one_current_org ON subscriptions (organization_id) WHERE deleted_at IS NULL AND status IN ('trialing','active','past_due','paused')`.
- `ix_subscription_items__organization_subscription`, `uq_billing_customers__provider_external`, and `uq_billing_events__provider_event`.
- Billing event time index `(organization_id,occurred_at DESC,id DESC)` supports evidence/export.

## Reliability, audit, and operations

- `ix_activity_logs__workspace_cursor ON activity_logs (workspace_id,occurred_at DESC,id DESC) WHERE deleted_at IS NULL AND hidden_at IS NULL`.
- Partition-local `ix_audit_logs__workspace_time ON audit_logs (workspace_id,occurred_at DESC,id DESC)` and organization equivalent.
- `brin_audit_logs__occurred_at USING brin (occurred_at) WITH (pages_per_range=64)`.
- `uq_idempotency_keys__scope_principal_operation_key_where_active` with `NULLS NOT DISTINCT`; `ix_idempotency_keys__expiry ON idempotency_keys (expires_at,id)`.
- `ix_outbox_events__publish_due ON outbox_events (available_at,id) WHERE published_at IS NULL`; `ix_outbox_events__aggregate ON ... (aggregate_type,aggregate_id,occurred_at,id)`.
- `brin_outbox_events__occurred_at` for retention scans.
- `uq_inbox_messages__consumer_message`; `ix_inbox_messages__retention ON inbox_messages (processed_at,id) WHERE processed_at IS NOT NULL`.
- `uq_webhook_receipts__provider_external`; fallback unique `(provider_code,payload_hash)` only for providers without event IDs.
- `ix_webhook_receipts__unprocessed ON webhook_receipts (received_at,id) WHERE processed_at IS NULL AND processing_status IN ('received','failed')`.
- `ix_background_jobs__claim ON background_jobs (available_at,priority DESC,id) INCLUDE (workspace_id,queue_name) WHERE deleted_at IS NULL AND state IN ('queued','retry_wait')`.
- `ix_background_jobs__expired_lease ON background_jobs (leased_until,id) WHERE deleted_at IS NULL AND state IN ('leased','running')`.
- `ix_data_exports__workspace_cursor` and `ix_data_exports__expiry ON data_exports (expires_at,id) WHERE deleted_at IS NULL AND state IN ('ready','expired')`.

## Index operations and review

- Validate plans with representative tenant cardinalities and `EXPLAIN (ANALYZE,BUFFERS)` in staging. Watch write amplification, unused indexes, bloat, cache hit ratio, and partition-local index skew.
- Remove redundant prefix indexes only after confirming FK enforcement and all query shapes. Reindex concurrently when required.
- Keep statistics current; raise per-column statistics targets selectively for skewed `state`, `platform_id`, and large-tenant distributions.
- Extended statistics candidates: `(workspace_id,state)`, `(workspace_id,asset_type,lifecycle_status)`, and `(workspace_id,social_account_id,scheduled_for)`.
- Global due scanners run under dedicated least-privilege roles and never expose fetched rows to request contexts. Product reads remain workspace-first.
