# Dependency Rules

## Governing rule

Dependencies point toward business policy:

```text
presentation/workers -> application -> domain
infrastructure ------> application/domain ports
bootstrap -----------> all layers for composition only
```

The source layer owns the abstraction it needs. Infrastructure implements inward-owned ports; domain/application code never imports concrete adapters.

## Layer rules

### Domain

May import the Python standard library and approved domain-only primitives. It must not import web frameworks, validation frameworks tied to HTTP, ORM/database packages, cloud/provider SDKs, queue clients, settings libraries, or infrastructure.

### Application

May import its module's domain and stable `core` primitives. It defines use cases, DTOs, transaction/repository/provider ports, and authorization requirements. It must not import routers, middleware, ORM models, SQL, concrete repositories, provider SDKs, or another module's internals.

### Presentation and workers

May import their module's application public API and approved cross-cutting API primitives. They translate transport/job input and invoke one or more use cases. They may not query persistence, instantiate SDK clients, or encode domain transitions.

### Infrastructure

May import inward ports and domain types needed for mapping. Database mappings and adapters are private implementation details. Infrastructure modules do not call presentation code and do not become a second service layer.

### Bootstrap

May import all layers solely to construct the process. Nothing outside bootstrap may import bootstrap.

## Feature boundaries

- A module may consume another module only through its documented application facade, stable DTO, or published event.
- Direct imports of another module's `domain`, repository implementation, ORM mapping, or private function are forbidden.
- Cross-module writes are coordinated by an owning application service or asynchronous events. One module never mutates another module's tables directly.
- Cross-module reads use an exposed query port/read model. Ad hoc joins across bounded modules require architecture review and a declared owner.
- Cyclic module dependencies are forbidden. Resolve them with an inward abstraction, orchestration service, or event.

## Shared modules

`core` is restricted to stable, feature-neutral capabilities such as IDs, clock, actor/request context, base errors, configuration interfaces, telemetry interfaces, and pagination primitives. A contribution to `core` must have at least two real consumers and no feature vocabulary.

Do not create `common.py`, `helpers.py`, or `utils.py` dumping grounds. Validation rules, constants, exceptions, and policies remain in the owning feature. Shared code may depend only on the standard library or explicitly approved foundational packages.

## Dependency inversion

Ports are narrow, capability-oriented protocols. Prefer `ObjectStorage.put_capability()` over exposing an Azure client, and `AIProvider.generate()` over exposing an SDK session. Port methods use domain/application DTOs, not provider payloads or ORM objects.

Inject clock, UUID generation, secrets, external clients, repositories, unit of work, and event publisher where determinism or replacement matters. Do not hide dependencies in globals, decorators with side effects, import-time initialization, or service locators.

## Database ownership

Each table has one owning module. Only that module's repository implementation writes it. Transactional outbox and audit writes occur through dedicated ports inside the same transaction. Raw SQL is confined to database infrastructure and migrations. Repository return values are domain entities or declared read DTOs, never ORM rows.

## Forbidden imports and behaviors

- Domain/application importing FastAPI, SQLAlchemy, Alembic, cloud SDKs, HTTP clients, or worker runtimes.
- Routes importing database sessions or concrete repositories.
- Modules importing provider-specific adapters.
- Infrastructure importing presentation.
- Production modules importing test factories or fixtures.
- Runtime code importing from migration files.
- Relative traversal into another feature's private package.
- Inline imports except a documented, unavoidable circular-dependency boundary; redesign is preferred.

## Enforcement

CI runs architecture tests that encode allowed package edges and detect cycles. Static typing runs across the complete package. Code owners review changes to module public APIs, `core`, ports, and bootstrap wiring. A temporary exception requires an owner, rationale, expiry issue, and architecture decision record; undocumented exceptions fail review.
