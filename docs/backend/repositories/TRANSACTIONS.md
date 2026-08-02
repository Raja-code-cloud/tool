# Transactions

## Purpose

Transaction management guarantees atomic use-case persistence with automatic rollback on failure and support for nested savepoints.

## Components

- `TransactionManager`: manages outer transactions and nested savepoints for one session
- `SqlAlchemyUnitOfWork`: request/job-scoped wrapper that creates the session and delegates to the transaction manager

## Behavior

### Automatic rollback

Any uncaught exception inside a unit-of-work context triggers rollback before the session is closed.

### Nested transactions

`await unit_of_work.begin()` starts a nested savepoint. Nested contexts may commit locally while the outer transaction remains open until the root context succeeds.

### Flush without commit

`await unit_of_work.flush()` writes pending INSERT/UPDATE/DELETE operations to the database without committing. Use this when downstream repository operations need database-generated values or constraint checks inside the same transaction.

## Error propagation

Repository methods raise typed infrastructure exceptions such as:

- `EntityNotFound`
- `DuplicateEntity`
- `ConcurrencyConflict`
- `TransactionFailed`

Application services decide whether to retry, translate, or abort. Repositories do not swallow database exceptions.

## Concurrency

Optimistic updates rely on the mapped `version` column. Zero affected rows during update, soft delete, or restore produce `ConcurrencyConflict`. Application services map that to `VersionConflictError` at the delivery boundary.

## Savepoint example

```python
async with SqlAlchemyUnitOfWork(session_factory) as unit_of_work:
    await repository.create(first_entity)
    async with unit_of_work.transaction:
        await repository.create(second_entity)
```

If the nested block fails, only the savepoint rolls back unless the failure propagates to the outer context.
