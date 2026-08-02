# Table Specifications

**PostgreSQL 17 · authoritative inventory: 86 tables.**

## Reading rules

- Unless stated otherwise, every table has `id uuid PK`.
- **Universal audit columns (UAC)** apply to every one of the 86 tables without exception: `created_at timestamptz NOT NULL DEFAULT now()`, `updated_at timestamptz NOT NULL DEFAULT now()`, `created_by uuid NULL FK users`, `updated_by uuid NULL FK users`, `deleted_at timestamptz NULL`, `version integer NOT NULL DEFAULT 1 CHECK (version > 0)`. Global/system actors may be null.
- **Mutable** rows update `updated_at`/`updated_by`, increment `version`, and may set `deleted_at` according to deletion policy. **Immutable/append-only** rows still contain all UAC columns but initialize `updated_at = created_at`, `updated_by = created_by`, `deleted_at = NULL`, and `version = 1`; constraints plus restricted privileges and a guard trigger reject `UPDATE` and `DELETE`. Retention purge or partition drop is available only to privileged maintenance. **Catalog** rows and **junction** rows also contain all UAC columns; catalog lifecycle and junction hard-delete policy do not waive any column.
- Every **WS** table has `workspace_id uuid NOT NULL FK workspaces`; every parent reference is a composite `(workspace_id, parent_id)` tenant-safe FK to a parent `UNIQUE(workspace_id,id)`. Every WS table has `UNIQUE(workspace_id,id)`, explicit application scoping, and RLS. **ORG** tables have `organization_id`; **GLOBAL** tables are unscoped catalogs/principals.
- `UQ(active: ...)` means a partial unique index with `WHERE deleted_at IS NULL`. Text checks reject blank strings where meaningful. All timestamps are UTC `timestamptz`; schedule wall times are the documented exception. Flexible JSON defaults to `'{}'::jsonb` or `'[]'::jsonb` and is shape/size validated.
- Deletion codes: **SD** soft-delete then retention purge; **HD** hard-delete; **IM** immutable/append-only; **RET** retained by policy then partition/drop or purge. FKs are `RESTRICT` unless a stated junction/ephemeral child uses `CASCADE`; actor FKs use `SET NULL`.

## Identity and tenancy (11)

### 1. `users`

Purpose: global internal principal/profile. Columns: `email citext NULL`, `display_name text NOT NULL`, `avatar_object_key text NULL`, `locale text NOT NULL DEFAULT 'en'`, `time_zone text NOT NULL DEFAULT 'UTC'`, `status text NOT NULL DEFAULT 'active' CHECK (active|disabled|anonymized)`, `last_seen_at timestamptz NULL`, UAC (mutable). Keys: PK; UQ(active: `email`) when non-null. Tenancy: GLOBAL. Deletion: SD; anonymize before purge, identity references retained.

### 2. `external_identities`

Purpose: OIDC subject mapping only. Columns: `user_id uuid NOT NULL FK users`, `issuer text NOT NULL`, `subject text NOT NULL`, `provider_code text NOT NULL CHECK nonblank`, `email_at_link citext NULL`, `claims_fingerprint bytea NULL`, `linked_at timestamptz NOT NULL DEFAULT now()`, UAC (mutable). UQ: permanent `(issuer,subject)` and active `(user_id,issuer)`. Tenancy: GLOBAL. Deletion: SD after unlink; no token/claims payload.

### 3. `user_sessions`

Purpose: revocable session/refresh metadata, never bearer tokens. Columns: `user_id uuid NOT NULL FK users`, `session_hash bytea NOT NULL`, `provider_session_id_hash bytea NULL`, `issued_at/expires_at timestamptz NOT NULL`, `last_used_at/revoked_at timestamptz NULL`, `revocation_reason text NULL`, `ip_hash bytea NULL`, `user_agent_hash bytea NULL`, UAC (immutable). UQ: `session_hash`; checks `expires_at>issued_at`. Tenancy: GLOBAL. Deletion: RET 90 days after expiry/revoke.

### 4. `organizations`

Purpose: commercial customer boundary. Columns: `name text NOT NULL`, `slug citext NOT NULL`, `status text NOT NULL DEFAULT 'active' CHECK (trial|active|suspended|closed)`, `billing_email citext NULL`, `default_time_zone text NOT NULL DEFAULT 'UTC'`, `data_region text NULL`, UAC (mutable). UQ(active: `slug`). Tenancy: GLOBAL commercial root. Deletion: SD, legal/billing hold aware.

### 5. `organization_memberships`

Purpose: organization-level commercial/admin access. Columns: `organization_id uuid NOT NULL FK organizations`, `user_id uuid NOT NULL FK users`, `role text NOT NULL CHECK (owner|billing_admin|admin|member)`, `status text NOT NULL DEFAULT 'active' CHECK (invited|active|suspended)`, `invited_at/accepted_at timestamptz NULL`, UAC (mutable). UQ(active: `organization_id,user_id`). Tenancy: ORG. Deletion: SD.

### 6. `workspaces`

Purpose: operational tenant. Columns: `organization_id uuid NOT NULL FK organizations`, `name text NOT NULL`, `slug citext NOT NULL`, `status text NOT NULL DEFAULT 'active' CHECK (provisioning|active|suspended|closing|closed)`, `time_zone text NOT NULL DEFAULT 'UTC'`, `retention_policy_days integer NULL CHECK (>0)`, UAC (mutable). UQ(active: `organization_id,slug`), `UNIQUE(id,organization_id)`. Tenancy: ORG root; RLS context source. Deletion: SD followed by controlled tenant purge.

### 7. `workspace_memberships`

Purpose: workspace user access. Columns: `workspace_id`, `user_id uuid NOT NULL FK users`, `status text NOT NULL DEFAULT 'active' CHECK (invited|active|suspended)`, `invited_by uuid NULL FK users`, `invited_at/accepted_at timestamptz NULL`, UAC (mutable). UQ(active: `workspace_id,user_id`). Tenancy: WS. Deletion: SD.

### 8. `roles`

