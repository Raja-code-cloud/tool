# Frontend Guidelines

## Purpose

These standards govern frontend implementation for Cloud Content Hub AI. Product architecture and design documentation, when added, takes precedence over this document.

## Engineering principles

- Preserve the established architecture and visual language.
- Prefer existing components, hooks, utilities, and tokens before adding abstractions.
- Keep server-rendered output by default; add `"use client"` only at the smallest interactive boundary.
- Build accessible, responsive, typed interfaces with predictable loading, empty, error, and success states.
- Keep feature code cohesive and shared code genuinely reusable.
- Do not place business rules in presentation components.

## Implementation workflow

1. Read relevant product and design documentation.
2. Locate existing analogous screens and components.
3. identify server/client boundaries and data requirements.
4. Reuse primitives and compose small domain components.
5. Define all states before implementation.
6. Verify keyboard access, responsive behavior, types, lint, and tests.

## Next.js and React

- Use the App Router and React Server Components by default.
- Fetch initial route data on the server when supported by the backend.
- Use client components for browser APIs, local interaction, forms, animation, and client caches.
- Keep route files thin; compose feature components and colocate route-specific loading and error boundaries.
- Use Server Actions only when adopted by project architecture; otherwise call typed route handlers or API clients.
- Never pass secrets or privileged data into client components.

## UI composition

- shadcn/ui primitives are the accessible foundation, not a second design system.
- Encode visual decisions in shared variants and semantic design tokens.
- Every data surface must define loading, empty, error, permission-denied, and populated states where applicable.
- Destructive actions require explicit language and confirmation proportionate to impact.

## Quality gate

Before review, changes must pass TypeScript, linting, relevant tests, responsive checks, keyboard checks, and an inspection for duplicated patterns. Document intentional exceptions.

