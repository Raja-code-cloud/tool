# Dependency Report — Cloud Content Hub Frontend RC Audit

**Audit date:** 2026-08-03  
**Commit:** `172fcc4f87a4bf0853c9e34f0585978a4a28f4a6`  
**Scope:** Root `package.json` / `package-lock.json`

---

## Executive Summary

| Metric | Result |
| ------ | ------ |
| Production dependencies | 24 |
| Development dependencies | 33 |
| Package manager | npm 10.9.2 |
| Lock file | `package-lock.json` present |
| Peer dependency errors | None reported |
| Security vulnerabilities (`npm audit`) | **5** (2 moderate, 3 high) |
| License compatibility | **PASS** (MIT/Apache-2.0/ISC production set) |

---

## Production Dependencies

| Package | Declared | Purpose |
| ------- | -------- | ------- |
| `@hookform/resolvers` | ^3.9.1 | **Unused** — no imports in app/tests |
| `@radix-ui/react-avatar` | ^1.1.2 | User avatars |
| `@radix-ui/react-checkbox` | ^1.1.3 | Form controls |
| `@radix-ui/react-dialog` | ^1.1.4 | Modals |
| `@radix-ui/react-dropdown-menu` | ^2.1.4 | Menus |
| `@radix-ui/react-label` | ^2.1.1 | Accessible labels |
| `@radix-ui/react-radio-group` | ^1.2.2 | Radio inputs |
| `@radix-ui/react-select` | ^2.1.4 | Select dropdowns |
| `@radix-ui/react-slot` | ^1.1.1 | Composition |
| `@radix-ui/react-switch` | ^1.1.2 | Toggles |
| `@radix-ui/react-toast` | ^1.2.4 | Notifications |
| `class-variance-authority` | ^0.7.1 | Variant styling |
| `clsx` | ^2.1.1 | Class merging |
| `framer-motion` | ^11.15.0 | Animations |
| `lucide-react` | ^0.469.0 | Icons |
| `next` | ^15.1.0 | Framework (resolved 15.5.22) |
| `react` | ^19.0.0 | UI runtime |
| `react-day-picker` | ^9.5.0 | Calendar/date |
| `react-dom` | ^19.0.0 | DOM renderer |
| `react-dropzone` | ^14.3.5 | File upload |
| `react-hook-form` | ^7.54.2 | **Unused** — no imports in app/tests |
| `react-hook-form` pair | — | Forms use custom `FormField` pattern |
| `recharts` | ^2.15.0 | Analytics charts |
| `tailwind-merge` | ^2.6.0 | Class merge helper |
| `zod` | ^3.24.1 | Env validation |

---

## Development Dependencies

