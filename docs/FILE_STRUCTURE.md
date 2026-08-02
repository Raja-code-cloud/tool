# File Structure

```text
app/
  (auth)/
  (dashboard)/
  api/
  layout.tsx
  loading.tsx
  error.tsx
components/
  ui/
  layout/
  navigation/
  buttons/
  cards/
  forms/
  tables/
  charts/
  upload/
  analytics/
  feedback/
  common/
features/
  <feature>/
    api/
    components/
    hooks/
    schemas/
    types/
    utils/
hooks/
lib/
  api/
  env/
  utils/
constants/
types/
public/
styles/
tests/
```

This is a target convention, not permission to reorganize an existing repository. Adopt folders incrementally and preserve established architecture.

## Placement rules

- `app`: routing, metadata, layouts, and route boundaries; keep business implementation thin.
- `components/ui`: owned shadcn primitives and variants.
- `components/*`: cross-feature compositions with demonstrated reuse.
- `features`: cohesive domain implementation.
- `hooks`: framework-level reusable hooks only.
- `lib`: infrastructure and dependency adapters.
- `constants`: shared stable values, grouped by domain.
- `types`: truly cross-domain types; prefer feature colocation.

Tests and stories should colocate with implementation unless project tooling requires dedicated directories. Static public files use stable kebab-case names.

## Environment configuration

Validate environment variables in one server-only module at startup. Expose browser-safe variables only with the `NEXT_PUBLIC_` prefix and a separate client schema. Commit `.env.example` with names and safe placeholders. Never commit credentials, log secrets, or read arbitrary `process.env` values throughout the codebase.

