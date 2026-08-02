# Soft Delete Strategy

Applies to the authoritative **86-table** design. Soft deletion is a business lifecycle tool, not a substitute for retention, erasure, or immutable evidence.

## Rules

- Every table in every classification below contains `created_at`, `updated_at`, `created_by`, `updated_by`, `deleted_at`, and `version`; classification changes permitted behavior, never physical column presence.
- Active means `deleted_at IS NULL`. Normal application reads always include this predicate in addition to explicit workspace scope; RLS does not hide deleted rows by itself unless a separate policy intentionally does so.
- A delete command updates `deleted_at`, `updated_at`, `updated_by`, and increments `version` under optimistic concurrency. It emits an outbox event and material audit event where required.
- Database `ON DELETE CASCADE` is limited to hard-deleted junction/ephemeral rows. Business aggregate deletion is an explicit, idempotent service workflow so storage, OAuth revocation, external posts, exports, billing holds, and legal holds are handled safely.
- Business-key reuse uses partial unique indexes `WHERE deleted_at IS NULL`. Referential tenant keys retain non-partial `UNIQUE(workspace_id,id)` so composite FKs remain valid.
- Queries that intentionally include deleted rows require a named administrative repository method, authorization, and audit.

## Classification by table

### Soft-delete business records

`users`, `external_identities`, `organizations`, `organization_memberships`, `workspaces`, `workspace_memberships`, custom `roles`, `projects`, `folders`, `collections`, `tags`, `categories`, `content_assets`, `articles`, `videos`, `posters`, `thumbnails`, `storage_objects`, `content_drafts`, `comments`, `approval_requests`, `approval_steps`, `saved_views`, `brand_profiles`, `ai_prompt_templates`, `ai_generation_requests`, `ai_suggestions`, `social_content_templates`, `social_accounts`, `oauth_token_vaults`, `social_account_settings`, `publications`, `publication_targets`, `publication_schedules`, `publishing_jobs`, `dead_letters`, `notification_preferences`, `notifications`, `notification_deliveries`, `notification_templates`, `settings`, `quota_policies`, `quota_periods`, `subscriptions`, `subscription_items`, `billing_customers`, `activity_logs`, `idempotency_keys`, `background_jobs`, `data_exports`.

Restrictions override the mechanism: published targets/publications, decided approvals, and billing records are retained rather than user-purgeable until their policy expires. System roles and catalogs cannot be soft-deleted through tenant APIs.

### Immutable or append-only

`user_sessions`, `content_versions`, `ai_generation_outputs`, `ai_usage_records`, `ai_suggestion_actions`, `social_platform_capabilities`, `publishing_attempts`, `publication_status_history`, `metric_observations`, `analytics_snapshots`, `content_performance_snapshots`, `social_account_snapshots`, `usage_events`, `billing_events`, `audit_logs`, `outbox_events`, `inbox_messages`, `webhook_receipts`.

These rows still have all six universal audit columns. At insert, `updated_at = created_at`, `updated_by = created_by`, `deleted_at = NULL`, and `version = 1`. An immutable-shape check, denied `UPDATE`/`DELETE` privileges, and a mutation-guard trigger/policy reject ordinary mutation. Corrections are new facts or compensating events. Retention-aware physical purge or partition detach/drop is allowed only through privileged, separately credentialed, audited maintenance after legal-hold checks.

### Catalogs: deactivate/retire, do not tenant-delete

`permissions`, `ai_providers`, `ai_models`, `social_platforms`, `notification_types`, `setting_definitions`, `metric_definitions`, `usage_dimensions`.

Every catalog row contains all six audit columns. Referenced rows remain forever or through the maximum evidence window; lifecycle is expressed with catalog status/effective dates rather than omitting `deleted_at`. Future platforms/providers remain rows.

### Hard-delete junctions and ephemeral claims

`role_permissions`, `membership_roles`, `collection_items`, `asset_tags`, `asset_categories`, `asset_storage_objects`, `project_members`, `content_relations`, `social_account_permissions`, `job_leases`.

Every junction and lease row contains all six audit columns during its lifetime. Permitted hard deletion is the business/operational event; material changes still produce audit/outbox evidence. Expired leases are deleted only by the authorized operational maintenance path. `job_leases` history is not evidence; attempts/status history is.

## Aggregate delete behavior

### Workspace closure

1. Mark workspace `closing`; block new writes and publishing.
2. Cancel schedules/jobs, revoke OAuth credentials, expire signed access, and pause integrations.
3. Produce requested export; evaluate legal, billing, security, and contractual holds.
4. Soft-delete mutable workspace rows in dependency-safe batches while retaining immutable evidence.
5. Delete blobs only after all attachment references and holds are clear.
6. Mark workspace `closed`; purge after grace period. Organization/billing evidence remains organization-scoped.

