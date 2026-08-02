# Backend Folder Structure

## Canonical hierarchy

The backend is a separately deployable Python package. The name `src/cloud_content_hub` is canonical; do not place backend code in the Next.js `app/` directory.

```text
backend/
├── pyproject.toml
├── README.md
├── .env.example
├── alembic.ini
├── migrations/
│   ├── env.py
│   └── versions/
├── scripts/
├── src/cloud_content_hub/
│   ├── main.py
│   ├── bootstrap/
│   │   ├── api.py
│   │   ├── worker.py
│   │   └── container.py
│   ├── core/
│   │   ├── config.py
│   │   ├── context.py
│   │   ├── errors.py
│   │   ├── logging.py
│   │   ├── security.py
│   │   ├── telemetry.py
│   │   └── types.py
│   ├── api/
│   │   ├── dependencies.py
│   │   ├── middleware/
│   │   ├── schemas/
│   │   └── v1/
│   ├── modules/
│   │   ├── identity/
│   │   ├── tenancy/
│   │   ├── content/
│   │   ├── storage/
│   │   ├── ai/
│   │   ├── social/
│   │   ├── publishing/
│   │   ├── notifications/
│   │   ├── settings/
│   │   ├── analytics/
│   │   ├── billing/
│   │   └── operations/
│   ├── infrastructure/
│   │   ├── database/
│   │   ├── storage/
│   │   ├── messaging/
│   │   ├── auth/
│   │   ├── encryption/
│   │   ├── ai/
│   │   ├── social/
│   │   ├── notifications/
│   │   └── observability/
│   └── workers/
│       ├── runtime.py
│       ├── publishing/
│       ├── ai/
│       ├── media/
│       ├── notification/
│       └── maintenance/
└── tests/
    ├── unit/
    ├── integration/
    ├── contract/
    ├── architecture/
    ├── migration/
    ├── factories/
    └── fixtures/
```

## Responsibilities

- `pyproject.toml`: Python version, dependencies, build metadata, lint/type/test configuration. It is the single tool configuration source where supported.
- `README.md`: local setup, commands, dependency prerequisites, and operational entry points.
- `.env.example`: non-secret variable names and safe examples only.
- `migrations/`: reviewed PostgreSQL migrations. `versions/` contains immutable, deploy-safe revisions named according to `MIGRATION_STRATEGY.md`.
- `scripts/`: thin operational entry points for local/bootstrap/admin tasks. Reusable logic belongs in the package.
- `main.py`: compatibility entry point only; delegates application construction to bootstrap.
- `bootstrap/`: composition roots. `api.py` constructs HTTP delivery, `worker.py` constructs worker processes, and `container.py` wires ports to adapters. No business logic.
- `core/`: small, stable cross-cutting primitives that cannot belong to one feature. It must not become a miscellaneous utility bucket.
- `api/`: HTTP-only concerns. `dependencies.py` resolves request-scoped context; `middleware/` contains isolated middleware; `schemas/` contains truly cross-endpoint transport schemas; `v1/` composes versioned routers.
- `modules/`: bounded business features. Modules do not import another module's internals.
- `infrastructure/`: implementations of ports and process-level technical adapters. It contains no product policy.
- `workers/`: queue runtimes and thin handlers that invoke application use cases. Queue-specific orchestration lives here; domain decisions do not.
- `tests/`: mirrors production boundaries and separates fast unit tests from dependency-backed suites.

## Standard module layout

Each module follows this shape and omits folders it does not need:

```text
modules/<module>/
├── domain/
│   ├── entities.py
│   ├── value_objects.py
│   ├── events.py
│   ├── errors.py
│   └── policies.py
├── application/
│   ├── commands/
│   ├── queries/
│   ├── dto.py
│   ├── ports.py
│   └── services.py
└── presentation/
    ├── router.py
    ├── requests.py
    └── responses.py
```

`domain` is framework-free. `application` coordinates use cases and owns ports. `presentation` maps HTTP transport to application DTOs and may import only its own module plus approved `core` API types.

## Infrastructure layout

`infrastructure/database` owns engine/session setup, unit of work, RLS context, ORM mappings, and repository implementations grouped by module. ORM models are persistence details and never returned from application services.

Provider-specific adapters live one level below their capability, for example `infrastructure/social/linkedin/` or `infrastructure/ai/openai/`. Shared provider base classes may normalize transport behavior but must not encode domain policy.

## Test placement

- `unit/`: domain/application tests without network, filesystem, or database.
- `integration/`: real PostgreSQL, storage emulator, queue, or provider sandbox adapters.
- `contract/`: API schema, event schema, and adapter behavior contracts.
- `architecture/`: import/dependency boundary tests.
- `migration/`: empty-to-head, upgrade, compatibility, and invariant checks.
- `factories/`: deterministic object/data builders.
- `fixtures/`: fixture plugins and static safe samples; no production data.

## File organization rules

Prefer cohesive files below roughly 400 lines. Split by use case or stable responsibility, not arbitrary “utils.” Keep imports at module top. Public module exports are deliberate; do not rely on wildcard exports. A folder is not a boundary unless dependency tests enforce it.