Purpose: system role templates and workspace custom roles. Columns: `workspace_id uuid NULL FK workspaces`, `code citext NOT NULL`, `name text NOT NULL`, `description text NULL`, `is_system boolean NOT NULL DEFAULT false`, UAC (mutable). UQ(active global: `code` where workspace null); UQ(active WS: `workspace_id,code`). Check system roles have null workspace. Tenancy: GLOBAL or WS; WS rows RLS. Deletion: system HD prohibited; custom SD.

### 9. `permissions`

Purpose: global stable permission-code catalog. Columns: `code citext NOT NULL`, `module text NOT NULL`, `description text NOT NULL`, `risk_level text NOT NULL CHECK (normal|sensitive|destructive)`, UAC (catalog). UQ `code`. Tenancy: GLOBAL. Deletion: HD only when unreferenced and retired by release.

### 10. `role_permissions`

Purpose: permission grants. Columns: `role_id uuid NOT NULL FK roles`, `permission_id uuid NOT NULL FK permissions`, `workspace_id uuid NULL` (copied for custom-role RLS), UAC (junction). PK/UQ `(role_id,permission_id)`; check workspace matches role scope. Tenancy: GLOBAL or WS. Deletion: HD/CASCADE with role.

### 11. `membership_roles`

Purpose: assign roles to workspace memberships. Columns: `workspace_id`, `membership_id uuid NOT NULL FK workspace_memberships`, `role_id uuid NOT NULL FK roles`, UAC (junction). PK/UQ `(workspace_id,membership_id,role_id)`; check role is system or same workspace. Tenancy: WS. Deletion: HD/CASCADE.

## Projects, content, taxonomy, collaboration, and storage (24)

### 12. `projects`

Purpose: campaign/project grouping. Columns: `workspace_id`, `name text NOT NULL`, `slug citext NOT NULL`, `description text NULL`, `status text NOT NULL DEFAULT 'active' CHECK (active|archived)`, `owner_id uuid NULL FK users`, `starts_at/ends_at timestamptz NULL`, UAC (mutable). UQ(active: `workspace_id,slug`); check end after start. Tenancy: WS. Deletion: SD.

### 13. `folders`

Purpose: content hierarchy. Columns: `workspace_id`, `parent_folder_id uuid NULL FK folders`, `name text NOT NULL`, `path_cache text NULL`, UAC (mutable). UQ(active: `workspace_id,parent_folder_id,name`, with root null-safe form); check parent != id. Tenancy: WS. Deletion: SD; children explicitly moved/archived.

### 14. `collections`

Purpose: curated content sets. Columns: `workspace_id`, `name text NOT NULL`, `description text NULL`, `visibility text NOT NULL DEFAULT 'workspace' CHECK (private|workspace)`, `owner_id uuid NULL FK users`, UAC (mutable). UQ(active: `workspace_id,name`). Tenancy: WS. Deletion: SD.

### 15. `collection_items`

Purpose: ordered collection membership. Columns: `workspace_id`, `collection_id uuid NOT NULL FK collections`, `asset_id uuid NOT NULL FK content_assets`, `position integer NOT NULL DEFAULT 0 CHECK (>=0)`, UAC (junction). UQ `(workspace_id,collection_id,asset_id)` and `(workspace_id,collection_id,position)`. Tenancy: WS. Deletion: HD/CASCADE from collection.

### 16. `tags`

Purpose: workspace folksonomy. Columns: `workspace_id`, `name citext NOT NULL`, `color text NULL`, UAC (mutable). UQ(active: `workspace_id,name`). Tenancy: WS. Deletion: SD.

### 17. `asset_tags`

Purpose: asset/tag bridge. Columns: `workspace_id`, `asset_id uuid NOT NULL FK content_assets`, `tag_id uuid NOT NULL FK tags`, UAC (junction). UQ `(workspace_id,asset_id,tag_id)`. Tenancy: WS. Deletion: HD/CASCADE from asset.

### 18. `categories`

Purpose: controlled hierarchical taxonomy. Columns: `workspace_id`, `parent_category_id uuid NULL FK categories`, `name text NOT NULL`, `slug citext NOT NULL`, `description text NULL`, UAC (mutable). UQ(active: `workspace_id,slug`); check parent != id. Tenancy: WS. Deletion: SD.

### 19. `asset_categories`

Purpose: asset/category bridge. Columns: `workspace_id`, `asset_id uuid NOT NULL FK content_assets`, `category_id uuid NOT NULL FK categories`, `is_primary boolean NOT NULL DEFAULT false`, UAC (junction). UQ `(workspace_id,asset_id,category_id)`; partial UQ one primary per asset. Tenancy: WS. Deletion: HD.

### 20. `content_assets`

Purpose: master content aggregate/library row. Columns: `workspace_id`, `project_id/folder_id uuid NULL`, `asset_type text NOT NULL CHECK (article|video|poster|thumbnail)`, `title text NOT NULL`, `summary text NULL`, `lifecycle_status text NOT NULL DEFAULT 'draft' CHECK (draft|active|archived)`, `owner_id uuid NULL FK users`, `is_favorite boolean NOT NULL DEFAULT false`, `search_document tsvector NULL`, UAC (mutable). UQ `(workspace_id,id)`; optional active project/title index, not uniqueness. Tenancy: WS. Deletion: SD.

### 21. `articles`

Purpose: article-specific current metadata. Columns: `workspace_id`, `asset_id uuid PK/FK content_assets`, `source_kind text NOT NULL CHECK (compose|paste|import|upload)`, `canonical_url text NULL`, `language_code text NOT NULL DEFAULT 'en'`, `word_count integer NOT NULL DEFAULT 0 CHECK (>=0)`, `reading_minutes integer NOT NULL DEFAULT 0 CHECK (>=0)`, UAC (mutable). UQ `asset_id`; check asset type article. Tenancy: WS. Deletion: SD with asset.

### 22. `videos`

Purpose: video-specific metadata. Columns: `workspace_id`, `asset_id uuid PK/FK`, `duration_ms bigint NULL CHECK (>=0)`, `width/height integer NULL CHECK (>0)`, `frame_rate numeric(8,3) NULL CHECK (>0)`, `transcript_status text NOT NULL DEFAULT 'none' CHECK (none|pending|ready|failed)`, `caption_language text NULL`, UAC (mutable). Tenancy: WS. Deletion: SD with asset.

