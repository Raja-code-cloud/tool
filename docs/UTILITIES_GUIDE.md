# Utilities Guide

Utilities are pure, narrowly scoped, independently testable functions. Domain rules remain with their feature.

## Organization

```text
lib/utils/
  formatting.ts
  dates.ts
  validation.ts
  strings.ts
  urls.ts
  storage.ts
  theme.ts
  cn.ts
```

Do not create a miscellaneous `helpers.ts`. Split modules by stable responsibility.

## Standards by category

- **Formatting:** use `Intl` for numbers, currency, percentages, and lists; pass locale and units explicitly where product context varies.
- **Dates:** store and transport ISO 8601 values, distinguish instants from calendar dates, and format in the user's locale/time zone.
- **Validation:** centralize reusable Zod schema fragments; return structured errors and never treat client validation as security.
- **Strings:** normalize, truncate, slugify, and pluralize without embedding feature copy.
- **URLs:** use `URL` and `URLSearchParams`; allowlist protocols and never concatenate untrusted redirect targets.
- **Storage:** provide typed, versioned access with parsing, SSR guards, and failure handling; never store secrets or authoritative data.
- **Theme:** map semantic tokens and theme identifiers without manipulating component styles directly.

## Constants

Colocate feature constants under `app/(dashboard)/<route>/_components/` or route-adjacent modules in the current implementation. A `features/<feature>/constants.ts` layout is a target convention for greenfield modules. Put only cross-feature values in the root `constants/` directory. Use immutable objects with `as const` where literal unions are useful. Avoid numeric or string literals whose meaning is not evident.

## API and backend integration

Define backend-facing DTOs and runtime schemas at feature boundaries. Map DTOs to UI models rather than leaking transport shape across components. Centralize authentication headers, request IDs, error normalization, and base URLs in the API adapter. This allows mocked implementations to be replaced by TanStack Query-backed endpoints without rewriting presentation components.

## Quality

Utilities must avoid hidden global state and browser assumptions unless named as browser adapters. Cover boundary values, invalid input, locale behavior, and security-sensitive URL/storage cases with unit tests.

