# Migration Strategy

PostgreSQL 17 deployment policy for the documented **86-table** schema. This document defines operational procedure, not executable migrations.

## Principles

- Every new table, including catalogs, junctions, partitions, immutable facts, and integration infrastructure, must define all six universal audit columns: `created_at`, `updated_at`, `created_by`, `updated_by`, `deleted_at`, and `version`. A migration creating a table without any one of them fails review and automated schema inspection.
- Use expand → migrate → contract. Application releases remain compatible with both old and new shapes during the transition.
- Schema changes are reviewed artifacts, immutable after production use, and applied by a dedicated migration role. Request and worker roles cannot run DDL.
- Prefer roll-forward. A rollback is allowed only when it is proven data-preserving and lock-safe.
- Set migration `lock_timeout` and `statement_timeout`; abort rather than block production traffic. Monitor replicas, WAL volume, long transactions, and connection pool saturation.
- PostgreSQL 17 is the minimum tested version. Extensions, collations, and server settings are explicit environment prerequisites.

## Expand

1. Add nullable columns or columns with safe constant defaults. On PG17, a nonvolatile constant default can avoid a table rewrite, but verify catalog behavior and table size.
2. Add new tables, triggers, and dual-write support before readers depend on them.
3. Create indexes with `CREATE INDEX CONCURRENTLY` outside transaction blocks. For uniqueness, first find/repair duplicates, build a concurrent unique index, then attach a constraint where applicable.
4. Add FKs and expensive checks as `NOT VALID`; new writes are checked immediately while historical rows remain unscanned.
5. Deploy code that can read old/new forms and writes both where necessary. Outbox event schemas change additively and carry `event_version`.

## Migrate/backfill

- Backfill in bounded, resumable batches ordered by PK or tenant and PK. Each batch commits independently, records progress externally or in a controlled migration ledger, and is idempotent.
- Throttle by replica lag, WAL rate, lock wait, and request latency. Use `SKIP LOCKED` only where concurrent worker safety is intentionally designed.
- Do not calculate tenant scope from an untrusted join. For a new `workspace_id`, join through the authoritative ownership chain, detect zero/multiple matches, quarantine anomalies, and verify every populated child has a matching `(workspace_id,parent_id)`.
- For large columns, avoid repeated full-row updates. Backfill only missing rows and vacuum/analyze deliberately.
- Compare old/new read paths with counts, checksums, null rates, cross-tenant orphan queries, and sampled semantic results.
- Stop dual writes only after backfill, validation, and a full compatibility window.

## Contract

1. Validate `NOT VALID` constraints with `VALIDATE CONSTRAINT`; this minimizes blocking compared with adding a fully validated constraint immediately.
2. Enforce `NOT NULL` by first adding/validating an equivalent check, then setting not-null in a short-lock window.
3. Switch reads to the new shape and observe at least one release window.
4. Remove old writes, then old columns/tables/indexes in a later release. Renames use additive aliases/views or dual columns; never combine rename and removal.
5. Drop indexes concurrently where supported. Destructive contract migrations require backup verification and explicit approval.

## Zero-downtime constraint and index patterns

- Foreign key: add `NOT VALID` → verify tenant-safe key population → validate → optionally enforce not-null.
- Unique key: detect duplicates → establish deterministic conflict policy → build unique index concurrently → attach/use it → deploy code relying on uniqueness.
- Check constraint: add `NOT VALID` → backfill/repair → validate.
- New required column: add nullable → dual-write → backfill → add/validate check → set not-null → remove compatibility code.
- Type change: add new column → dual-write/cast in batches → compare → switch reads → contract. Avoid rewrite-heavy in-place casts.
- Index definitions must match `INDEX_STRATEGY.md`, including predicate, column order, opclass, and partition locality.

## Universal audit-column and immutability rollout

- For legacy tables missing audit fields, add all six through expand/migrate/contract: add nullable/safe-default columns, backfill deterministic values, validate checks, then enforce nullability/defaults. Never introduce a permanent table-class exception.
- Backfill `created_at` from the best trustworthy occurrence/ingestion time; otherwise use a documented migration timestamp. Backfill mutable `updated_at` from known modification time or `created_at`, actor IDs where known, `deleted_at` from prior lifecycle evidence, and `version = 1` unless a trustworthy concurrency version exists.
- For immutable/append-only rows, backfill and validate `updated_at = created_at`, `updated_by IS NOT DISTINCT FROM created_by`, `deleted_at IS NULL`, and `version = 1`. Add `ck_<table>__immutable_audit_shape`, revoke ordinary `UPDATE`/`DELETE`, and install/test `trg_<table>__reject_mutation` before declaring the table immutable.
- Partitioned immutable parents and every partition expose identical six-column definitions and protections. Retention detach/drop/purge is granted only to a separate audited maintenance role; request, worker, and ordinary migration/runtime roles cannot bypass mutation guards.
- Junctions and catalogs receive the same six columns and defaults. Junction hard deletion remains policy-controlled and catalogs use status/effective dates, but neither classification changes the schema contract.