### 23. `posters`

Purpose: poster/image-specific metadata. Columns: `workspace_id`, `asset_id uuid PK/FK`, `width/height integer NULL CHECK (>0)`, `aspect_ratio numeric(12,6) NULL CHECK (>0)`, `alt_text text NULL`, `crop_metadata jsonb NOT NULL DEFAULT '{}'`, UAC (mutable). Tenancy: WS. Deletion: SD with asset.

### 24. `thumbnails`

Purpose: thumbnail-specific metadata. Columns: `workspace_id`, `asset_id uuid PK/FK`, `width/height integer NULL CHECK (>0)`, `aspect_ratio numeric(12,6) NULL CHECK (>0)`, `alt_text text NULL`, `source_time_ms bigint NULL CHECK (>=0)`, UAC (mutable). Tenancy: WS. Deletion: SD with asset.

### 25. `storage_objects`

Purpose: private blob metadata. Columns: `workspace_id`, `object_key text NOT NULL`, `storage_provider text NOT NULL DEFAULT 'azure_blob'`, `container_name text NOT NULL`, `mime_type text NOT NULL`, `byte_size bigint NOT NULL CHECK (>=0)`, `checksum_sha256 bytea NOT NULL`, `scan_status text NOT NULL DEFAULT 'pending' CHECK (pending|clean|infected|failed)`, `scan_completed_at timestamptz NULL`, `encryption_key_ref text NULL`, `retention_until timestamptz NULL`, UAC (mutable). UQ active `(workspace_id,object_key)` and `(workspace_id,checksum_sha256,byte_size)` optional dedupe. Tenancy: WS. Deletion: SD then asynchronous blob purge.

### 26. `asset_storage_objects`

Purpose: attach blobs/renditions to assets. Columns: `workspace_id`, `asset_id uuid NOT NULL`, `storage_object_id uuid NOT NULL`, `purpose text NOT NULL CHECK (source|rendition|poster|thumbnail|transcript|caption|attachment)`, `variant_key text NOT NULL DEFAULT 'original'`, `position integer NOT NULL DEFAULT 0`, UAC (junction). UQ `(workspace_id,asset_id,purpose,variant_key,position)`. Tenancy: WS. Deletion: HD; does not itself delete blob.

### 27. `content_drafts`

Purpose: current mutable autosave/editor state. Columns: `workspace_id`, `asset_id uuid NOT NULL`, `base_version_id uuid NULL FK content_versions`, `body_text text NULL`, `body_rich jsonb NULL`, `metadata jsonb NOT NULL DEFAULT '{}'`, `autosaved_at timestamptz NOT NULL DEFAULT now()`, UAC (mutable). UQ(active: `workspace_id,asset_id`). Tenancy: WS. Deletion: SD/purge after version creation or asset purge.

### 28. `content_versions`

Purpose: immutable content snapshots/provenance. Columns: `workspace_id`, `asset_id uuid NOT NULL`, `version_number integer NOT NULL CHECK (>0)`, `title text NOT NULL`, `body_text text NULL`, `body_rich jsonb NULL`, `metadata jsonb NOT NULL DEFAULT '{}'`, `origin text NOT NULL CHECK (user|ai|import|regeneration)`, `source_version_id uuid NULL FK self`, `content_hash bytea NOT NULL`, `change_summary text NULL`, UAC (immutable). UQ `(workspace_id,asset_id,version_number)` and `(workspace_id,asset_id,content_hash)`. Tenancy: WS. Deletion: IM until asset retention purge/legal hold release.

### 29. `comments`

Purpose: threaded review comments. Columns: `workspace_id`, `asset_id uuid NOT NULL`, `version_id uuid NULL`, `parent_comment_id uuid NULL`, `author_id uuid NULL FK users`, `body text NOT NULL`, `anchor jsonb NULL`, `resolved_at timestamptz NULL`, `resolved_by uuid NULL`, UAC (mutable). Check body nonblank, parent same asset. Tenancy: WS. Deletion: SD, retain tombstone if children exist.

### 30. `approval_requests`

Purpose: approval workflow instance. Columns: `workspace_id`, `asset_id/version_id uuid NOT NULL`, `status text NOT NULL DEFAULT 'pending' CHECK (pending|approved|rejected|changes_requested|cancelled)`, `requested_by uuid NULL`, `requested_at timestamptz NOT NULL DEFAULT now()`, `decided_at timestamptz NULL`, `decision_reason text NULL`, UAC (mutable). One partial UQ active pending request per version. Tenancy: WS. Deletion: SD only when cancelled; otherwise retained.

### 31. `approval_steps`

Purpose: ordered reviewer decisions. Columns: `workspace_id`, `approval_request_id uuid NOT NULL`, `step_order integer NOT NULL CHECK (>0)`, `reviewer_user_id uuid NULL`, `reviewer_role_id uuid NULL`, `status text NOT NULL DEFAULT 'pending' CHECK (pending|approved|rejected|changes_requested|skipped)`, `decided_at timestamptz NULL`, `note text NULL`, UAC (mutable). UQ active `(workspace_id,approval_request_id,step_order)`; exactly one reviewer selector. Tenancy: WS. Deletion: SD with request.

### 32. `saved_views`

Purpose: persisted library/analytics filters. Columns: `workspace_id`, `owner_id uuid NOT NULL FK users`, `name text NOT NULL`, `view_type text NOT NULL CHECK (content|calendar|analytics|activity)`, `filter_spec jsonb NOT NULL`, `sort_spec jsonb NOT NULL DEFAULT '[]'`, `is_shared boolean NOT NULL DEFAULT false`, UAC (mutable). UQ(active: `workspace_id,owner_id,view_type,name`). Tenancy: WS. Deletion: SD.

### 33. `brand_profiles`

Purpose: brand voice and defaults. Columns: `workspace_id`, `name text NOT NULL`, `description text NULL`, `voice_guidelines text NULL`, `audience text NULL`, `default_language text NOT NULL DEFAULT 'en'`, `style_settings jsonb NOT NULL DEFAULT '{}'`, `is_default boolean NOT NULL DEFAULT false`, UAC (mutable). UQ active name; partial UQ one default/workspace. Tenancy: WS. Deletion: SD.

### 34. `project_members`

