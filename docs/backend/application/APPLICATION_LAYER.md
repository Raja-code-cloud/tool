# Application Layer

## Purpose

The application layer coordinates use cases for Cloud Content Hub AI. It sits between HTTP/worker delivery and infrastructure adapters, owning transaction boundaries, authorization checks, business validation, and DTO mapping.

Implementation lives in `backend/src/cloud_content_hub/application/`.

## Structure

```text
application/
├── shared/           # Actor context, common DTOs, cross-cutting ports
├── assets/           # Asset upload, replace, delete, search
├── content/          # AI generation, regeneration, content queries
├── publishing/       # Publication create, dispatch, cancel
├── scheduler/        # Schedule create, cancel, query
├── analytics/        # Dashboard queries, analytics import
└── notifications/    # Inbox queries, read-state updates
```

Each feature module follows the same internal layout:

```text
<feature>/
├── commands/         # Immutable command objects (write intent)
├── queries/          # Immutable query objects (read intent)
├── handlers/         # Command and query handler classes
├── dto/              # Request and response DTOs (Pydantic v2)
├── validators/       # Business validation (not transport validation)
├── interfaces/       # Repository and provider ports + read models
├── exceptions/       # Feature-specific application errors
└── mappers/          # Read model → response DTO mapping
```

## Responsibilities

| Concern                | Owner                                              |
| ---------------------- | -------------------------------------------------- |
| Use-case orchestration | Command/query handlers                             |
| Authorization          | Handlers via `ActorContext` + `require_permission` |
| Business validation    | Feature validators                                 |
| Transaction boundaries | `IUnitOfWork` (one UoW per mutating use case)      |
| Persistence            | Repository ports (infrastructure implements)       |
| External I/O           | Storage, AI, schedule-time ports                   |
| Response shape         | Application DTOs (never ORM models)                |

## Dependency rules

- Application code imports `core.errors` and its own modules only.
- Repository ports declare read models as dataclasses, not SQLAlchemy models.
- Handlers receive dependencies through constructor injection.
- External provider calls (storage upload, AI generation) happen outside long DB transactions; handlers persist intent and enqueue background jobs first.

## Actor context

Every handler receives an `ActorContext` containing:

- `user_id` — authenticated user UUID
- `workspace_id` — validated workspace scope
- `permissions` — resolved workspace permission set

Handlers call `require_permission(actor, "<resource>:<action>")` before any work.

## Transaction pattern

```python
async with unit_of_work_factory() as unit_of_work:
    repository = repository_factory(unit_of_work)
    await repository.create(...)
    await unit_of_work.flush()
# UoW commits on clean exit, rolls back on exception
```

Repositories never call `commit()`. Only the unit of work owns commit/rollback.

## Wiring

Handlers are constructed at the composition root (`bootstrap/container.py`). Infrastructure provides:

- `SqlAlchemyUnitOfWork` implementing `IUnitOfWork`
- Entity-specific repository implementations for each port
- Storage, AI, and schedule-time resolver adapters

See also: [`USE_CASES.md`](USE_CASES.md), [`COMMANDS.md`](COMMANDS.md), [`QUERIES.md`](QUERIES.md), [`DTO_GUIDE.md`](DTO_GUIDE.md).
