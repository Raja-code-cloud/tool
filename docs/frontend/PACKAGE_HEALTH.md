# Frontend Package Health Report

**Project:** Cloud Content Hub AI  
**Report date:** 2026-08-02  
**Node requirement:** `>=22.22.1` (see `.nvmrc`, CI `NODE_VERSION`)

---

## Stack health overview

| Category             | Health     | Summary                                           |
| -------------------- | ---------- | ------------------------------------------------- |
| Core framework       | **Green**  | Next.js 15.5 + React 19 — current stable pairing  |
| Styling              | **Green**  | Tailwind CSS v4 with PostCSS 4 plugin             |
| UI primitives        | **Green**  | Radix UI — modular, per-component imports         |
| Animation            | **Yellow** | framer-motion v11 stable; v12 available           |
| Charts               | **Yellow** | recharts v2 stable; v3 available                  |
| Testing              | **Green**  | Vitest 4 + Testing Library 16 + Playwright 1.62   |
| Storybook            | **Green**  | Storybook 10 with Next.js Vite framework          |
| Linting / types      | **Green**  | ESLint 9 flat config + TypeScript 5.9 strict mode |
| Security transitives | **Green**  | postcss/sharp overrides active, 0 audit findings  |

---

## Core stack versions

| Package        | Declared  | Installed | Latest  | Status             |
| -------------- | --------- | --------- | ------- | ------------------ |
| **Next.js**    | `^15.1.0` | 15.5.22   | 16.2.12 | Current within v15 |
| **React**      | `^19.0.0` | 19.2.8    | 19.2.8  | Up to date         |
| **React DOM**  | `^19.0.0` | 19.2.8    | 19.2.8  | Up to date         |
| **TypeScript** | `^5.7.0`  | 5.9.3     | 7.0.2   | Current within v5  |

### Next.js

- **Version:** 15.5.22
- **Config:** App Router, `reactStrictMode`, security headers, `optimizePackageImports`
- **Build:** 13 static routes, shared JS 103 kB
- **Major upgrade path (v16):** Coordinate with `eslint-config-next@16`, review breaking changes in Next.js 16 release notes, re-run full E2E suite. **Do not upgrade until planned.**

### React

- **Version:** 19.2.8
- **Compatibility:** Aligned with Next.js 15.5 and Radix UI 1.x/2.x
- **Strict mode:** Enabled in `next.config.ts`

---

## Styling stack

| Package                      | Declared | Installed | Latest | Status       |
| ---------------------------- | -------- | --------- | ------ | ------------ |
| **tailwindcss**              | `^4.0.0` | 4.3.3     | 4.3.3  | Up to date   |
| **@tailwindcss/postcss**     | `^4.0.0` | 4.3.3     | 4.3.3  | Up to date   |
| **tailwind-merge**           | `^2.6.0` | 2.6.1     | 3.6.0  | v3 available |
| **tw-animate-css**           | `^1.4.0` | 1.4.0     | 1.4.0  | Up to date   |
| **class-variance-authority** | `^0.7.1` | 0.7.1     | 0.7.1  | Up to date   |
| **clsx**                     | `^2.1.1` | 2.1.1     | 2.1.1  | Up to date   |

### Tailwind CSS v4

- CSS-first configuration in `styles/globals.css` via `@theme`
- PostCSS pipeline: `@tailwindcss/postcss` in `postcss.config.mjs`
- Prettier integration: `prettier-plugin-tailwindcss` with `tailwindFunctions: ["clsx", "cn", "cva"]`

**Upgrade note:** `tailwind-merge@3` targets Tailwind v4 native APIs. Evaluate when adopting new merge utilities; test `cn()` helper across all variant combinations.

---

## Radix UI

All Radix packages are **modular per-primitive imports** — optimal for tree-shaking.

