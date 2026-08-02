# Folder structure

```text
app/
  layout.tsx                 root metadata/providers
  page.tsx                   redirects / to /dashboard
  (dashboard)/
    layout.tsx               sidebar provider and workspace shell
    dashboard/               page plus route-local _components/
    content-library/         page plus route-local _components/
    upload/                  page plus route-local _components/
    ai-studio/               page plus route-local _components/
    scheduler/               page plus route-local _components/
    calendar/
    analytics/               page plus route-local _components/
    social-accounts/         page plus route-local _components/
    settings/                page plus route-local _components/
components/
  buttons/ calendar/ cards/ charts/ common/ dialogs/ feedback/
  filters/ forms/ layout/ navigation/ platform/ shared/
  tables/ theme/ ui/ upload/
constants/                     stable values and mock feature data
hooks/                         shared UI hooks and providers
lib/
  adapters/ config/ domain/ services/ utils/
  motion.ts
styles/
  globals.css
docs/
  frontend/
```

The parenthesized route group is organizational and absent from public URLs. Category folders under `components/` expose intentional public entry points. Domain-specific UI is colocated under each route's `_components/` directory; route `page.tsx` files remain thin composition layers.

Generated `.next/`, installed `node_modules/`, and deployment artifacts are not source. Frontend documentation is maintained in `docs/frontend/`.