Purpose: project-level responsibility. Columns: `workspace_id`, `project_id uuid NOT NULL`, `user_id uuid NOT NULL`, `project_role text NOT NULL CHECK (owner|editor|reviewer|viewer)`, UAC (junction). UQ `(workspace_id,project_id,user_id)`. Tenancy: WS. Deletion: HD.

### 35. `content_relations`

Purpose: typed links among assets. Columns: `workspace_id`, `source_asset_id/target_asset_id uuid NOT NULL`, `relation_type text NOT NULL CHECK (thumbnail_for|poster_for|derived_from|translation_of|related_to)`, UAC (junction). UQ `(workspace_id,source_asset_id,target_asset_id,relation_type)`; check source != target. Tenancy: WS. Deletion: HD.

## AI generation (8)

### 36. `ai_providers`

Purpose: extensible provider catalog. Columns: `code citext NOT NULL`, `name text NOT NULL`, `status text NOT NULL DEFAULT 'enabled' CHECK (enabled|disabled|degraded)`, `capabilities jsonb NOT NULL DEFAULT '{}'`, `secret_config_ref text NULL`, UAC (catalog). UQ `code`. Tenancy: GLOBAL. Deletion: deactivate, no delete while referenced.

### 37. `ai_models`

Purpose: provider model catalog. Columns: `provider_id uuid NOT NULL FK ai_providers`, `model_code text NOT NULL`, `display_name text NOT NULL`, `capabilities jsonb NOT NULL`, `context_window integer NULL CHECK (>0)`, `input_cost_per_million numeric(20,8) NULL CHECK (>=0)`, `output_cost_per_million numeric(20,8) NULL CHECK (>=0)`, `currency char(3) NULL`, `status text NOT NULL CHECK (enabled|disabled|deprecated)`, UAC (catalog). UQ `(provider_id,model_code)`. GLOBAL. Retain deprecated rows.

### 38. `ai_prompt_templates`

Purpose: versioned workspace prompt policy. Columns: `workspace_id`, `name text NOT NULL`, `purpose text NOT NULL`, `template_text text NOT NULL`, `template_version integer NOT NULL CHECK (>0)`, `input_schema jsonb NOT NULL DEFAULT '{}'`, `is_active boolean NOT NULL DEFAULT true`, UAC (mutable). UQ(active: `workspace_id,name,template_version`). Tenancy: WS. Deletion: SD; referenced versions retained.

### 39. `ai_generation_requests`

Purpose: generation aggregate/request state. Columns: `workspace_id`, `asset_id/source_version_id uuid NOT NULL`, `model_id uuid NOT NULL FK ai_models`, `prompt_template_id uuid NULL`, `brand_profile_id uuid NULL`, `status text NOT NULL DEFAULT 'queued' CHECK (queued|running|succeeded|failed|cancelled)`, `scope text NOT NULL CHECK (whole|selection|headline|cta|hashtags|tone|platform_variant)`, `parameters jsonb NOT NULL DEFAULT '{}'`, `provider_request_id text NULL`, `idempotency_key text NOT NULL`, `started_at/completed_at timestamptz NULL`, `failure_code/text NULL`, UAC (mutable). UQ `(workspace_id,idempotency_key)`. Tenancy: WS. Deletion: SD after retention.

### 40. `ai_generation_outputs`

Purpose: immutable generated candidates. Columns: `workspace_id`, `generation_request_id uuid NOT NULL`, `sequence_no integer NOT NULL CHECK (>0)`, `platform_id uuid NULL FK social_platforms`, `output_text text NOT NULL`, `output_metadata jsonb NOT NULL DEFAULT '{}'`, `safety_status text NOT NULL CHECK (unchecked|passed|flagged|blocked)`, `content_hash bytea NOT NULL`, `materialized_version_id uuid NULL`, UAC (immutable). UQ `(workspace_id,generation_request_id,sequence_no)`. Tenancy: WS. Deletion: RET with generation.

### 41. `ai_usage_records`

Purpose: normalized provider usage/cost evidence. Columns: `workspace_id`, `generation_request_id uuid NOT NULL`, `provider_id/model_id uuid NOT NULL`, `input_tokens/output_tokens/total_tokens bigint NOT NULL DEFAULT 0 CHECK (>=0)`, `provider_units numeric(20,6) NULL CHECK (>=0)`, `cost_amount numeric(20,8) NOT NULL DEFAULT 0 CHECK (>=0)`, `currency char(3) NOT NULL`, `provider_payload jsonb NULL` (redacted fragment), UAC (immutable). UQ `(workspace_id,generation_request_id,provider_id,model_id)`. Tenancy: WS. Deletion: RET billing policy.

### 42. `ai_suggestions`

Purpose: explainable AI/editor recommendations. Columns: `workspace_id`, `asset_id/version_id uuid NOT NULL`, `generation_request_id uuid NULL`, `category text NOT NULL CHECK (grammar|seo|engagement|readability|timing|warning)`, `title/description text NOT NULL`, `proposed_change jsonb NULL`, `status text NOT NULL DEFAULT 'open' CHECK (open|accepted|dismissed|expired)`, UAC (mutable). Tenancy: WS. Deletion: SD/RET with content.

### 43. `ai_suggestion_actions`

Purpose: immutable suggestion decision history. Columns: `workspace_id`, `suggestion_id uuid NOT NULL`, `action text NOT NULL CHECK (accepted|dismissed|reopened|applied)`, `actor_id uuid NULL`, `reason text NULL`, UAC (immutable). Tenancy: WS. Deletion: RET.

## Social connections (7)

### 44. `social_platforms`

Purpose: extensible publishing platform catalog. Columns: `code citext NOT NULL`, `name text NOT NULL`, `status text NOT NULL CHECK (enabled|disabled|coming_soon)`, `api_version text NULL`, `capability_metadata jsonb NOT NULL DEFAULT '{}'`, UAC (catalog). UQ `code`. GLOBAL. Never delete referenced rows.

### 45. `social_platform_capabilities`