| Package                         | Installed | Usage                 |
| ------------------------------- | --------- | --------------------- |
| `@radix-ui/react-avatar`        | 1.1.x     | User avatars          |
| `@radix-ui/react-checkbox`      | 1.1.x     | Form controls         |
| `@radix-ui/react-dialog`        | 1.1.x     | Modal dialogs         |
| `@radix-ui/react-dropdown-menu` | 2.1.x     | Context menus         |
| `@radix-ui/react-label`         | 2.1.x     | Accessible labels     |
| `@radix-ui/react-radio-group`   | 1.2.x     | Radio inputs          |
| `@radix-ui/react-select`        | 2.1.x     | Select dropdowns      |
| `@radix-ui/react-slot`          | 1.1.x     | Composition primitive |
| `@radix-ui/react-switch`        | 1.1.x     | Toggle switches       |
| `@radix-ui/react-toast`         | 1.2.x     | Toast notifications   |

**Health:** All packages on current minor/patch within declared ranges. No peer conflicts with React 19.

---

## Storybook

| Package                   | Installed | Status  |
| ------------------------- | --------- | ------- |
| `storybook`               | 10.5.5    | Current |
| `@storybook/nextjs-vite`  | 10.5.5    | Current |
| `@storybook/addon-a11y`   | 10.5.5    | Current |
| `@storybook/addon-docs`   | 10.5.5    | Current |
| `@storybook/addon-themes` | 10.5.5    | Current |

- **Framework:** `@storybook/nextjs-vite` (Vite-powered, aligned with Vitest toolchain)
- **Stories:** 11 story files under `stories/`
- **Addons:** Accessibility, docs, and theme switching enabled
- **Type imports:** `@storybook/react` resolved transitively (consider adding as explicit devDependency for clearer peer resolution)

**Validation:** `npm run build-storybook` recommended before release (not run in this audit due to scope).

---

## Vitest

| Package                       | Installed | Status               |
| ----------------------------- | --------- | -------------------- |
| `vitest`                      | 4.1.10    | Current              |
| `@vitest/coverage-v8`         | 4.1.10    | Current              |
| `@vitejs/plugin-react`        | 6.0.5     | Current              |
| `jsdom`                       | 27.4.0    | Current within range |
| `@testing-library/react`      | 16.3.2    | Current              |
| `@testing-library/jest-dom`   | 7.0.0     | Current              |
| `@testing-library/user-event` | 14.6.1    | Current              |
| `msw`                         | 2.12.7    | Current              |

- **Config:** `vitest.config.ts` — jsdom environment, MSW integration tests
- **Coverage:** v8 provider, thresholds at 0% (baseline mode)
- **Test result:** 13 tests passing across 3 files

---

## Playwright

| Package            | Installed | Status  |
| ------------------ | --------- | ------- |
| `@playwright/test` | 1.62.1    | Current |

- **Config:** `playwright.config.ts` — Chromium desktop, dev server auto-start
- **E2E directory:** `tests/e2e/`
- **CI behavior:** 2 retries, 1 worker, trace on first retry

**Validation:** E2E not run in this audit (requires dev server lifecycle).

---

## ESLint

| Package              | Installed | Status               |
| -------------------- | --------- | -------------------- |
| `eslint`             | 9.39.5    | Current within v9    |
| `eslint-config-next` | 15.5.22   | Aligned with Next.js |
| `@eslint/eslintrc`   | 3.3.x     | FlatCompat bridge    |

- **Config:** Flat config via `eslint.config.mjs`
- **Extends:** `next/core-web-vitals`, `next/typescript`
- **Policy:** `--max-warnings=0`

**Major upgrade note:** ESLint 10 requires migration review of flat config and plugin compatibility. Defer until Next.js ecosystem publishes ESLint 10 guidance.

---

## TypeScript

| Package            | Installed | Status                |
| ------------------ | --------- | --------------------- |
| `typescript`       | 5.9.3     | Current within v5     |
| `@types/node`      | 22.20.1   | Aligned with Node 22  |
| `@types/react`     | 19.x      | Aligned with React 19 |
| `@types/react-dom` | 19.x      | Aligned with React 19 |

### Strict compiler options (tsconfig.json)

- `strict`, `exactOptionalPropertyTypes`, `noUncheckedIndexedAccess`
- `noUnusedLocals`, `noUnusedParameters`, `noImplicitOverride`
- `moduleResolution: bundler`, `jsx: preserve`

