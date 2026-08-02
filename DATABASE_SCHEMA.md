# Cloud Content Hub AI — Database Schema

**Baseline:** PostgreSQL 17 · schema version 1.0 · 86 tables  
**Scope:** production physical/logical design for a commercial multi-tenant SaaS. This is design documentation, not executable DDL.

## 1. Architectural decisions

1. `organizations` are the commercial/customer and billing boundary. `workspaces` are the operational tenant and authorization boundary. An organization may own many workspaces.
2. Every workspace-owned row stores `workspace_id uuid NOT NULL` directly, including descendants where it is derivable. Parent tables expose `UNIQUE (workspace_id, id)` and children use composite tenant-safe foreign keys `(workspace_id, parent_id) REFERENCES parent(workspace_id, id)`.
3. Application commands, queries, and repositories must always receive and filter by explicit workspace scope; absent scope fails closed. PostgreSQL RLS is defense in depth, not a replacement. Transactions set a validated `app.workspace_id`; policies compare it to the row's `workspace_id`. Privileged maintenance roles are separate, audited, and never used by request traffic.
4. UUID primary keys use application-generated UUIDv7 where sortable identity is useful. All times are `timestamptz`, persisted in UTC. User-selected zones are IANA names stored as `text`.
5. No PostgreSQL ENUMs. Stable, workflow-owned states use lowercase text plus `CHECK`; extensible platforms, providers, models, metrics, and usage dimensions use catalog rows.
6. Every one of the 86 tables—business, operational, catalog, junction, immutable, and integration—carries `created_at timestamptz NOT NULL DEFAULT now()`, `updated_at timestamptz NOT NULL DEFAULT now()`, `created_by uuid NULL`, `updated_by uuid NULL`, `deleted_at timestamptz NULL`, and `version integer NOT NULL DEFAULT 1 CHECK (version > 0)`. There are no table-level exceptions. Global/system actor FKs may be null so bootstrap, automation, and privacy erasure do not fabricate users.
7. Optimistic updates require `WHERE id = ? AND workspace_id = ? AND version = ?`; successful mutable writes increment `version`. Database triggers may maintain `updated_at`, but not domain state.
8. Soft-delete uniqueness uses partial unique indexes with `WHERE deleted_at IS NULL`. Mutable business FKs default to `RESTRICT`; service-layer archival/restoration traverses aggregates explicitly. Immutable history uses retained identifiers/snapshots.
9. `jsonb` is limited to safe provider fragments, capability metadata, redacted diffs, settings values, and immutable event payloads. Query-critical fields remain typed columns. OAuth access/refresh secrets are encrypted outside PostgreSQL or stored only as ciphertext/key references; plaintext is prohibited.
10. Content lifecycle, approval state, schedule state, and job state are separate:
    - content: `draft | active | archived`
    - approval: `pending | approved | rejected | changes_requested | cancelled`
    - schedule: `draft | scheduled | paused | dispatched | completed | cancelled | failed`
    - publishing job: `queued | leased | running | retry_wait | succeeded | failed | dead_lettered | cancelled`

### Universal audit and immutability invariant

Mutable writes set `updated_at`, set nullable `updated_by`, and increment `version`; soft deletion sets `deleted_at`. Immutable/append-only rows initialize `updated_at = created_at`, `updated_by = created_by`, `deleted_at = NULL`, and `version = 1`. A check constraint validates that immutable shape, ordinary application roles receive no `UPDATE`/`DELETE`, and a guard trigger/policy rejects mutation even if privileges drift. Catalog rows retain all six columns even when lifecycle is represented by status/effective dates. Junction rows retain all six columns for their lifetime even when their permitted removal is a hard delete. Retention purge, physical hard delete of immutable data, and partition detach/drop run only through a separately credentialed, audited maintenance path after hold checks.

## 2. Module catalog (authoritative table inventory)

The names below are authoritative and total **86 tables**.

### Identity and tenancy (11)

`users`, `external_identities`, `user_sessions`, `organizations`, `organization_memberships`, `workspaces`, `workspace_memberships`, `roles`, `permissions`, `role_permissions`, `membership_roles`.

### Projects, content, taxonomy, collaboration, and storage (24)