## Tenant-safe FK rollout

1. Add direct nullable `workspace_id` and parent `UNIQUE(workspace_id,id)`.
2. Backfill by authoritative parent in tenant-bounded batches.
3. Produce anomaly reports for cross-organization parents, missing ancestors, duplicates, and null scope.
4. Add child `(workspace_id,parent_id)` index concurrently.
5. Add composite FK `NOT VALID`, validate, then enforce `workspace_id NOT NULL`.
6. Deploy explicit workspace predicates before enabling RLS.
7. Negative-test guessed IDs, joins, bulk updates, workers, exports, and soft-deleted parents.

## RLS rollout

- Phase 1: application explicit scope and composite tenant FKs, with query logging/assertions in nonproduction.
- Phase 2: create policies disabled; test through the actual request/worker roles.
- Phase 3: enable RLS for canary roles/workspaces, verify connection pools use transaction-local validated context and reset it.
- Phase 4: enable and `FORCE ROW LEVEL SECURITY` for all WS tables. Table owners are not request roles.
- A safe context function returns no tenant on missing/malformed setting. Never use a policy that treats null context as unrestricted.
- Background global dispatchers use separate least-privilege roles and claim only operational columns; tenant-scoped handlers re-establish workspace context before loading aggregates.
- Keep break-glass bypass time-bound, approved, logged in `audit_logs`, and unavailable to application credentials.

## Workflow and schedule migrations

- Status additions are additive check changes: deploy code tolerant of the new value, replace check safely, then begin writes.
- Status splits (content/approval/schedule/job) require dual projection, deterministic mapping, anomaly review, and only then removal of overloaded legacy status.
- Timezone backfills preserve original wall time and zone. Re-resolve UTC using a pinned tzdata version, record fold/policy, and require manual decisions for ambiguous/nonexistent times; never silently shift scheduled posts.

## Partition lifecycle

- Start unpartitioned unless measured volume warrants partitioning. Converting a live table uses a shadow partitioned table, compatible dual writes/change capture, bounded copy, validation, and short cutover.
- Create monthly partitions at least two periods ahead, with all local indexes/constraints, and alert if inserts reach the default partition.
- Seal old partitions read-only where operationally possible. Detach before archive/drop; verify retention, legal holds, exports, and backups first.
- Global uniqueness across partitions must include the partition key or be enforced through a separate idempotency/catalog table and application invariant.
- Analyze new partitions after load; monitor skew and default-partition growth.

## Rollback and roll-forward

- Expand migrations normally roll back by disabling the new code path, not dropping data.
- Backfills have resumable checkpoints and compensating logic; never “undo” by guessing prior values.
- Contract changes are roll-forward only after compatibility expires. Restore from PITR is an incident-level action, not a routine migration rollback.
- Every release declares: last safe application version, backward-compatible schema range, feature-flag/kill-switch path, and recovery owner.

## Migration tests and gates

- Upgrade from an empty database to head.
- Upgrade a production-shaped snapshot with large tables, deleted rows, orphan probes, and multiple tenants.
- Test previous app + expanded schema, new app + expanded schema, and new app + contracted schema.
- Validate all 86 table names and assert all six audit columns, exact types/defaults/nullability, actor FK policy, and positive-version check on every table. Also validate immutable-shape checks/guards/privileges, composite tenant FKs, RLS policies, partial unique predicates, status checks, and UTC/timezone constraints.
- Run concurrent-write tests for optimistic versions, idempotency, quota reservations, due-job claims, leases, outbox/inbox dedupe, and active-row uniqueness.
- Measure lock duration, rewrite size, migration runtime, WAL/replica lag, and query-plan regressions.
- Test downgrade only where declared supported; otherwise test feature disable and roll-forward repair.

## Backup, PITR, and restore drills

- Use encrypted automated base backups plus continuous WAL archiving for PITR. Define RPO/RTO by plan and region; monitor backup and WAL restore-chain integrity.
- Keep logically separate export capability for tenant portability, but do not treat exports as database backups.
- Run quarterly restore drills into an isolated account/network: restore to a timestamp, apply migrations, verify row counts/checksums, RLS, encryption-key access, blob references, partitions, and critical publish-history queries.
- Run annual regional/disaster recovery exercises and document measured RPO/RTO.
- A backup is not considered valid until restored and application-level invariants pass. Restrict and audit restore access; restored OAuth ciphertext remains protected and external publishing stays disabled until explicitly approved.

## Release evidence

Each migration change set records purpose, affected tables, estimated rows/bytes, lock/rewrite analysis, forward steps, compatibility window, validation queries, telemetry, failure thresholds, recovery path, data classification impact, and retention/partition impact.
