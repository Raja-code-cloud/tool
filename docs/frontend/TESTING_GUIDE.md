# Frontend testing guide

This guide describes the Cloud Content Hub AI frontend test stack, folder layout, and workflows. The implementation is the source of truth; run commands from the repository root after `npm ci`.

## Testing philosophy

Tests protect the mock-backed workspace UI without requiring a live backend. The pyramid is:

1. **Unit tests** — pure utilities, hooks, and isolated components.
2. **Integration tests** — feature workflows, provider composition, and MSW-backed HTTP boundaries.
3. **End-to-end tests** — real browser flows via Playwright (local and optional CI job).

Accessibility checks run at unit/integration layers (`vitest-axe`) and in Playwright (`@axe-core/playwright`). CI enforces Vitest on every pull request and `main` push; Playwright is configured locally but not yet part of the core GitHub Actions pipelines.

## Folder structure

```text
tests/
  unit/              # Fast, isolated tests (utils, hooks, components, lib)
  integration/       # Multi-module workflows and MSW foundation tests
  e2e/               # Playwright browser specs
  mocks/             # MSW server, handlers, and browser worker setup
  setup/             # Vitest global setup (MSW, DOM mocks, axe matchers)
  fixtures/          # Shared route constants and test data
  utils/             # renderWithProviders, axe helpers, router utilities
vitest.config.ts     # Vitest + coverage configuration
playwright.config.ts # Playwright projects and dev-server wiring
.storybook/          # Storybook 10 (component isolation; not a test runner)
stories/             # 11 Storybook story modules
```

Feature code lives under `app/(dashboard)/*/_components/`; tests import from `@/` aliases rather than colocating beside every component.

## Unit tests

**Location:** `tests/unit/`

**Scope:** Formatting helpers, navigation utilities, service contracts against mocks, hook state, and shared components (buttons, forms, navigation, feedback, etc.).

**Run:**

```sh
npm run test:run -- tests/unit
```

**Patterns:**

- Import from `@/tests/utils` for `renderWithProviders`, `userEvent`, and axe helpers.
- Vitest globals are configured via `vitest.config.ts`; setup runs from `tests/setup/vitest.setup.ts`.
- Browser APIs (`matchMedia`, `ResizeObserver`, clipboard) are stubbed in `tests/setup/browser.ts`.

## Integration tests

**Location:** `tests/integration/`

**Scope:** End-to-end feature workflows within jsdom — dashboard, content library, upload wizard, scheduler, analytics, AI studio, settings, accessibility compositions, and MSW handler registration.

**Run:**

```sh
npm run test:run -- tests/integration
```

Integration tests exercise services → hooks → views using mock repositories; they do not call a real API.

## Playwright (E2E)

**Location:** `tests/e2e/`

**Specs:** `foundation.spec.ts`, `routes.spec.ts`, `responsive.spec.ts`, `accessibility.spec.ts`, `user-journeys.spec.ts`

**Configuration:** `playwright.config.ts` starts `npm run dev` on `http://127.0.0.1:3000` unless `PLAYWRIGHT_BASE_URL` is set.

**Run:**

```sh
npm run test:e2e:install   # first-time Chromium install
npm run test:e2e
npm run test:e2e:ui        # interactive UI mode
```

**CI behavior:** Playwright is **not** executed in `.github/workflows/ci.yml` or `build.yml` today. Treat Linux CI Vitest results as the release gate; run Playwright locally before large UI changes.

## MSW (Mock Service Worker)

**Files:**

- `tests/mocks/handlers.ts` — default handler list (empty; extend per feature)
- `tests/mocks/server.ts` — Node server via `setupServer`
- `tests/mocks/browser.ts` — browser worker export for future use

**Setup:** `tests/setup/vitest.setup.ts` calls `server.listen({ onUnhandledRequest: "error" })` so unexpected network calls fail tests.

**Mock strategy:**

- Register feature-specific handlers with `server.use(http.get(...))` inside the test or `beforeEach`.
- Keep global handlers minimal; prefer explicit per-test overrides.
- Production code continues to use mock repositories until `NEXT_PUBLIC_API_BASE_URL` activates HTTP adapters.

See `tests/integration/msw-foundation.test.ts` for the reference pattern.

## Accessibility testing

| Layer        | Tool                   | Location                                                         |
| ------------ | ---------------------- | ---------------------------------------------------------------- |
| Unit/integr. | `vitest-axe`           | `tests/utils/axe.ts`, `tests/integration/accessibility.test.tsx` |
| E2E          | `@axe-core/playwright` | `tests/e2e/accessibility.spec.ts`                                |
| Manual       | Storybook a11y addon   | `npm run storybook` (not CI-gated)                               |

`expectNoCriticalViolations(container)` filters **critical** and **serious** axe violations. Route-level WCAG compliance still requires manual keyboard and screen-reader review.

## Coverage strategy

**Command:**

```sh
npm run test:coverage
```

**Output:** `coverage/` (text, HTML, lcov, json-summary)

**Included paths:** `components/**`, `hooks/**`, `lib/utils/**`

**Thresholds** (enforced when coverage runs with `--coverage`):

| Metric     | Minimum |
| ---------- | ------- |
| Lines      | 80%     |
| Statements | 80%     |
| Functions  | 80%     |
| Branches   | 75%     |

Coverage is **not** enforced in CI pipelines today; thresholds apply when developers run `npm run test:coverage` locally.

## Running tests

| Command                 | Purpose                                    |
| ----------------------- | ------------------------------------------ |
| `npm run test`          | Vitest watch mode                          |
| `npm run test:run`      | Single CI-style Vitest run                 |
| `npm run test:coverage` | Vitest with v8 coverage                    |
| `npm run test:e2e`      | Playwright full suite                      |
| `npm run verify`        | format:check + typecheck + lint + test:run |

**Windows note:** The full Vitest suite can take several minutes on Windows (`pool: "forks"`, `maxWorkers: 1`). Linux CI (`ubuntu-latest`) is the authoritative timing environment.

## CI behavior

**Pull requests (`ci.yml`):** dependency review → `format:check` → `typecheck` → `lint` → `test:run` → `build`

**Main branch (`build.yml`):** quality job (format, typecheck, lint, test:run) → production build artifact upload

Pre-push hook (`.husky/pre-push`) runs `npm run verify` locally.

## Writing new tests

1. Place unit tests under `tests/unit/` mirroring the source area (`lib/`, `hooks/`, `components/`).
2. Add integration specs under `tests/integration/` for cross-module workflows.
3. Use `renderWithProviders` from `@/tests/utils` so theme, toast, and sidebar context match production.
4. For HTTP boundaries, add MSW handlers with `server.use()`; never rely on live network in unit/integration tests.
5. For new routes, extend `tests/fixtures/routes.ts` and add Playwright coverage when browser behavior matters.
6. Run `npm run verify` before opening a pull request.

## Storybook

Storybook 10 (`@storybook/nextjs-vite`) supports isolated component development with a11y, docs, and themes addons. It complements—not replaces—automated tests.

```sh
npm run storybook
npm run build-storybook
```

Eleven story modules live in `stories/`. Storybook builds are optional for release and are not part of CI today.

## Related documentation

- [Developer guide](../DEVELOPER_GUIDE.md)
- [CI/CD guide](./CI_CD_GUIDE.md)
- [Accessibility guide](./ACCESSIBILITY_GUIDE.md)
- [Environment setup](./ENVIRONMENT_SETUP.md)
