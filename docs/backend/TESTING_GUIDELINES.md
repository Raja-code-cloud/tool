# Testing Guidelines

## Strategy

Use pytest and a test pyramid: many isolated domain/application unit tests, focused adapter/database integration tests, contract tests for public boundaries, and a small number of end-to-end smoke tests. Tests prove tenant isolation, idempotency, state transitions, and failure behavior—not only happy-path coverage.

## Test layout and markers

Tests live under `tests/unit`, `integration`, `contract`, `architecture`, and `migration`. Name files `test_<subject>.py`, test classes `Test<Behavior>`, and tests `test_<expected_behavior>_when_<condition>`.

Register markers such as `integration`, `contract`, `migration`, `slow`, and `external`. The default developer suite runs deterministic unit and architecture tests. CI runs all required suites in explicit stages; unregistered markers fail.

## Unit tests

Unit tests have no network, real database, filesystem dependency, sleep, or wall-clock dependency. Test domain invariants, permission decisions, state machines, scheduling ambiguity, retry classification, redaction, and application orchestration. Inject deterministic clocks, UUID generators, and fake ports.

Mock only boundaries owned by the application. Prefer small fakes or autospecced protocols. Do not mock private methods, ORM internals, or provider SDK call chains.

## Integration tests

Use a real supported PostgreSQL 17 instance for repositories, transactions, constraints, indexes where relevant, RLS, and migrations. Do not substitute SQLite. Use emulators/containers for storage and queues where behavior is compatible; otherwise use approved sandboxes with isolated credentials.

Each database test runs in a disposable database/schema or rollback-safe transaction while still permitting tests of commits where necessary. Verify SQL and RLS through the actual request/worker roles, not an owner role.

Mandatory database cases include:

- explicit workspace predicates and cross-tenant guessed IDs;
- composite tenant-safe foreign keys;
- active-row filtering and soft-delete uniqueness;
- optimistic version conflicts;
- immutable-row mutation denial;
- idempotency, outbox/inbox, webhook dedupe;
- atomic job claims, leases, heartbeat recovery, quota reservations;
- scheduling DST gaps/folds and UTC resolution.

## Contract tests

Validate OpenAPI against route behavior and perform compatibility checks against the released schema. Test every documented status/error shape, authentication requirement, pagination cursor, unknown field behavior, and idempotency replay.

Provider adapter contract suites run against a common port specification. Webhook tests cover signature verification, replay, malformed payloads, clock tolerance, and redaction. Event contracts verify type, `event_version`, required fields, backward-compatible evolution, and secret-free payloads.

## Fixtures and factories

Fixtures provide infrastructure lifetimes and stable context; factories create domain/database data. Keep fixtures narrow and composable. Avoid autouse fixtures except universal safety cleanup. Factory defaults are valid, minimal, deterministic, and overridable.

Always create at least two organizations/workspaces for tenant-sensitive tests. Generate synthetic data only; production snapshots must be approved and irreversibly sanitized. Secrets used in tests are obvious non-production values.

## Migration tests

Test empty-to-head and upgrade from a production-shaped previous schema. Assert all 86 authoritative table names, six universal audit columns, immutable guards, named constraints, tenant FKs, RLS, partial indexes, statuses, and timezone rules. Test old app/new expanded schema compatibility and lock/runtime behavior for risky migrations. Follow `MIGRATION_STRATEGY.md`.

## Background jobs

Test first execution, duplicate delivery, crash after external success but before acknowledgement, lease expiry, retry backoff, max attempts, dead-letter, replay authorization, and graceful cancellation. Time is controlled; tests never sleep. Verify external side effects remain idempotent.

## Security tests

Include JWT algorithm/issuer/audience/expiry failures, revoked sessions, RBAC denial, cross-tenant access, CORS preflight, upload spoofing, injection payloads, SSRF/redirect allowlists, oversized inputs, webhook replay, rate limiting, and sensitive-data absence from logs/errors/events.

## Coverage and quality gates

Coverage is a risk signal, not the objective. Repository-wide line coverage must be at least 85% and branch coverage at least 75%; domain state machines, authorization, tenancy, money/quota, scheduler, idempotency, and security redaction target 95% branch coverage. New/changed code should not reduce coverage and must cover material branches.

Never exclude business code merely to meet a number. Generated migrations and defensive platform-only branches may be excluded with review. Mutation testing is recommended for authorization and critical domain policies.

## Reliability

Tests must be order-independent, parallel-safe, locale/timezone-explicit, and deterministic. Freeze time at meaningful boundaries. Property-based tests are encouraged for cursors, scheduling, money, normalization, and state transitions. Quarantine is time-bounded with an owner and issue; flaky tests are defects, not rerun policy.

## CI sequence

Run format/lint, strict typing, unit/architecture tests, integration/contract tests, migration tests, security/dependency scans, then smoke tests. Publish coverage and test reports. A retry may diagnose infrastructure flakiness but does not convert an initially failing deterministic test into a pass.