No database cascade performs these external effects.

### Content asset

- Soft-delete the asset, subtype, current draft, comments, mutable approvals, and mutable relations/attachments in one command workflow.
- Immutable versions, generation/usage records, published targets, attempts, and audit evidence remain until retention permits purge.
- Storage objects are reference-counted logically. An object is purgeable only when no active or retained attachment/export/history requires it.
- Existing external posts are not deleted by default. A separate explicit “delete from platform” command is capability-aware and audited.

### Social account

- Disable publishing immediately, cancel or block future targets, revoke provider access, then soft-delete account/settings/vault metadata.
- Cryptographically erase ciphertext/key material after the revocation grace period. Keep non-secret external identifiers and publication evidence only as retention requires.

### User

- Disable sessions and access first. Remove memberships/role assignments.
- If erasure applies, anonymize profile/email and external identity data; set nullable actor FKs to null or a documented tombstone principal.
- Keep audit, approval, publication, and billing evidence with non-PII actor identifiers where legally required.

## Restore

- Restore is allowed only during the grace period, before irreversible blob/secret/PII purge, and when parent organization/workspace is active.
- Lock the aggregate root, verify tenant ownership, legal state, and all active-row unique keys. Conflicts require a user-selected rename/relink; restoration never silently displaces an active row.
- Restore parent before children, validate composite FKs, recreate required junctions only from retained evidence, and increment versions.
- Reconnect OAuth accounts rather than restoring expired/revoked secrets. Re-resolve schedules against current timezone rules and require confirmation; never automatically requeue old jobs.
- Emit restored events and append audit records. Immutable rows are never “restored” because they were never soft-deleted.

## Purge and retention

- A purge coordinator selects rows whose `deleted_at + grace_period` has elapsed and that have no legal hold, retention dependency, active export, billing requirement, or unreconciled external operation.
- Defaults: transient idempotency 24–72 hours; leases 7 days; published outbox 30 days; inbox 30–90 days; operational/webhook records 90–365 days; activity/jobs/deliveries 180 days; raw analytics 13 months; aggregates 25 months; financial evidence 7 years; audit 1–7 years by policy.
- Purge child-to-parent in bounded tenant batches through the privileged maintenance role, then vacuum/analyze as appropriate. Large immutable tables expire only by privileged detached partition drop after hold checks.
- Blob purge is two-phase: mark pending deletion, verify no references, delete provider object, then remove metadata. Failures retry and enter dead-letter handling.
- OAuth purge is cryptographic first (destroy key/reference), metadata second. Export packages expire and are deleted from storage before metadata is purged.
- Purge emits summary evidence containing counts, scope, policy, and checksum—not deleted content or secrets.

## FK behavior

- Mutable business parents: `RESTRICT`/`NO ACTION`; service workflows control order.
- Hard-delete junction children: `CASCADE` is acceptable from a parent that itself is being physically purged by privileged maintenance; junction rows still had all six audit columns during their lifetime.
- Actor references: `ON DELETE SET NULL`.
- Immutable facts: retain FK while parent remains; before lawful parent physical purge, either retain a minimal tombstone parent or replace the FK with a non-PII immutable snapshot only through a reviewed migration.
- Cross-workspace references are impossible through composite `(workspace_id,parent_id)` FKs.

## Active-row uniqueness examples

- `users(email) WHERE deleted_at IS NULL AND email IS NOT NULL`
- `workspaces(organization_id,slug) WHERE deleted_at IS NULL`
- `content_drafts(workspace_id,asset_id) WHERE deleted_at IS NULL`
- `social_accounts(workspace_id,platform_id,external_account_id) WHERE deleted_at IS NULL`
- `oauth_token_vaults(workspace_id,social_account_id) WHERE deleted_at IS NULL`
- `publication_schedules(workspace_id,publication_target_id) WHERE deleted_at IS NULL AND state IN ('scheduled','paused','dispatched')`
- `notification_preferences(workspace_id,user_id,notification_type_id,channel) WHERE deleted_at IS NULL`

`external_identities(issuer,subject)` is intentionally permanent uniqueness: deleting and recreating a mapping must not allow silent identity takeover.

## Verification

Test delete/restore/purge for every aggregate with uniqueness collisions, cross-tenant guessed IDs, active schedules, published targets, shared blobs, revoked secrets, legal holds, billing retention, nested folders/comments, retry after partial failure, and concurrent updates. Verify ordinary reads, search indexes, analytics projections, exports, and outbox consumers exclude deleted business rows.