`projects`, `folders`, `collections`, `collection_items`, `tags`, `asset_tags`, `categories`, `asset_categories`, `content_assets`, `articles`, `videos`, `posters`, `thumbnails`, `storage_objects`, `asset_storage_objects`, `content_drafts`, `content_versions`, `comments`, `approval_requests`, `approval_steps`, `saved_views`, `brand_profiles`, `project_members`, `content_relations`.

### AI generation (8)

`ai_providers`, `ai_models`, `ai_prompt_templates`, `ai_generation_requests`, `ai_generation_outputs`, `ai_usage_records`, `ai_suggestions`, `ai_suggestion_actions`.

### Social connections (7)

`social_platforms`, `social_platform_capabilities`, `social_content_templates`, `social_accounts`, `oauth_token_vaults`, `social_account_permissions`, `social_account_settings`.

### Publishing and scheduling (8)

`publications`, `publication_targets`, `publication_schedules`, `publishing_jobs`, `publishing_attempts`, `publication_status_history`, `job_leases`, `dead_letters`.

### Notifications (5)

`notification_types`, `notification_preferences`, `notifications`, `notification_deliveries`, `notification_templates`.

### Settings and inheritance (2)

`setting_definitions`, `settings`.

### Analytics (5)

`metric_definitions`, `metric_observations`, `analytics_snapshots`, `content_performance_snapshots`, `social_account_snapshots`.

### Usage, quota, subscriptions, and billing (8)

`usage_dimensions`, `usage_events`, `quota_policies`, `quota_periods`, `subscriptions`, `subscription_items`, `billing_customers`, `billing_events`.

### Reliability, audit, and operations (8)

`activity_logs`, `audit_logs`, `idempotency_keys`, `outbox_events`, `inbox_messages`, `webhook_receipts`, `background_jobs`, `data_exports`.

## 3. Module-by-module schema

### Identity and tenancy

`users` is a global internal principal with profile and lifecycle only; external subjects live in `external_identities`. `user_sessions` stores revocation and hashed refresh-session metadata only—never bearer tokens. Organization and workspace memberships are separate because commercial access does not imply workspace access. `roles` may be system templates or workspace-defined; `permissions` is a global code catalog. Membership-role assignment is workspace-local.

### Content and storage

`content_assets` is the aggregate root and common library record. Exactly one subtype row in `articles`, `videos`, `posters`, or `thumbnails` must match `asset_type`; this cross-table invariant is enforced by the application plus a deferred constraint trigger if implemented. A poster, video, article, or thumbnail remains a first-class asset; relationships such as “thumbnail for video” use `content_relations`.

`content_drafts` stores mutable autosave/editor state; `content_versions` stores immutable snapshots and provenance while retaining the universal six audit columns in their fixed immutable state. Approved versions are referenced by publication targets, so later edits cannot change scheduled material. `storage_objects` contains tenant-prefixed object keys, MIME/checksum/scan metadata, never public URLs. `asset_storage_objects` names source, rendition, transcript, caption, poster, and thumbnail attachments and retains all six audit columns during its junction lifetime.

Folders have a tenant-safe self-FK; collections are many-to-many curated sets. Tags and categories are workspace-scoped. Comments may anchor to a version and support threads. Approval requests contain ordered approval steps.

### AI generation

Providers and models are row-extensible global catalogs. A request records source version, prompt template/version, model, parameters, safety state, provider request ID, and lifecycle. Outputs are immutable candidates and may materialize as content versions. Usage records preserve normalized input/output tokens, provider units, currency, and `numeric(20,8)` cost. Suggestions and actions keep explainable acceptance/dismissal history.

### Social connections

Platforms and capability rows preserve future platforms (`threads`, `hashnode`, `devto`, `tiktok`, `newsletter`) as disabled/catalog rows rather than code/schema changes. Social accounts are workspace-owned external account identities. Token vault rows contain encrypted ciphertext or managed-secret references, key version, expiry, and rotation metadata only. Permissions and defaults are relational where queried; flexible provider defaults may use constrained `jsonb`.

### Publishing and scheduling

`publications` binds a content asset to an immutable version. Each `publication_target` selects a platform/account and optional platform variant. `publication_schedules` stores requested wall time (`timestamp without time zone`), IANA zone, `fold smallint CHECK (fold IN (0,1))`, ambiguity policy (`reject|earlier|later`), and resolved UTC `scheduled_for timestamptz`. Nonexistent local times are rejected; ambiguous times require explicit fold/policy. Rescheduling recomputes and records resolved UTC.

