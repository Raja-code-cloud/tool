# Entity Relationship Diagrams

These bounded-context diagrams cover the authoritative **86-table** inventory. They emphasize ownership and principal relationships; every workspace-owned child also has the direct `workspace_id` relationship and composite tenant-safe FK described in `DATABASE_SCHEMA.md`. Every entity shown—business, operational, catalog, junction, immutable, or integration—contains `created_at`, `updated_at`, `created_by`, `updated_by`, `deleted_at`, and `version`; the six repeated columns are omitted from diagram boxes only for readability, never from the physical design.

## Identity and tenancy (11)

```mermaid
erDiagram
  users ||--o{ external_identities : maps
  users ||--o{ user_sessions : opens
  organizations ||--o{ organization_memberships : has
  users ||--o{ organization_memberships : joins
  organizations ||--o{ workspaces : owns
  workspaces ||--o{ workspace_memberships : has
  users ||--o{ workspace_memberships : joins
  workspaces o|--o{ roles : defines
  roles ||--o{ role_permissions : grants
  permissions ||--o{ role_permissions : included
  workspace_memberships ||--o{ membership_roles : assigned
  roles ||--o{ membership_roles : assigned
```

## Content, projects, collaboration, and storage (24)

```mermaid
erDiagram
  workspaces ||--o{ projects : owns
  workspaces ||--o{ folders : owns
  folders o|--o{ folders : contains
  workspaces ||--o{ collections : owns
  collections ||--o{ collection_items : contains
  content_assets ||--o{ collection_items : included
  workspaces ||--o{ tags : defines
  content_assets ||--o{ asset_tags : tagged
  tags ||--o{ asset_tags : applies
  workspaces ||--o{ categories : defines
  categories o|--o{ categories : contains
  content_assets ||--o{ asset_categories : classified
  categories ||--o{ asset_categories : applies
  projects o|--o{ content_assets : groups
  folders o|--o{ content_assets : contains
  content_assets ||--o| articles : article
  content_assets ||--o| videos : video
  content_assets ||--o| posters : poster
  content_assets ||--o| thumbnails : thumbnail
  workspaces ||--o{ storage_objects : owns
  content_assets ||--o{ asset_storage_objects : attaches
  storage_objects ||--o{ asset_storage_objects : attached
  content_assets ||--o| content_drafts : current_draft
  content_assets ||--o{ content_versions : versions
  content_versions o|--o{ content_versions : derived_from
  content_assets ||--o{ comments : discussed
  comments o|--o{ comments : replies
  content_versions o|--o{ comments : anchors
  content_versions ||--o{ approval_requests : reviewed
  approval_requests ||--o{ approval_steps : contains
  workspaces ||--o{ saved_views : owns
  workspaces ||--o{ brand_profiles : owns
  projects ||--o{ project_members : staffed
  users ||--o{ project_members : participates
  content_assets ||--o{ content_relations : source
  content_assets ||--o{ content_relations : target
```

## AI generation (8)

```mermaid
erDiagram
  ai_providers ||--o{ ai_models : offers
  workspaces ||--o{ ai_prompt_templates : owns
  content_versions ||--o{ ai_generation_requests : sources
  ai_models ||--o{ ai_generation_requests : executes
  ai_prompt_templates o|--o{ ai_generation_requests : configures
  brand_profiles o|--o{ ai_generation_requests : guides
  ai_generation_requests ||--o{ ai_generation_outputs : produces
  ai_generation_requests ||--o{ ai_usage_records : meters
  ai_providers ||--o{ ai_usage_records : bills
  ai_models ||--o{ ai_usage_records : bills
  content_versions ||--o{ ai_suggestions : receives
  ai_generation_requests o|--o{ ai_suggestions : suggests
  ai_suggestions ||--o{ ai_suggestion_actions : history
```

## Social accounts (7)

```mermaid
erDiagram
  social_platforms ||--o{ social_platform_capabilities : describes
  social_platforms ||--o{ social_content_templates : formats
  workspaces o|--o{ social_content_templates : overrides
  social_platforms ||--o{ social_accounts : hosts
  workspaces ||--o{ social_accounts : connects
  social_accounts ||--o| oauth_token_vaults : secures
  social_accounts ||--o{ social_account_permissions : grants
  social_accounts ||--o| social_account_settings : defaults
```

## Publishing and scheduling (8)

