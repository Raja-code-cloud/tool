# Specification Pattern

## Purpose

Specifications express composable query intent without leaking SQLAlchemy details to the application layer. Repositories translate specifications into SQL expressions at the infrastructure boundary.

## Core types

- `Specification[ModelT]`: abstract composable filter
- `AttributeEquals`: compare one mapped attribute to a constant
- `CustomSpecification`: wrap an expression factory for entity-specific cases
- `AndSpecification`, `OrSpecification`, `NotSpecification`: boolean composition

## Composition

Specifications support Python operators:

```python
active = AttributeEquals("status", "active")
published = AttributeEquals("lifecycle_status", "published")
spec = active & published
rows = await repository.find(spec, workspace_id=workspace_id)
```

Negation uses `~spec`. Complex entity joins should use `CustomSpecification` or an entity-specific repository helper.

## Error handling

`SpecificationError` is raised when:

- a referenced attribute does not exist on the mapped model
- a custom factory is not callable
- a custom factory does not return a SQLAlchemy boolean expression

## Design rules

- Keep specifications persistence-oriented, not business-policy oriented.
- Domain invariants belong in domain entities and application services.
- Prefer explicit attribute names over stringly-typed query builders.
- Combine specifications with `RepositoryFilter` only for transport-level list/query parameters.