| Category | Packages |
| -------- | -------- |
| Testing | vitest, @vitest/coverage-v8, @testing-library/*, jsdom, msw, vitest-axe, @axe-core/playwright, @playwright/test |
| Storybook | storybook, @storybook/nextjs-vite, addon-a11y/docs/themes |
| Linting / types | eslint, eslint-config-next, @eslint/eslintrc, typescript, @types/* |
| Formatting | prettier, @ianvs/prettier-plugin-sort-imports, prettier-plugin-tailwindcss |
| Git hooks | husky, lint-staged, @commitlint/* |
| Build | @vitejs/plugin-react, @tailwindcss/postcss, tailwindcss, tw-animate-css |

---

## Unused Packages

| Package | Evidence | Recommendation |
| ------- | -------- | -------------- |
| `react-hook-form` | Zero imports in `app/`, `components/`, `hooks/`, `lib/`, `tests/` | Remove |
| `@hookform/resolvers` | No `zodResolver` usage | Remove |

**Note:** A prior audit (2026-08-02) documented removal; packages are **present again** in current `package.json`.

### Depcheck false positives (retain)

| Package | Actual usage |
| ------- | ------------ |
| `tailwindcss`, `@tailwindcss/postcss` | PostCSS pipeline |
| `tw-animate-css` | CSS import in `styles/globals.css` |
| `eslint-config-next` | `eslint.config.mjs` |
| `@storybook/addon-*` | `.storybook/main.ts` |
| `@commitlint/*` | Husky hooks |
| Prettier plugins | `prettier.config.mjs` |

---

## Duplicate Packages

Normal npm deduplication; notable duplicates:

| Package | Versions | Risk |
| ------- | -------- | ---- |
| `postcss` | 8.5.x (root) + 8.4.31 (Next internal) | **Medium** — audit flags XSS advisory on older pin |
| `sharp` | 0.35.x (override) + <0.35.0 (Next internal) | **High** — libvips CVEs in Next-bundled copy |
| `react-is` | 16.x–18.x (Recharts transitive) | Low |

**Mitigation:** Documented overrides for `postcss >=8.5.18` and `sharp >=0.35.0` in prior audits; verify they remain effective in current lockfile after clean install.

---

## Outdated Packages

All direct dependencies at semver **wanted** within declared ranges. Major upgrades available:

| Package | Installed | Latest major | Notes |
| ------- | --------- | ------------ | ----- |
| `next` | 15.5.22 | 16.2.12 | Coordinate with eslint-config-next |
| `eslint` | 9.39.5 | 10.8.0 | Flat config migration |
| `framer-motion` | 11.18.2 | 12.43.0 | Animation audit required |
| `recharts` | 2.15.4 | 3.10.1 | Chart API breaking |
| `zod` | 3.25.76 | 4.4.3 | Schema migration |
| `lucide-react` | 0.469.0 | 1.28.0 | Icon export changes |
| `tailwind-merge` | 2.6.1 | 3.6.0 | Tailwind v4 alignment |
| `react-day-picker` | 9.14.0 | 10.0.1 | Calendar API |
| `react-dropzone` | 14.4.1 | 20.0.0 | Upload wizard impact |
| `@types/node` | 22.20.1 | 26.1.2 | Align with Node LTS |
| `typescript` | 5.9.3 | 7.0.2 | Stay on TS 5.x for Next.js |

---

## Security Vulnerabilities

**`npm audit` result (2026-08-03 audit host):**

```
5 vulnerabilities (2 moderate, 3 high)
```

| Advisory area | Severity | Package | Notes |
| ------------- | -------- | ------- | ----- |
| PostCSS XSS via unescaped `</style>` | moderate/high | `postcss` (transitive via `next`) | GHSA-qx2v-qp2m-jg93 |
| sharp/libvips CVEs | high | `sharp <0.35.0` in `next/node_modules/sharp` | GHSA-f88m-g3jw-g9cj |
| Storybook/Next chain | moderate | `@storybook/nextjs-vite` via `next` | Dev-only |

**Fix availability:** `npm audit fix` partial; some issues require dependency upgrades or override verification.

### CI gap

Frontend `npm audit` is **not** in scheduled security workflow (backend-only `pip-audit`/Trivy). Recommend adding `npm audit --omit=dev --audit-level=high` to CI.

---

## License Concerns

| Assessment | Result |
| ---------- | ------ |
| Production licenses | MIT (majority), Apache-2.0 (CVA), ISC (lucide-react) |
| Copyleft (GPL/AGPL) in production set | **None found** |
| Distribution model | `"private": true` |
| **Overall** | **PASS** |

See `docs/frontend/LICENSE_REPORT.md` for full matrix.

### Package metadata gaps

| Field | Status |
| ----- | ------ |
| `repository` | Missing (KI-004) |
| `license` | Missing (KI-004) |
| `author` | Missing (KI-004) |

---

## Bundle-Heavy Dependencies

| Package | Mitigation |
| ------- | ---------- |
| `lucide-react` | `optimizePackageImports` in `next.config.ts` |
| `recharts` | Same + route-level splitting on `/analytics` |
| `framer-motion` | Same; used across dashboard routes |
| `react-day-picker` | Scoped to calendar/scheduler |
| `react-dropzone` | Scoped to upload wizard |

---

## Recommendations

| Priority | Action |
| -------- | ------ |
| P0 | Clean `npm ci` on Node 22.22.1; re-run `npm audit`; confirm overrides |
| P0 | Resolve high-severity `sharp`/`postcss` transitives before production |
| P1 | Remove unused `react-hook-form` and `@hookform/resolvers` |
| P1 | Add frontend audit step to CI |
| P2 | Plan coordinated major upgrades (Next 16, recharts 3) post-RC |
| P2 | Add `repository`, `license`, `author` to `package.json` |

---

*Generated by Release Audit Engineer — dependency tree not modified during audit.*
