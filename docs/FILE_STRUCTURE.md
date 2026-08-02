# File Structure

```text
app/
  (auth)/
  (dashboard)/
    <route>/
      page.tsx
      _components/     # current implementation: route-local feature UI
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
features/              # target convention; not used in current frontend
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
  config/
  domain/
  services/
  adapters/
  utils/
constants/
types/
public/
styles/
tests/
  unit/
  integration/
  e2e/
  mocks/
  setup/
  utils/
  fixtures/
.storybook/
stories/
```

This describes both the **current implementation** and target conventions. The live frontend colocates feature UI under `app/(dashboard)/*/_components/` rather than a top-level `features/` directory. Adopt new folders incrementally without reorganizing working code.

## Placement rules

- `app`: routing, metadata, layouts, and route boundaries; keep business implementation thin.
- `app/(dashboard)/*/_components/`: route-local feature views, hooks, and components (**current implementation**).
- `components/ui`: owned shadcn primitives and variants.
- `components/*`: cross-feature compositions with demonstrated reuse.
- `features/`: target convention for cohesive domain implementation; the current frontend colocates feature code under route `_components/` instead.
- `hooks`: framework-level reusable hooks only.
- `lib`: infrastructure and dependency adapters.
- `constants`: shared stable values, grouped by domain.
- `types`: truly cross-domain types; prefer feature colocation.

Tests and stories should colocate with implementation unless project tooling requires dedicated directories. Static public files use stable kebab-case names.

## Environment configuration

Validate environment variables in one server-only module at startup. Expose browser-safe variables only with the `NEXT_PUBLIC_` prefix and a separate client schema. Commit `.env.example` with names and safe placeholders. Never commit credentials, log secrets, or read arbitrary `process.env` values throughout the codebase.

