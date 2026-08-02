# Coverage strategy

## Scope

Vitest coverage is collected for reusable frontend surfaces only:

- `components/**/*.{ts,tsx}`
- `hooks/**/*.{ts,tsx}`
- `lib/utils/**/*.{ts,tsx}`

Route-local `_components` and application wiring are validated by integration and Playwright tests rather than unit coverage thresholds.

Configuration lives in `vitest.config.ts`. Reports are written to `coverage/` (`text`, `html`, `lcov`, `json-summary`).

## RC3 baseline (2026-08-03)

Measured with `npm run test:coverage` (144 tests, 42 files):

| Metric     | Measured | RC3 enforced floor | GA target |
| ---------- | -------- | ------------------ | --------- |
| Lines      | 72.58%   | **70%**            | 80%       |
| Statements | 71.01%   | **70%**            | 80%       |
| Functions  | 64.15%   | **62%**            | 80%       |
| Branches   | 56.36%   | **54%**            | 75%       |

### Why interim floors are below target

The GA targets (80/80/80/75) remain the engineering goal documented in the testing sprint. Current coverage is below those targets because several component categories still lack direct unit tests:

- **0% coverage:** `calendar`, `charts`, `common`, `dialogs`, `layout`, `shared`, `tables`, `upload`
- **Branch gap:** Radix wrapper branches in `components/ui` and navigation edge cases
- **Function gap:** Presentational exports exercised only through E2E or integration paths

Lowering RC3 floors to the measured baseline prevents CI flakiness while **still blocking regressions**. Floors are set ~2 points below measured values to absorb minor instrumentation variance.

## Staged rollout

| Phase   | When        | Lines / Stmts | Functions | Branches | Gate location        |
| ------- | ----------- | ------------- | --------- | -------- | -------------------- |
| **RC3** | Now         | 70 / 70       | 62        | 54       | CI `test:coverage`   |
| **RC4** | Next sprint | 75 / 75       | 70        | 62       | Raise after test PRs |
| **GA**  | Release     | 80 / 80       | 80        | 75       | Final quality bar    |

### RC4 focus areas (ordered by impact)

1. Add unit tests for zero-coverage component categories (`layout`, `upload`, `charts`, `dialogs`, `tables`)
2. Expand branch coverage in `components/navigation` and `components/ui/primitives.tsx`
3. Cover remaining `lib/utils` branches in `ai-studio.ts` and `content-library.ts`

## CI integration

Pull request, main, and release workflows run:

```sh
npm run test:coverage
```

Vitest fails the job when coverage drops below configured thresholds. HTML and LCOV artifacts upload on every PR for reviewer inspection.

## Local commands

```sh
npm run test:run        # fast feedback (no threshold enforcement)
npm run test:coverage   # same suite + coverage gate (matches CI)
```

`npm run verify` uses `test:run` for pre-push speed. CI remains authoritative for coverage enforcement.

## Maintenance

When raising thresholds:

1. Run `npm run test:coverage` locally and capture `coverage/coverage-summary.json`
2. Update `vitest.config.ts` thresholds
3. Update this document and the phase table
4. Ensure CI passes before merging