Purpose: versioned capability/limit records. Columns: `platform_id uuid NOT NULL`, `capability_code citext NOT NULL`, `supported boolean NOT NULL`, `limit_value numeric(20,6) NULL`, `unit text NULL`, `metadata jsonb NOT NULL DEFAULT '{}'`, `effective_from timestamptz NOT NULL`, `effective_to timestamptz NULL`, UAC (immutable). UQ `(platform_id,capability_code,effective_from)`; valid interval check. GLOBAL. Retain history.

### 46. `social_content_templates`

Purpose: platform content rendering templates. Columns: `platform_id uuid NOT NULL`, `workspace_id uuid NULL`, `name text NOT NULL`, `template_version integer NOT NULL`, `body_template text NOT NULL`, `constraints jsonb NOT NULL DEFAULT '{}'`, `is_active boolean NOT NULL DEFAULT true`, UAC (mutable). UQ active by scope/platform/name/version. GLOBAL or WS; WS RLS. Deletion: SD.

### 47. `social_accounts`

Purpose: connected external account identity/health. Columns: `workspace_id`, `platform_id uuid NOT NULL`, `external_account_id text NOT NULL`, `account_name/display_name text NOT NULL`, `username text NULL`, `account_type text NULL`, `connection_status text NOT NULL CHECK (connected|disconnected)`, `health_status text NOT NULL CHECK (healthy|warning|error|needs_reauth)`, `publishing_enabled boolean NOT NULL DEFAULT true`, `default_audience text NULL`, `time_zone text NOT NULL DEFAULT 'UTC'`, `followers_count bigint NULL CHECK (>=0)`, `connected_at/last_sync_at timestamptz NULL`, UAC (mutable). UQ active `(workspace_id,platform_id,external_account_id)`. WS. SD; revoke token before purge.

### 48. `oauth_token_vaults`

Purpose: encrypted OAuth secret metadata. Columns: `workspace_id`, `social_account_id uuid NOT NULL`, `ciphertext bytea NULL`, `managed_secret_ref text NULL`, `key_id/key_version text NOT NULL`, `token_fingerprint bytea NOT NULL`, `scopes_hash bytea NULL`, `expires_at/rotated_at/revoked_at timestamptz NULL`, `status text NOT NULL CHECK (active|expiring_soon|expired|renew_required|revoked)`, UAC (mutable). UQ active social account; exactly one ciphertext/reference; no plaintext. WS. Cryptographic purge after revoke + 30 days.

### 49. `social_account_permissions`

Purpose: granted platform scopes. Columns: `workspace_id`, `social_account_id uuid NOT NULL`, `permission_code citext NOT NULL`, `granted_at timestamptz NOT NULL`, `revoked_at timestamptz NULL`, UAC (junction). UQ `(workspace_id,social_account_id,permission_code)`. WS. RET current connection + 90 days.

### 50. `social_account_settings`

Purpose: account publishing defaults. Columns: `workspace_id`, `social_account_id uuid NOT NULL`, `visibility text NULL`, `hashtag_strategy text NULL`, `auto_publish/ai_optimization/auto_schedule/url_tracking boolean NOT NULL DEFAULT false`, `provider_defaults jsonb NOT NULL DEFAULT '{}'`, UAC (mutable). UQ active social account. WS. SD with account.

## Publishing and scheduling (8)

### 51. `publications`

Purpose: publish aggregate for approved content. Columns: `workspace_id`, `asset_id/version_id uuid NOT NULL`, `approval_request_id uuid NULL`, `status text NOT NULL DEFAULT 'draft' CHECK (draft|ready|in_progress|completed|partially_failed|cancelled)`, `title text NOT NULL`, UAC (mutable). Check version belongs asset. UQ active optional `(workspace_id,version_id)` where not cancelled. WS. SD only draft/cancelled; retain completed.

### 52. `publication_targets`

Purpose: one account/platform rendition. Columns: `workspace_id`, `publication_id uuid NOT NULL`, `social_account_id/platform_id uuid NOT NULL`, `content_version_id uuid NOT NULL`, `generation_output_id uuid NULL`, `approval_state text NOT NULL CHECK (pending|approved|rejected|changes_requested|cancelled)`, `external_post_id/url text NULL`, `published_at timestamptz NULL`, UAC (mutable). UQ active `(workspace_id,publication_id,social_account_id)`. WS. SD only before publish; published retained.

### 53. `publication_schedules`

Purpose: authoritative requested and resolved publish time. Columns: `workspace_id`, `publication_target_id uuid NOT NULL`, `requested_local_at timestamp NOT NULL`, `time_zone text NOT NULL`, `fold smallint NULL CHECK (0|1)`, `ambiguity_policy text NOT NULL DEFAULT 'reject' CHECK (reject|earlier|later)`, `scheduled_for timestamptz NOT NULL`, `state text NOT NULL DEFAULT 'draft' CHECK (draft|scheduled|paused|dispatched|completed|cancelled|failed)`, `priority text NOT NULL DEFAULT 'normal' CHECK (low|normal|high)`, `queue_order integer NOT NULL DEFAULT 0 CHECK (>=0)`, `dispatched_at timestamptz NULL`, UAC (mutable). UQ active target where state in scheduled/paused/dispatched. WS. SD draft/cancelled; retain terminal history window.

### 54. `publishing_jobs`

Purpose: durable publish execution state. Columns: `workspace_id`, `schedule_id/target_id uuid NOT NULL`, `state text NOT NULL DEFAULT 'queued' CHECK (queued|leased|running|retry_wait|succeeded|failed|dead_lettered|cancelled)`, `idempotency_key text NOT NULL`, `priority smallint NOT NULL DEFAULT 0`, `available_at timestamptz NOT NULL DEFAULT now()`, `attempt_count integer NOT NULL DEFAULT 0`, `max_attempts integer NOT NULL DEFAULT 5 CHECK (>0)`, `last_error_code/text NULL`, `completed_at timestamptz NULL`, UAC (mutable). UQ `(workspace_id,idempotency_key)`. WS. RET 180 days after terminal.

### 55. `publishing_attempts`

Purpose: immutable provider attempt history. Columns: `workspace_id`, `publishing_job_id uuid NOT NULL`, `attempt_no integer NOT NULL CHECK (>0)`, `started_at/finished_at timestamptz NOT NULL`, `outcome text NOT NULL CHECK (succeeded|transient_failure|permanent_failure|timeout|cancelled)`, `provider_request_id text NULL`, `http_status integer NULL CHECK (100..599)`, `error_code/message text NULL`, `response_fragment jsonb NULL` redacted, UAC (immutable). UQ `(workspace_id,publishing_job_id,attempt_no)`. WS. RET/partition 180 days+.