The dispatcher claims due schedules briefly, then creates `publishing_jobs`. Job state is independent from schedule and content state. Attempts are immutable but still carry the universal six audit columns in fixed form. `job_leases` provides heartbeat recovery; `dead_letters` captures terminal redacted envelopes and replay state. Status history is append-only under mutation-denying controls, not by omitting columns.

### Notifications and settings

Notification type and template catalogs are extensible. Preferences are recipient/type/channel scoped; deliveries are deduplicated by notification, recipient, and channel. Settings use definitions plus scoped values (`organization`, `workspace`, `user`, `project`, `social_account`). Resolution order is specific-to-general, then definition default; the selected source is exposed to clients so inherited versus overridden values are visible.

### Analytics, usage, and billing

Metric definitions normalize cross-platform meaning and units. Raw observations are append-only, deduplicated by source/account/target/metric/bucket, and partition candidates; their universal audit columns remain fixed. Snapshots accelerate dashboards while retaining freshness and methodology. Usage events are immutable billable facts with the same six columns, quota periods hold reservation/consumption counters, and policies define limits. Billing tables are future-ready mirrors of an external billing authority; no card or bank data is stored. Money uses ISO-4217 `char(3)` and `numeric(20,8)` amounts; subscription quantities use `numeric(20,6)`.

### Reliability, audit, and operations

`idempotency_keys` stores request hash and replayable response metadata. Transactional outbox and consumer inbox provide at-least-once safety. Webhook receipts deduplicate external callbacks. Background jobs are durable operational work records; job-specific publish detail remains in publishing tables.

`activity_logs` are ordinary user-facing, mutable-retention feed entries and may be hidden/soft-deleted. `audit_logs` are append-only, security/compliance records with actor, action, target, outcome, source, correlation, and redacted safe diff. They include all six audit columns, initialized to the immutable shape, and cannot be edited or soft-deleted through ordinary roles. `data_exports` tracks tenant export/erasure packages and expiry.

## 4. Core invariants

- A workspace belongs to exactly one organization; workspace ownership never changes without a controlled migration.
- Workspace-owned references never use a bare parent ID; composite tenant-safe FKs prevent cross-workspace linkage even if application filters fail.
- Organization-scoped billing rows may reference workspaces only through validated ownership; commercial records are not duplicated per workspace.
- Active slugs/names are unique within their documented scope; deleted rows do not block reuse unless external identity semantics require permanent uniqueness.
- One active external identity exists per `(issuer, subject)`. One active social account exists per `(workspace_id, platform_id, external_account_id)`.
- One current draft exists per asset. Version numbers are unique per asset and immutable.
- Publication targets reference immutable `content_versions`; publication and scheduling never infer approval from content lifecycle.
- A scheduled target must have an approved version and an enabled, healthy account at dispatch; this is a transactional domain invariant.
- Provider callbacks, outbox deliveries, inbox consumption, webhooks, publishing attempts, and usage facts are duplicate-prone and therefore have explicit idempotency/deduplication keys.
- Encrypted secret columns must be ciphertext produced by an approved envelope-encryption service; logs, audit diffs, outbox payloads, and provider fragments must be redacted before persistence.

## 5. Relationship matrix