**Major upgrade note:** TypeScript 7 is in preview/early release. Stay on TS 5.x until Next.js and ESLint officially support TS 7.

---

## Feature libraries

| Package            | Installed | Latest major | Health                                   |
| ------------------ | --------- | ------------ | ---------------------------------------- |
| `framer-motion`    | 11.18.2   | 12.43.0      | Stable; v12 migration planned separately |
| `recharts`         | 2.15.4    | 3.10.1       | Stable; v3 has API changes               |
| `lucide-react`     | 0.469.0   | 1.28.0       | Pinned icon set; v1 re-exports           |
| `react-day-picker` | 9.14.0    | 10.0.1       | Stable for scheduler                     |
| `react-dropzone`   | 14.4.1    | 20.0.0       | Stable for upload wizard                 |
| `zod`              | 3.25.76   | 4.4.3        | Used for env/config validation           |

---

## Dev tooling

| Package                               | Installed | Status                          |
| ------------------------------------- | --------- | ------------------------------- |
| `husky`                               | 9.1.7     | Active via `prepare` script     |
| `lint-staged`                         | 17.3.0    | Active via config               |
| `@commitlint/cli`                     | 21.2.1    | Conventional commits            |
| `prettier`                            | 3.9.6     | Current                         |
| `@ianvs/prettier-plugin-sort-imports` | 4.7.1     | Import ordering                 |
| `prettier-plugin-tailwindcss`         | 0.7.4     | Class sorting (0.8.1 available) |

---

## Security overrides

```json
"overrides": {
  "postcss": ">=8.5.18",
  "sharp": ">=0.35.0"
}
```

| Override  | Resolved | Purpose                                    |
| --------- | -------- | ------------------------------------------ |
| `postcss` | 8.5.25   | Patches GHSA advisories in CSS pipeline    |
| `sharp`   | 0.35.3   | Patches libvips CVEs in image optimization |

Re-run `npm audit --omit=dev` after every Next.js upgrade.

---

## Automation health

| Mechanism                    | Status      | Detail                                         |
| ---------------------------- | ----------- | ---------------------------------------------- |
| Dependabot (npm)             | Active      | Weekly Monday, grouped prod/dev minor+patch    |
| Dependabot (GitHub Actions)  | Active      | Monthly                                        |
| CI dependency review         | Active      | `dependency-review-action` on PRs              |
| CI validate pipeline         | Active      | typecheck, format, lint, test, build           |
| Frontend security scan in CI | **Missing** | Only backend has scheduled `pip-audit` / Trivy |

---

## Recommended upgrade roadmap

### Tier 1 — Safe maintenance (next sprint)

- [ ] Add `npm audit --omit=dev --audit-level=high` to CI
- [ ] Evaluate `prettier-plugin-tailwindcss@0.8.x` in dev (format-only impact)
- [ ] Add `@storybook/react` as explicit devDependency for cleaner type resolution

### Tier 2 — Minor coordination (quarterly)

- [ ] `lucide-react@1.x` — verify icon name stability across codebase
- [ ] `tailwind-merge@3.x` — test `cn()` with all CVA variants
- [ ] `jsdom@29.x` — run full Vitest suite

### Tier 3 — Major upgrades (planned releases)

- [ ] **Next.js 16** + `eslint-config-next@16` — full regression + E2E
- [ ] **recharts 3** — analytics page visual QA
- [ ] **framer-motion 12** — animation timing audit across dashboard
- [ ] **zod 4** — schema migration for `lib/config/env.ts`
- [ ] **react-dropzone 20** — upload wizard integration tests
- [ ] **ESLint 10** — flat config plugin audit

---

## Node.js engine alignment

| Environment                     | Node version | Status                                  |
| ------------------------------- | ------------ | --------------------------------------- |
| `package.json` engines          | `>=22.22.1`  | Declared                                |
| CI (`.github/workflows/ci.yml`) | 22.22.1      | Aligned                                 |
| Audit environment               | 22.13.1      | **Below minimum** — EBADENGINE warnings |

Ensure local developers and CI use Node 22.22.1+ (`.nvmrc`) to avoid engine warnings from `lint-staged@17`.