### 56. `publication_status_history`

Purpose: append-only target/schedule status timeline. Columns: `workspace_id`, `publication_target_id uuid NOT NULL`, `schedule_id/job_id uuid NULL`, `state_type text NOT NULL CHECK (approval|schedule|job|provider)`, `from_state/to_state text NULL/NOT NULL`, `reason_code/text NULL`, `occurred_at timestamptz NOT NULL DEFAULT now()`, UAC (immutable). WS. RET/partition.

### 57. `job_leases`

Purpose: short worker claims/heartbeats. Columns: `workspace_id`, `publishing_job_id uuid NOT NULL`, `lease_owner text NOT NULL`, `lease_token uuid NOT NULL`, `leased_until/heartbeat_at timestamptz NOT NULL`, `acquired_at timestamptz NOT NULL DEFAULT now()`, UAC (immutable). UQ active enforced as one current row/job by service/advisory lock; UQ `lease_token`. WS. HD promptly after terminal; expired rows 7-day retention.

### 58. `dead_letters`

Purpose: terminal failed work and controlled replay. Columns: `workspace_id`, `source_type text NOT NULL CHECK (publishing_job|notification|outbox|webhook|background_job)`, `source_id uuid NOT NULL`, `reason_code/message text NOT NULL`, `payload jsonb NOT NULL` redacted, `failed_at timestamptz NOT NULL`, `replay_state text NOT NULL DEFAULT 'pending' CHECK (pending|replayed|discarded)`, `replayed_at timestamptz NULL`, UAC (mutable). UQ active `(workspace_id,source_type,source_id)`. WS. RET 180 days after resolution.

## Notifications (5)

### 59. `notification_types`

Purpose: extensible event/notification catalog. Columns: `code citext NOT NULL`, `name/description text NOT NULL`, `category text NOT NULL CHECK (transactional|product|security)`, `default_channels text[] NOT NULL DEFAULT '{}'`, UAC (catalog). UQ `code`. GLOBAL. Retire, do not delete referenced rows.

### 60. `notification_preferences`

Purpose: recipient channel preferences. Columns: `workspace_id`, `user_id uuid NOT NULL`, `notification_type_id uuid NOT NULL`, `channel text NOT NULL CHECK (in_app|email|webhook)`, `enabled boolean NOT NULL DEFAULT true`, `quiet_hours_start/end time NULL`, `time_zone text NOT NULL DEFAULT 'UTC'`, UAC (mutable). UQ active `(workspace_id,user_id,notification_type_id,channel)`. WS. SD/reset to defaults.

### 61. `notifications`

Purpose: user-visible notification instance. Columns: `workspace_id`, `notification_type_id uuid NOT NULL`, `recipient_user_id uuid NOT NULL`, `title/body text NOT NULL`, `severity text NOT NULL CHECK (info|success|warning|error)`, `resource_type/id text/uuid NULL`, `dedupe_key text NOT NULL`, `read_at/archived_at timestamptz NULL`, `expires_at timestamptz NULL`, UAC (mutable). UQ active `(workspace_id,recipient_user_id,dedupe_key)`. WS. SD/RET 180 days.

### 62. `notification_deliveries`

Purpose: per-channel delivery attempts/status. Columns: `workspace_id`, `notification_id uuid NOT NULL`, `recipient_user_id uuid NOT NULL`, `channel text NOT NULL CHECK (in_app|email|webhook)`, `status text NOT NULL CHECK (pending|sent|delivered|failed|suppressed)`, `attempt_count integer NOT NULL DEFAULT 0`, `provider_reference text NULL`, `last_attempt_at/delivered_at timestamptz NULL`, `error_code text NULL`, UAC (mutable). UQ active `(workspace_id,notification_id,recipient_user_id,channel)`. WS. RET/partition.

### 63. `notification_templates`

Purpose: localized channel templates. Columns: `notification_type_id uuid NOT NULL`, `workspace_id uuid NULL`, `channel text NOT NULL`, `locale text NOT NULL DEFAULT 'en'`, `template_version integer NOT NULL`, `subject_template text NULL`, `body_template text NOT NULL`, `is_active boolean NOT NULL DEFAULT true`, UAC (mutable). UQ active by scope/type/channel/locale/version. GLOBAL or WS. SD.

## Settings and inheritance (2)

### 64. `setting_definitions`

Purpose: typed setting registry/defaults. Columns: `key citext NOT NULL`, `value_type text NOT NULL CHECK (boolean|integer|decimal|string|string_list|object)`, `allowed_scopes text[] NOT NULL`, `default_value jsonb NOT NULL`, `validation_schema jsonb NOT NULL DEFAULT '{}'`, `is_secret boolean NOT NULL DEFAULT false`, `description text NOT NULL`, UAC (catalog). UQ `key`; secret definitions may store only secret references. GLOBAL. Retire, no delete while used.

### 65. `settings`

Purpose: scoped overrides and inheritance. Columns: `workspace_id uuid NULL`, `organization_id/user_id/project_id/social_account_id uuid NULL`, `definition_id uuid NOT NULL`, `scope_type text NOT NULL CHECK (organization|workspace|user|project|social_account)`, `value jsonb NOT NULL`, UAC (mutable). Exactly one scope target; workspace direct for all WS scopes. UQ active `(definition_id,scope_type,scope target)`. ORG or WS; RLS for WS. SD means inherit.

## Analytics (5)

### 66. `metric_definitions`

Purpose: extensible metric semantics. Columns: `code citext NOT NULL`, `name/description text NOT NULL`, `unit text NOT NULL`, `aggregation text NOT NULL CHECK (sum|last|max|min|average|ratio)`, `value_kind text NOT NULL CHECK (integer|decimal|percentage|currency)`, `methodology_version integer NOT NULL DEFAULT 1`, `platform_id uuid NULL`, UAC (catalog). UQ `(code,methodology_version,platform_id)` null-safe. GLOBAL. Retain history.