| Parent                | Child / bridge                                                         | Cardinality and rule                                    |
| --------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------- |
| organizations         | workspaces, organization_memberships, subscriptions, billing_customers | 1:N; organization is commercial boundary                |
| workspaces            | all workspace-owned tables                                             | 1:N; direct `workspace_id`, composite FKs, RLS          |
| users                 | memberships, comments, approvals, preferences                          | 1:N; user deletion anonymizes nullable actor references |
| workspace_memberships | membership_roles                                                       | M:N roles via assignment                                |
| projects              | content_assets, project_members                                        | 1:N and M:N users                                       |
| content_assets        | subtype, drafts, versions, tags, categories, comments                  | 1:1 subtype; otherwise 1:N/M:N                          |
| storage_objects       | asset_storage_objects                                                  | M:N attachment with purpose                             |
| content_versions      | approval_requests, generation requests, publication targets            | immutable source/approved artifact                      |
| ai_providers          | ai_models                                                              | 1:N extensible catalog                                  |
| social_platforms      | capabilities, templates, accounts                                      | 1:N                                                     |
| social_accounts       | token vault, permissions, targets, snapshots                           | 1:1 active vault; otherwise 1:N                         |
| publications          | targets                                                                | 1:N                                                     |
| publication_targets   | schedules, jobs, status history                                        | 1:N over lifecycle                                      |
| publishing_jobs       | attempts, leases, dead letters                                         | 1:N attempts; 0..1 active lease                         |
| notifications         | deliveries                                                             | 1:N per recipient/channel                               |
| metric_definitions    | observations and snapshots                                             | 1:N                                                     |
| usage_dimensions      | events, policies, periods, subscription items                          | shared extensible dimension                             |
| outbox_events         | inbox_messages (logical, cross-service)                                | delivery/consumption by event ID                        |

## 6. Data classification and retention

| Class                | Examples                                                      | Protection                                                         | Default retention                                |
| -------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------ |
| Restricted secrets   | OAuth ciphertext, key references                              | envelope encryption, no payload/log copies, tightly separated role | until revoke + 30 days, then cryptographic purge |
| Personal data        | user profile, external identity, account display data         | least privilege, tenant scope, export/erasure workflow             | account life + contractual/legal window          |
| Confidential content | drafts, versions, prompts, generated output, storage metadata | tenant RLS, encryption at rest, signed short-lived access          | tenant policy; purge after soft-delete grace     |
| Financial            | subscriptions, billing events, normalized costs               | organization scope, immutable evidence                             | 7 years or jurisdiction contract                 |
| Security audit       | `audit_logs`, session revocation, webhook evidence            | append-only, restricted readers, integrity monitoring              | 1–7 years by plan/policy                         |
| Operational          | jobs, attempts, inbox/outbox, activity                        | redaction and TTL partitions                                       | 30–180 days after terminal state                 |
| Analytics            | metric observations/snapshots                                 | pseudonymization/aggregation                                       | raw 13 months; aggregates 25 months by default   |

Legal hold overrides purge. Tenant-configurable retention may lengthen but not shorten statutory minima. Erasure replaces actor PII with tombstone identity while retaining required financial/audit evidence.

## 7. Partition and scale candidates

- Monthly range partitions: `audit_logs`, `activity_logs`, `metric_observations`, `usage_events`, `outbox_events`, `inbox_messages`, `webhook_receipts`, `publishing_attempts`, `publication_status_history`, `notification_deliveries`.
- Partition only after measured size/maintenance thresholds; keep a default partition and alert on unexpected routing.
- Prefer time range partitioning with tenant-prefixed local indexes. High-volume enterprise deployments may subpartition selected facts by hash of `workspace_id`, but should avoid one partition per tenant.
- BRIN indexes support append-correlated time scans; B-tree tenant/time indexes support product queries. Partition lifecycle is described in MIGRATION_STRATEGY.md.

## 8. PostgreSQL 17 and RLS baseline

Enable RLS and `FORCE ROW LEVEL SECURITY` on every workspace-owned table. Typical policy semantics are `workspace_id = current_setting('app.workspace_id', true)::uuid`; a missing or malformed setting yields no rows through a safe helper, never broad access. Organization billing policies use validated organization context separately. Connection pools must reset transaction-local settings. Owners/migration roles bypass only in controlled jobs.

Test every repository with cross-tenant negative cases, including guessed UUIDs, joins, soft-deleted rows, background jobs, and bulk operations. RLS is the second barrier; explicit application predicates and tenant-safe constraints remain mandatory.

## 9. Documentation map

- `TABLE_SPECIFICATIONS.md`: column, key, constraint, tenancy, audit, and retention specification for all 86 tables.
- `ERD.md`: bounded-context Mermaid diagrams and cross-module links.
- `INDEX_STRATEGY.md`: concrete index inventory and operating rules.
- `NAMING_CONVENTIONS.md`: identifiers, constraints, statuses, and migration naming.
- `MIGRATION_STRATEGY.md`: PostgreSQL 17 zero-downtime change process.
- `SOFT_DELETE_STRATEGY.md`: deletion classes, restore, uniqueness, cascade, and purge.
