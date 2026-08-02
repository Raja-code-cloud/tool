# Naming Conventions

Applies to the complete **86-table PostgreSQL 17** design.

## SQL identifiers

- Use unquoted lowercase `snake_case`; plural nouns for tables (`publication_targets`), singular nouns for columns (`publication_id`).
- Primary key is `id uuid`. Foreign keys are `<singular_parent>_id`; polymorphic references use paired `<concept>_type` and `<concept>_id` only where a closed FK is impossible.
- Every workspace-owned table has `workspace_id`; organization-owned commercial tables have `organization_id`. Never call either `tenant_id`: the two boundaries mean different things.
- Boolean names start with `is_`, `has_`, or a clear capability verb: `is_active`, `has_video`, `publishing_enabled`.
- UTC instants end `_at` (`published_at`); date-only values end `_date`; local clock values end `_local_at`; durations include units (`duration_ms`); counts end `_count`; money uses `<concept>_amount` plus `currency`.
- Hashes/fingerprints state the algorithm or purpose (`checksum_sha256`, `request_hash`, `token_fingerprint`). Encrypted material is `ciphertext` or `<concept>_secret_ref`, never misleadingly `token`.
- JSON columns describe their shape (`capability_metadata`, `provider_fragment`, `safe_diff`), not `data` or `json`.
- Use `code` for machine-stable catalog identifiers, `name` for display labels, `external_*_id` for vendor identifiers, and `idempotency_key`/`dedupe_key` only for their distinct semantics.

## Universal audit and lifecycle columns

Every table without exception uses these columns in this order:

`created_at`, `updated_at`, `created_by`, `updated_by`, `deleted_at`, `version`.

Types/defaults are `created_at timestamptz NOT NULL DEFAULT now()`, `updated_at timestamptz NOT NULL DEFAULT now()`, `created_by uuid NULL`, `updated_by uuid NULL`, `deleted_at timestamptz NULL`, and `version integer NOT NULL DEFAULT 1 CHECK (version > 0)`. This applies equally to business, operational, catalog, junction, immutable, and integration tables. Global/system actors may be null.

For mutable rows, `deleted_at IS NULL` means active and successful updates advance `updated_at`, `updated_by`, and `version`. Immutable rows initialize `updated_at = created_at`, `updated_by = created_by`, `deleted_at = NULL`, and `version = 1`; a named check plus mutation-guard trigger/policy and privilege revocation enforce append-only behavior. Junctions may be hard-deleted under their policy but still have all six columns while present. `version` is an optimistic concurrency integer, not a content revision. Content revision is `version_number`; event schema revision is `event_version`; template revision is `template_version`.

Constraint names for immutable shape and mutation protection use `ck_<table>__immutable_audit_shape` and `trg_<table>__reject_mutation`. Physical retention purge and partition drop are maintenance operations, not ordinary row lifecycle updates.

Immutable facts use `occurred_at` for domain occurrence and `created_at` or `received_at` for ingestion. Do not overload `timestamp`.

## Status vocabulary

- Columns use precise state-machine names, never generic `status` when ambiguity exists: `lifecycle_status`, `approval_state`, schedule `state`, job `state`, `health_status`, `connection_status`, `scan_status`.
- Values are lowercase `snake_case` text constrained with `CHECK`; PostgreSQL ENUMs are prohibited.
- Content lifecycle: `draft`, `active`, `archived`.
- Approval: `pending`, `approved`, `rejected`, `changes_requested`, `cancelled`.
- Schedule: `draft`, `scheduled`, `paused`, `dispatched`, `completed`, `cancelled`, `failed`.
- Job: `queued`, `leased`, `running`, `retry_wait`, `succeeded`, `failed`, `dead_lettered`, `cancelled`.
- Do not reuse UI roll-up labels as persisted state. “Publishing” and “Needs approval” are projections composed from the four independent state machines.
- Catalog rows, not checks, represent extensible providers, models, platforms, metrics, permissions, and usage dimensions.

## Constraints

Keep names under PostgreSQL's 63-byte limit; abbreviate only well-known words (`fk`, `pk`, `uq`, `ck`, `ix`).

- Primary key: `pk_<table>`
- Foreign key: `fk_<child>__<columns>__<parent>`
- Unique constraint/index: `uq_<table>__<columns>[_where_<predicate>]`
- Check: `ck_<table>__<rule>`
- Exclusion: `ex_<table>__<rule>`
- Non-unique index: `ix_<table>__<columns>[_where_<predicate>]`
- GIN/BRIN suffix: `_gin` / `_brin`

Examples: `fk_comments__workspace_id_asset_id__content_assets`, `ck_publication_schedules__fold`, `uq_tags__workspace_id_name_where_active`.

Composite tenant FKs list `workspace_id` first on both sides. Constraint names must express the actual columns, not an ORM relationship name.

## Indexes

- Name columns in index order. Add `desc` only when it materially documents cursor order.
- Partial indexes append a short predicate phrase: `_where_active`, `_where_due`, `_where_unread`.
- Expression indexes append the normalized expression concept, not raw SQL.
- Partition child indexes inherit the logical base name plus a generated partition suffix; migrations refer to the parent logical index.
- Avoid auto-generated names in reviewed migrations.

## Schemas, partitions, and sequences

- Initial deployment may use `public`; if database schemas are introduced, use bounded-context names such as `content`, `publishing`, and `billing`, never tenant-specific schemas.
- Partition names: `<table>_p<yyyy_mm>` for monthly ranges, e.g. `audit_logs_p2026_08`; default partition `<table>_pdefault`.
- UUIDs require no sequences. Any unavoidable sequence is `<table>_<column>_seq`.

## Time, timezone, and scheduling

- Persist instants as UTC `timestamptz`; APIs emit RFC 3339.
- IANA zone column is `time_zone`, never an offset or abbreviation.
- Scheduling uses `requested_local_at timestamp without time zone`, `time_zone`, `fold`, `ambiguity_policy`, and resolved `scheduled_for timestamptz`.
- A nonexistent DST wall time is rejected. Ambiguous times require `fold` (`0` first, `1` second) or explicit `earlier`/`later`; default policy is `reject`.

## API/domain mapping

- Database names remain storage-oriented and precise; API fields may be camelCase but map explicitly.
- Domain aggregate names are singular (`ContentAsset`); tables are plural (`content_assets`).
- Provider terminology stays behind adapters unless it is an external identifier or redacted provider fragment.
- Event types use past-tense dotted names with version outside the name, e.g. `publication.scheduled` plus `event_version=1`.

## Migration naming

- Migration filename/ID: UTC sortable prefix plus imperative summary, e.g. `20260802_152500_add_publication_schedule_fold`.
- Use verbs accurately: `add`, `backfill`, `validate`, `enforce`, `drop`; never “update schema”.
- One migration has one deploy-safe purpose. Data backfills are named separately from constraint enforcement.

## Reserved and prohibited forms

- Avoid SQL keywords and vague names: `user`, `order`, `group`, `type`, `data`, `value`, `item`, `info`, `status` without qualification.
- Do not encode provider/platform names into table or column names. Future providers/platforms are rows.
- Do not prefix tables with `tbl_`, columns with type hints, or indexes with ORM-generated hashes.
- Do not use absolute blob URLs, plaintext-secret columns, timezone abbreviations, floating-point money, or PostgreSQL ENUM types.