```mermaid
erDiagram
  content_assets ||--o{ publications : publishes
  content_versions ||--o{ publications : freezes
  approval_requests o|--o{ publications : authorizes
  publications ||--o{ publication_targets : targets
  social_accounts ||--o{ publication_targets : receives
  social_platforms ||--o{ publication_targets : platform
  content_versions ||--o{ publication_targets : renders
  ai_generation_outputs o|--o{ publication_targets : variant
  publication_targets ||--o{ publication_schedules : schedules
  publication_schedules ||--o{ publishing_jobs : dispatches
  publication_targets ||--o{ publishing_jobs : executes
  publishing_jobs ||--o{ publishing_attempts : attempts
  publication_targets ||--o{ publication_status_history : records
  publication_schedules o|--o{ publication_status_history : records
  publishing_jobs o|--o{ publication_status_history : records
  publishing_jobs ||--o{ job_leases : leases
  publishing_jobs o|--o{ dead_letters : terminal
```

## Notifications and settings (7)

```mermaid
erDiagram
  notification_types ||--o{ notification_preferences : controls
  users ||--o{ notification_preferences : chooses
  notification_types ||--o{ notifications : classifies
  users ||--o{ notifications : receives
  notifications ||--o{ notification_deliveries : delivers
  notification_types ||--o{ notification_templates : renders
  workspaces o|--o{ notification_templates : overrides
  setting_definitions ||--o{ settings : instantiates
  organizations o|--o{ settings : scopes
  workspaces o|--o{ settings : scopes
  users o|--o{ settings : scopes
  projects o|--o{ settings : scopes
  social_accounts o|--o{ settings : scopes
```

## Analytics (5)

```mermaid
erDiagram
  social_platforms o|--o{ metric_definitions : specializes
  metric_definitions ||--o{ metric_observations : defines
  social_accounts o|--o{ metric_observations : measures
  publication_targets o|--o{ metric_observations : measures
  content_assets o|--o{ metric_observations : measures
  workspaces ||--o{ analytics_snapshots : summarizes
  content_assets ||--o{ content_performance_snapshots : summarizes
  publication_targets ||--o{ content_performance_snapshots : summarizes
  social_accounts ||--o{ social_account_snapshots : summarizes
```

## Usage, quota, subscriptions, and billing (8)

```mermaid
erDiagram
  usage_dimensions ||--o{ usage_events : classifies
  workspaces ||--o{ usage_events : consumes
  organizations ||--o{ usage_events : billed
  usage_dimensions ||--o{ quota_policies : limits
  organizations ||--o{ quota_policies : owns
  workspaces o|--o{ quota_policies : overrides
  usage_dimensions ||--o{ quota_periods : counts
  organizations ||--o{ quota_periods : owns
  organizations ||--o{ subscriptions : subscribes
  subscriptions ||--o{ subscription_items : contains
  usage_dimensions o|--o{ subscription_items : meters
  organizations ||--o{ billing_customers : maps
  organizations ||--o{ billing_events : records
```

## Reliability, audit, and operations (8)

```mermaid
erDiagram
  workspaces o|--o{ activity_logs : records
  organizations o|--o{ audit_logs : scopes
  workspaces o|--o{ audit_logs : scopes
  workspaces ||--o{ idempotency_keys : deduplicates
  workspaces o|--o{ outbox_events : emits
  organizations o|--o{ outbox_events : emits
  outbox_events ||..o{ inbox_messages : consumed_as
  workspaces o|--o{ webhook_receipts : receives
  workspaces o|--o{ background_jobs : executes
  workspaces ||--o{ data_exports : exports
  storage_objects o|--o{ data_exports : packages
```

## Cross-module relationship summary

- Tenancy → every WS module: direct `workspace_id`; no transitive-only tenancy.
- Identity → universal audit: every table has all six audit columns; nullable `created_by`/`updated_by` supports global/system actors and user anonymization without erasing records.
- Content → AI: immutable `content_versions` are generation inputs; outputs can materialize new versions.
- Content → publishing: approved immutable versions feed `publications` and `publication_targets`.
- Social → publishing/analytics: accounts are targets and analytics sources; platforms remain row-extensible catalogs.
- Publishing → notifications/activity/audit: state events create user notifications and ordinary activity while material/security transitions also create append-only audit records. Append-only tables retain all six columns in a fixed immutable shape and reject ordinary mutation.
- AI/publishing/storage → usage/billing: immutable `usage_events` normalize metered consumption and retain the same universal six audit columns.
- All transactional modules → outbox/inbox: state and event persist atomically; consumers deduplicate.

Count reconciliation: 11 + 24 + 8 + 7 + 8 + 5 + 2 + 5 + 8 + 8 = **86 tables**.