### 67. `metric_observations`

Purpose: raw normalized time-series facts. Columns: `workspace_id`, `metric_definition_id uuid NOT NULL`, `social_account_id uuid NULL`, `publication_target_id/content_asset_id uuid NULL`, `observed_at timestamptz NOT NULL`, `bucket_start/end timestamptz NOT NULL`, `value numeric(30,10) NOT NULL`, `currency char(3) NULL`, `is_estimated boolean NOT NULL DEFAULT false`, `source_fingerprint bytea NOT NULL`, `provider_fragment jsonb NULL`, UAC (immutable). UQ `(workspace_id,metric_definition_id,source_fingerprint)`; bucket check. WS. RET/partition 13 months raw.

### 68. `analytics_snapshots`

Purpose: dashboard aggregate cache with methodology. Columns: `workspace_id`, `snapshot_type text NOT NULL CHECK (workspace_kpi|platform_comparison|growth_trend|publishing_frequency)`, `period_start/end timestamptz NOT NULL`, `time_zone text NOT NULL`, `dimensions jsonb NOT NULL`, `metrics jsonb NOT NULL`, `fresh_through timestamptz NOT NULL`, `methodology_version integer NOT NULL`, UAC (immutable). UQ `(workspace_id,snapshot_type,period_start,period_end,methodology_version,dimensions hash)`. WS. RET 25 months.

### 69. `content_performance_snapshots`

Purpose: ranked content performance projection. Columns: `workspace_id`, `content_asset_id/publication_target_id uuid NOT NULL`, `snapshot_at timestamptz NOT NULL`, `reach/engagements/clicks/conversions bigint NULL CHECK (>=0)`, `engagement_rate numeric(12,8) NULL CHECK (>=0)`, `metrics jsonb NOT NULL DEFAULT '{}'`, UAC (immutable). UQ `(workspace_id,publication_target_id,snapshot_at)`. WS. RET 25 months.

### 70. `social_account_snapshots`

Purpose: account health/follower history. Columns: `workspace_id`, `social_account_id uuid NOT NULL`, `snapshot_at timestamptz NOT NULL`, `followers_count bigint NULL CHECK (>=0)`, `connection_status/health_status text NOT NULL`, `metrics jsonb NOT NULL DEFAULT '{}'`, UAC (immutable). UQ `(workspace_id,social_account_id,snapshot_at)`. WS. RET 25 months.

## Usage, quota, subscription, and billing (8)

### 71. `usage_dimensions`

Purpose: extensible metered-resource catalog. Columns: `code citext NOT NULL`, `name text NOT NULL`, `unit text NOT NULL`, `aggregation text NOT NULL CHECK (sum|max|last)`, `billable boolean NOT NULL DEFAULT false`, UAC (catalog). UQ `code`. GLOBAL. Retire, no delete.

### 72. `usage_events`

Purpose: immutable metering facts. Columns: `workspace_id`, `organization_id uuid NOT NULL`, `usage_dimension_id uuid NOT NULL`, `quantity numeric(30,10) NOT NULL CHECK (>=0)`, `occurred_at timestamptz NOT NULL`, `source_type/id text/uuid NOT NULL`, `dedupe_key text NOT NULL`, `cost_amount numeric(20,8) NULL CHECK (>=0)`, `currency char(3) NULL`, `metadata jsonb NOT NULL DEFAULT '{}'`, UAC (immutable). UQ `(workspace_id,dedupe_key)`. WS plus ORG. RET/partition 7 years if invoiced, otherwise 25 months.

### 73. `quota_policies`

Purpose: plan/org/workspace quota limits. Columns: `organization_id uuid NOT NULL`, `workspace_id uuid NULL`, `usage_dimension_id uuid NOT NULL`, `period_kind text NOT NULL CHECK (day|month|billing_cycle|lifetime)`, `hard_limit numeric(30,10) NOT NULL CHECK (>=0)`, `soft_limit numeric(30,10) NULL CHECK (>=0 and <=hard)`, `effective_from/to timestamptz`, UAC (mutable). UQ active scope/dimension/effective_from. ORG or WS. SD after expiry.

### 74. `quota_periods`

Purpose: concurrency-safe quota counters/reservations. Columns: `organization_id uuid NOT NULL`, `workspace_id uuid NULL`, `usage_dimension_id uuid NOT NULL`, `period_start/end timestamptz NOT NULL`, `consumed_quantity/reserved_quantity numeric(30,10) NOT NULL DEFAULT 0 CHECK (>=0)`, `last_reconciled_at timestamptz NULL`, UAC (mutable). UQ active `(scope,dimension,period_start,period_end)`; period check. ORG or WS. RET 25 months.

### 75. `subscriptions`

Purpose: external subscription mirror. Columns: `organization_id uuid NOT NULL`, `provider_code text NOT NULL`, `external_subscription_id text NOT NULL`, `plan_code text NOT NULL`, `status text NOT NULL CHECK (trialing|active|past_due|paused|cancelled|ended)`, `currency char(3) NOT NULL`, `current_period_start/end timestamptz NULL`, `cancel_at/end_at timestamptz NULL`, UAC (mutable). UQ active `(provider_code,external_subscription_id)` and one current subscription/org. ORG. SD only after statutory retention.

### 76. `subscription_items`

Purpose: subscription meters/seats/features. Columns: `organization_id`, `subscription_id uuid NOT NULL`, `usage_dimension_id uuid NULL`, `external_item_id text NULL`, `price_code text NOT NULL`, `quantity numeric(20,6) NOT NULL CHECK (>=0)`, `unit_amount numeric(20,8) NULL CHECK (>=0)`, `currency char(3) NOT NULL`, UAC (mutable). UQ active `(subscription_id,price_code,usage_dimension_id)` null-safe. ORG. SD/retain with subscription.

### 77. `billing_customers`

Purpose: external billing customer reference; no payment instruments. Columns: `organization_id uuid NOT NULL`, `provider_code text NOT NULL`, `external_customer_id text NOT NULL`, `billing_email citext NULL`, `tax_region text NULL`, `status text NOT NULL CHECK (active|delinquent|closed)`, UAC (mutable). UQ active organization/provider and `(provider_code,external_customer_id)`. ORG. SD/RET 7 years.

