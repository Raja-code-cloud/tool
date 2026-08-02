# Unit of Work

## Purpose

The unit of work owns transaction boundaries for a use case. Repositories flush changes through a shared session, but only the unit of work commits or rolls back.

## Implementation

`SqlAlchemyUnitOfWork` wraps an `async_sessionmaker[AsyncSession]` and exposes:

- `session`: active async session for repositories
- `transaction`: nested transaction manager
- `begin()`: start a nested transaction or savepoint
- `flush()`: flush pending changes without committing
- `commit()`: commit the outermost transaction
- `rollback()`: rollback the active transaction

## Usage

```python
async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
    tag_repository = SqlAlchemyRepository(unit_of_work.session, Tag, workspace_scoped=True)
    await tag_repository.create(tag)
    await unit_of_work.flush()
```

When the context exits successfully, the unit of work commits. When an exception propagates, it rolls back automatically.

## Rules

- One unit of work per application command or query that mutates state.
- Do not share a unit of work across unrelated requests or background jobs.
- Application services coordinate repositories through the same unit of work instance.
- External provider calls must not occur while a long-lived unit of work remains open.

## Relationship to FastAPI

HTTP dependencies may construct a request-scoped unit of work. Route handlers and application services receive repositories bound to that session. Commit/rollback remains in middleware or the application service, not in route bodies.
