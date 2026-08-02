# Component Architecture

## Categories

```text
components/
  ui/           # shadcn primitives and approved variants
  layout/       # shells, containers, page structure
  navigation/   # sidebar, breadcrumbs, tabs, pagination
  buttons/      # domain-specific button compositions
  cards/        # reusable content containers
  forms/        # shared fields and form composition
  tables/       # table framework and cells
  charts/       # chart wrappers, legends, tooltips
  upload/       # file selection, queue, progress
  analytics/    # reusable analytics presentations
  feedback/     # alerts, empty states, errors, skeletons
  common/       # cross-domain compositions with proven reuse
```

Feature-specific components belong under `app/(dashboard)/<route>/_components/` in the current implementation. A top-level `features/<feature>/components` layout is a target convention for future greenfield modules—not a requirement to reorganize existing routes.

## Component layers

1. **Primitive:** accessible, styleable UI building block.
2. **Composition:** combines primitives into a reusable interaction.
3. **Feature:** understands domain terminology and feature data.
4. **Route:** arranges features and owns route-level boundaries.

Dependencies flow downward. Primitives must not import feature or route code.

## Component contract

- One primary responsibility per component.
- Use explicit props and exported named types; avoid broad bags such as `data: any`.
- Prefer composition and `children` over boolean-heavy APIs.
- Forward refs only when consumers need focus or element access.
- Accept `className` on reusable visual components and merge it with `cn`.
- Do not embed network calls in reusable presentational components.
- Use named exports except where Next.js requires default exports.
- Keep files focused; split when independent behavior, testing, or reuse becomes clear.

## Server and client boundaries

Server components may load data and compose client islands. Client components must not import server-only modules. Add `"use client"` only to files that directly require client behavior; do not propagate it to an entire subtree for convenience.

## Variants

Use `class-variance-authority` for stable visual variants. Variant names describe semantics (`destructive`, `secondary`, `compact`), not raw colors. New variants require a repeated product use case.

## Public APIs

Use feature-level `index.ts` files only to expose intentional public APIs. Avoid repository-wide barrel files because they obscure dependencies and can increase bundle size.