### 78. `billing_events`

Purpose: immutable billing webhook/accounting evidence. Columns: `organization_id uuid NOT NULL`, `provider_code text NOT NULL`, `external_event_id text NOT NULL`, `event_type text NOT NULL`, `occurred_at/received_at timestamptz NOT NULL`, `amount numeric(20,8) NULL`, `currency char(3) NULL`, `payload_fragment jsonb NOT NULL` redacted, `payload_hash bytea NOT NULL`, UAC (immutable). UQ `(provider_code,external_event_id)`. ORG. IM/RET 7 years.

## Reliability, audit, and operations (8)

### 79. `activity_logs`

Purpose: ordinary user-facing recent-activity feed. Columns: `workspace_id`, `actor_id uuid NULL`, `activity_type text NOT NULL`, `resource_type/id text/uuid NULL`, `message text NOT NULL`, `metadata jsonb NOT NULL DEFAULT '{}'`, `occurred_at timestamptz NOT NULL DEFAULT now()`, `hidden_at timestamptz NULL`, UAC (mutable). WS. SD/RET 180 days; not compliance evidence.

### 80. `audit_logs`

Purpose: append-only security/material-change evidence. Columns: `workspace_id uuid NULL`, `organization_id uuid NULL`, `actor_user_id uuid NULL`, `actor_type text NOT NULL CHECK (user|service|system|provider)`, `action text NOT NULL`, `target_type text NOT NULL`, `target_id uuid NULL`, `outcome text NOT NULL CHECK (success|failure|denied)`, `source text NOT NULL`, `correlation_id uuid NULL`, `request_id text NULL`, `safe_diff jsonb NULL`, `ip_hash bytea NULL`, `occurred_at timestamptz NOT NULL DEFAULT now()`, UAC (immutable). At least one scope or explicit global event; no secrets/content. ORG/WS/global controlled policy. IM/partition 1–7 years.

### 81. `idempotency_keys`

Purpose: request deduplication/replay. Columns: `workspace_id`, `principal_id uuid NULL`, `key text NOT NULL`, `operation text NOT NULL`, `request_hash bytea NOT NULL`, `state text NOT NULL CHECK (processing|completed|failed)`, `response_status integer NULL`, `response_headers jsonb NULL`, `response_body_ref text NULL`, `locked_until/expires_at timestamptz NOT NULL`, UAC (mutable). UQ active `(workspace_id,principal_id,operation,key)` null-safe. WS. HD/RET 24–72 hours.

### 82. `outbox_events`

Purpose: transactionally persisted integration events. Columns: `workspace_id uuid NULL`, `organization_id uuid NULL`, `aggregate_type/id text/uuid NOT NULL`, `event_type text NOT NULL`, `event_version integer NOT NULL`, `payload jsonb NOT NULL` redacted/versioned, `headers jsonb NOT NULL DEFAULT '{}'`, `occurred_at/available_at timestamptz NOT NULL`, `published_at timestamptz NULL`, `attempt_count integer NOT NULL DEFAULT 0`, `last_error text NULL`, UAC (immutable). UQ `id`; scope required where tenant-owned. ORG/WS/global. RET/partition 30 days after publish.

### 83. `inbox_messages`

Purpose: consumer deduplication. Columns: `workspace_id uuid NULL`, `consumer_name text NOT NULL`, `message_id uuid NOT NULL`, `event_type text NOT NULL`, `received_at timestamptz NOT NULL`, `processed_at timestamptz NULL`, `outcome text NULL CHECK (processed|ignored|failed)`, `payload_hash bytea NOT NULL`, UAC (immutable). UQ `(consumer_name,message_id)`. Scope mirrors event. RET/partition 30–90 days.

### 84. `webhook_receipts`

Purpose: inbound provider callback dedupe/evidence. Columns: `workspace_id uuid NULL`, `provider_code text NOT NULL`, `external_event_id text NOT NULL`, `event_type text NOT NULL`, `signature_valid boolean NOT NULL`, `payload_hash bytea NOT NULL`, `payload_fragment jsonb NULL` redacted, `received_at timestamptz NOT NULL`, `processed_at timestamptz NULL`, `processing_status text NOT NULL CHECK (received|processed|ignored|failed)`, UAC (immutable). UQ `(provider_code,external_event_id)` or payload-hash fallback. ORG/WS resolved before processing; quarantined if unresolved. RET 90–365 days.

### 85. `background_jobs`

Purpose: durable non-publishing work (AI/media/notification/maintenance/export). Columns: `workspace_id uuid NULL`, `job_type text NOT NULL`, `queue_name text NOT NULL CHECK (ai|media|notification|maintenance)`, `state text NOT NULL CHECK (queued|leased|running|retry_wait|succeeded|failed|dead_lettered|cancelled)`, `resource_type/id text/uuid NULL`, `idempotency_key text NOT NULL`, `priority smallint NOT NULL DEFAULT 0`, `available_at timestamptz NOT NULL`, `attempt_count integer NOT NULL DEFAULT 0`, `max_attempts integer NOT NULL DEFAULT 5`, `lease_owner text NULL`, `leased_until/heartbeat_at/completed_at timestamptz NULL`, `error_code/message text NULL`, UAC (mutable). UQ active scope/type/key. WS/global maintenance. RET 90–180 days.

### 86. `data_exports`

Purpose: tenant export/erasure package tracking. Columns: `workspace_id`, `requested_by uuid NULL`, `export_type text NOT NULL CHECK (workspace_export|user_export|erasure_evidence)`, `state text NOT NULL CHECK (queued|running|ready|failed|expired|purged)`, `storage_object_id uuid NULL`, `requested_at/completed_at/expires_at/purged_at timestamptz NULL`, `checksum_sha256 bytea NULL`, `failure_code text NULL`, UAC (mutable). UQ active `(workspace_id,id)`; ready requires object/checksum/expiry. WS. SD metadata after package cryptographic/blob purge; retain erasure evidence without exported content.

## Count reconciliation

11 identity/tenancy + 24 content/storage + 8 AI + 7 social + 8 publishing + 5 notifications + 2 settings + 5 analytics + 8 usage/billing + 8 reliability/audit = **86 tables**.
