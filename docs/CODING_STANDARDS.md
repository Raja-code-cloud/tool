# Coding Standards

## TypeScript

- Enable strict mode and do not weaken compiler options.
- Prefer `unknown` over `any`; narrow at boundaries.
- Model finite states with discriminated unions.
- Use exhaustive `switch` statements with a `never` check.
- Use `satisfies` for configuration objects that should retain inferred literals.
- Avoid non-null assertions; prove the value or handle absence.
- Keep imports at the top of the module.

## React

- Use function components and hooks.
- Never mutate props, state, or cached data.
- Derive values during render instead of synchronizing redundant state.
- Use effects only to synchronize with external systems.
- Do not use array indexes as keys for mutable collections.
- Give interactive elements semantic HTML before adding ARIA.

## Naming

- Components, types, and enums: `PascalCase`.
- Variables, functions, hooks, and props: `camelCase`.
- Hooks: `useX`.
- Constants: `UPPER_SNAKE_CASE` only for true module-level constants.
- Component files: `kebab-case.tsx`; hooks and utilities: `kebab-case.ts`.
- Route segments: lowercase kebab-case.
- Boolean names start with `is`, `has`, `can`, or `should`.
- Event props use `onX`; local handlers use `handleX`.

## Imports

Order imports as framework/external, internal aliases, then relative modules. Separate type imports with `import type`. Prefer the configured project alias over deep relative traversal.

## Control flow

- Return early for invalid, loading, and permission states.
- Keep nesting shallow.
- Extract repeated policy or transformation logic into typed functions.
- Comments explain constraints or intent, never restate code.

## Testing

- Test user-visible behavior and domain transformations.
- Prefer role- and label-based queries.
- Do not test library internals or implementation details.
- Add regression coverage for fixed defects.

## Review requirements

No dead code, suppressed type errors without rationale, untracked TODOs, debug logging, duplicated components, inaccessible interactions, or secrets may enter production code.
