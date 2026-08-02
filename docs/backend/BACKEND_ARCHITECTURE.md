# Backend Architecture

## Purpose

This document defines the target backend architecture for Cloud Content Hub AI. It is an implementation contract, not executable code. The database documents at the repository root remain authoritative for tables, constraints, indexes, migrations, and retention.

## Architectural style

Use a modular monolith with Clean Architecture boundaries. Modules may later be extracted behind events or APIs, but engineers must not introduce network boundaries without measured scaling, ownership, or isolation needs.

Dependency direction is inward:

`delivery and workers -> application -> domain`

Infrastructure implements interfaces owned by the application or domain layers. The domain has no dependency on FastAPI, an ORM, PostgreSQL, queues, cloud SDKs, or provider SDKs.

## Layers

| Layer          | Responsibility                                                                               |
| -------------- | -------------------------------------------------------------------------------------------- |
| Domain         | Entities, value objects, state transitions, invariants, domain errors, repository ports      |
| Application    | Commands, queries, use-case services, authorization orchestration, transactions, DTOs, ports |
| Infrastructure | PostgreSQL repositories, storage, queues, encryption, provider adapters, telemetry           |
| Delivery       | HTTP routes, request/response schemas, middleware, authentication extraction                 |
| Workers        | Background consumers, schedulers, lease handling, retries, event handlers                    |

Delivery validates transport shape and delegates. It must not contain business decisions or issue ORM queries. Application services coordinate one use case and own transaction boundaries. Domain code decides whether a transition is valid.

## Bounded modules

The modules are `identity`, `tenancy`, `content`, `storage`, `ai`, `social`, `publishing`, `notifications`, `settings`, `analytics`, `billing`, and `operations`. A module exposes application commands, queries, DTOs, events, and ports; its internal models and repositories are private.

Organization is the billing boundary. Workspace is the operational tenant and authorization boundary. Every workspace command and query receives an explicit validated workspace context; missing scope fails closed.

## Repository pattern

- Define repository protocols beside the application/domain code that consumes them.
- Repositories operate on aggregates or explicit read models, not generic CRUD.
- Every workspace-owned method requires `workspace_id`; active reads also require `deleted_at IS NULL`.
- Child lookups use tenant-safe keys. Never load a workspace-owned row by bare ID.
- Mutations use optimistic concurrency with `version`; zero updated rows produces a conflict.
- Repositories never commit. The application unit of work owns commit/rollback.
- Special access to deleted rows is exposed only through named administrative methods with authorization and audit.
- RLS is defense in depth. Each transaction sets validated transaction-local workspace context and the pool resets it.

## Service layer and transactions

Application services represent use cases such as create asset, approve version, schedule publication, connect account, or request generation. A service:

1. authenticates an actor context and authorizes a permission;
2. validates tenant ownership and current aggregate version;
3. executes domain rules;
4. persists through repositories in one unit of work;
5. writes audit and transactional outbox records in that transaction;
6. returns an application DTO, not an ORM object.

External calls do not remain inside long database transactions. Persist intent/outbox work first, then execute asynchronously with idempotency and compensation.

## Dependency injection

Use constructor injection for services and explicit provider functions at composition roots. Production, tests, HTTP delivery, and workers may create different compositions. Do not use service locators, mutable global containers, or import-time clients. Resource lifetimes are explicit: process-wide immutable clients, request/job-scoped unit of work, and function-scoped repositories.

## HTTP middleware order

The effective order is: trusted proxy normalization, request/correlation IDs, security headers, CORS, size/time limits, authentication, workspace resolution, rate limiting, transaction context/RLS, route handler, error mapping, access logging, metrics. Middleware may enrich context but cannot silently choose a workspace.

## Configuration

Configuration is loaded once from environment and approved secret providers into typed immutable settings. Startup validates required values and dependency reachability. Environment names select values, never behavior branches scattered through domain code. See `CONFIGURATION_GUIDE.md`.

## Authentication and authorization flow

1. Validate the JWT signature, issuer, audience, algorithm, expiry, and not-before against cached OIDC metadata.
2. Resolve `(issuer, subject)` to one active `external_identity` and user.
3. Check user/session revocation where the token/session model requires it.
4. Resolve the requested workspace from an explicit route/header contract.
5. Verify active organization/workspace membership and compute permissions from workspace roles.
6. create an immutable actor context containing user, organization, workspace, permissions, session, request, and correlation identifiers.
7. Set transaction-local RLS context only after scope validation.

Organization membership does not grant workspace access. Authentication failures return 401; authenticated actors lacking permission return 403.

## Background jobs and events

`publishing_jobs` is dedicated to publishing. `background_jobs` handles `ai`, `media`, `notification`, and `maintenance` queues. Workers claim jobs atomically, obtain a lease, heartbeat, use bounded exponential backoff with jitter, and dead-letter terminal failures. Handlers are idempotent because delivery is at least once.

Transactional outbox events are persisted with business changes. Consumers use inbox deduplication. Event names are past-tense dotted names with a separate `event_version`. Payloads contain stable identifiers and redacted snapshots, not secrets.

## Storage

Azure Blob is the default provider behind a storage port. The backend issues short-lived, least-privilege upload/download capabilities; credentials and permanent public URLs are prohibited. Objects use tenant-prefixed keys, checksums, MIME validation, malware-scan state, and encryption references. Finalization verifies size/checksum and creates metadata. Purge is two-phase and reference/hold aware.

## AI abstraction

AI providers and models are catalog data. The application calls an `AIProvider` port with normalized requests and receives normalized output, usage, safety, and provider-reference data. Provider SDK objects and terminology stay in adapters. Prompt/model versions, idempotency, source content version, cost, and token usage are persisted. Outputs are immutable; accepted output creates a new content version rather than mutating history.

## Scheduler and publishing

The scheduler stores requested wall time, IANA zone, fold/policy, and resolved UTC time. Nonexistent times are rejected; ambiguous times require an explicit choice. A dispatcher claims due schedules briefly and creates publishing jobs. At dispatch it rechecks approved immutable content, healthy enabled account, permission, and idempotency. Schedule, publishing job, approval, and content lifecycle states remain independent.

## Integrations

Each external platform is implemented behind an adapter for OAuth, capabilities, publishing, deletion, and metrics. Capabilities are data-driven. OAuth material is envelope-encrypted ciphertext or a managed-secret reference. Inbound webhooks verify signatures, record a receipt before processing, deduplicate, and enqueue work. Adapters classify provider errors as retryable, rate-limited, authentication-required, invalid-input, or terminal.

## Operational requirements

All entry points emit structured logs, traces, metrics, request/correlation IDs, and audit evidence where material. Readiness covers required dependencies; liveness only proves the process can run. Graceful shutdown stops intake, lets bounded in-flight work finish, and releases leases safely.
