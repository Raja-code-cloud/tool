# Bootstrap Layer

## Purpose

The bootstrap package is the composition root for Cloud Content Hub AI. It is the only layer that may import all other layers to construct the running process. No business logic lives here — only dependency registration, lifecycle wiring, and adapter construction.

## Location

```text
backend/src/cloud_content_hub/bootstrap/
├── __init__.py
├── api.py                 # FastAPI application factory
├── worker.py              # Celery application factory
├── container.py           # Process-scoped DI container
├── configuration.py       # Typed settings aggregation
├── providers.py           # Infrastructure-to-application port adapters
├── repositories.py        # Repository factory registration
├── services.py            # Application service registration
├── handlers.py            # Handler registry wiring
├── events.py              # Outbox and Celery producer wiring
├── health.py              # Health contributor registration
├── startup.py             # Async startup and lifespan hook
└── shutdown.py            # Graceful resource disposal
```

## Responsibilities

| Module                       | Role                                                                                                                                                   |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `configuration.py`           | Loads core `Settings` plus identity, observability, storage, and AI configuration                                                                      |
| `container.py`               | Owns process lifetime for database, Redis, Celery, observability, events, identity, storage, AI, ports, repositories, services, and health             |
| `providers.py`               | Adapts infrastructure clients to application ports (`AIGenerationPort`, `IObjectStoragePort`, admin status ports, schedule time resolver, clock, UUID) |
| `repositories.py`            | Registers `SqlAlchemyUnitOfWork` and SQLAlchemy repository factories                                                                                   |
| `handlers.py`                | Builds the delivery-layer `HandlerRegistry` with constructor-injected dependencies                                                                     |
| `startup.py` / `shutdown.py` | Verifies and releases external dependencies in order                                                                                                   |
| `health.py`                  | Registers database, Redis, storage, application, and outbox health contributors                                                                        |

## Dependency rules

- Constructor injection only; no service locator or import-time singletons.
- Application and domain code never import bootstrap.
- Bootstrap never encodes product policy — it wires completed layers together.
- Missing infrastructure adapters (for example `IBackgroundJobRepository`) remain explicit `UnwiredDependency` placeholders until repository implementations exist.

## Entry points

- **HTTP**: `bootstrap.api.create_app()` constructs `Container`, wires handlers, and attaches `bootstrap_lifespan`.
- **Workers**: `bootstrap.worker.create_celery_app()` provides the Celery broker used by the outbox dispatcher.

See also: [`DEPENDENCY_GRAPH.md`](DEPENDENCY_GRAPH.md), [`SERVICE_REGISTRATION.md`](SERVICE_REGISTRATION.md), [`STARTUP_SEQUENCE.md`](STARTUP_SEQUENCE.md).
