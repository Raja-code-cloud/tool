# Frontend Dependency Audit

**Project:** Cloud Content Hub AI  
**Audit date:** 2026-08-02  
**Scope:** Root `package.json` (Next.js frontend)  
**Auditor role:** Senior Dependency Health Engineer

---

## Executive summary

The frontend dependency tree is in **good health**. After this audit:

| Metric                         | Result                |
| ------------------------------ | --------------------- |
| Direct production dependencies | 22 (down from 24)     |
| Direct dev dependencies        | 31                    |
| Total resolved packages        | 763                   |
| `npm audit` (full tree)        | **0 vulnerabilities** |
| `npm audit --omit=dev`         | **0 vulnerabilities** |
| Peer dependency errors         | **None**              |
| TypeScript / ESLint / Build    | **Pass**              |

Two unused production packages were removed. Lockfile dependencies were refreshed within existing semver ranges via `npm update`. No major-version upgrades were applied automatically.

Existing npm **overrides** for `postcss` (≥8.5.18) and `sharp` (≥0.35.0) remain in place and are effective (resolved: postcss 8.5.25, sharp 0.35.3).

---

## Audit methodology

1. Reviewed `package.json`, `package-lock.json`, `next.config.ts`, `tsconfig.json`, and `.github/` workflows.
2. Ran `depcheck`, `npm outdated`, `npm audit`, and `npm ls` for peer/duplicate analysis.
3. Cross-referenced imports across `app/`, `components/`, `hooks/`, `lib/`, `stories/`, and `tests/`.
4. Applied safe in-range updates and removed confirmed-unused production dependencies.
5. Validated with `npm install`, `npm run typecheck`, `npm run lint`, `npm run test:run`, and `npm run build`.

---

## Unused packages

### Removed (production)

| Package               | Reason                                                       |
| --------------------- | ------------------------------------------------------------ |
| `react-hook-form`     | No imports in application, test, or story code               |
| `@hookform/resolvers` | Paired with unused `react-hook-form`; no `zodResolver` usage |

These were listed in `SECURITY_REVIEW.md` as unused. Removal reduces install surface with zero functional impact.

### Retained (depcheck false positives)

Depcheck flagged several packages as unused because they are consumed indirectly:

| Package                                                              | Actual usage                               |
| -------------------------------------------------------------------- | ------------------------------------------ |
| `tailwindcss`, `@tailwindcss/postcss`                                | `postcss.config.mjs`, `styles/globals.css` |
| `tw-animate-css`                                                     | `@import` in `styles/globals.css`          |
| `eslint-config-next`                                                 | `eslint.config.mjs` via FlatCompat         |
| `@storybook/addon-*`                                                 | `.storybook/main.ts`                       |
| `@commitlint/*`                                                      | `commitlint.config.mjs`, Husky hooks       |
| `@ianvs/prettier-plugin-sort-imports`, `prettier-plugin-tailwindcss` | `prettier.config.mjs`                      |
| `lint-staged`                                                        | `lint-staged.config.mjs`                   |

### Transitive-only (documented, not added)

| Import             | Status                                                                                       |
| ------------------ | -------------------------------------------------------------------------------------------- |
| `@storybook/react` | Available transitively via `@storybook/nextjs-vite@10.5.5`; used for story type imports only |

---

## Duplicate packages

npm deduplication is normal for transitive dependencies. Notable duplicates in the lockfile (dev/transitive only):

| Package                                | Versions                                         | Risk                                                               |
| -------------------------------------- | ------------------------------------------------ | ------------------------------------------------------------------ |
| `postcss`                              | 8.5.25 (overridden) + 8.4.31 (Next internal pin) | **Low** — override ensures patched root; Next bundles its own copy |
| `react-is`                             | 16.x, 17.x, 18.x                                 | **Low** — Recharts transitive; no runtime conflict                 |
| `semver`, `ajv`, `eslint-visitor-keys` | 2 versions each                                  | **Low** — tooling transitive                                       |
| `@emnapi/*`                            | Multiple alpha/stable                            | **Low** — native binding internals                                 |

No direct-dependency duplication was found. Overrides for `postcss` and `sharp` intentionally unify security-sensitive transitives.

---

## Outdated packages

All direct dependencies are at their **semver `wanted`** version within declared ranges. Major upgrades available but **not applied**:

| Package                       | Installed | Latest major | Notes                                             |
| ----------------------------- | --------- | ------------ | ------------------------------------------------- |
| `next`                        | 15.5.22   | 16.2.12      | Requires coordinated `eslint-config-next` upgrade |
| `eslint`                      | 9.39.5    | 10.8.0       | Breaking flat-config changes expected             |
| `framer-motion`               | 11.18.2   | 12.43.0      | API/motion token changes                          |
| `recharts`                    | 2.15.4    | 3.10.1       | Chart API breaking changes                        |
| `zod`                         | 3.25.76   | 4.4.3        | Schema API changes                                |
| `lucide-react`                | 0.469.0   | 1.28.0       | Icon export changes                               |
| `tailwind-merge`              | 2.6.1     | 3.6.0        | Tailwind v4 alignment                             |
| `react-day-picker`            | 9.14.0    | 10.0.1       | Calendar API changes                              |
| `react-dropzone`              | 14.4.1    | 20.0.0       | Major API revision                                |
| `@types/node`                 | 22.20.1   | 26.1.2       | Align with Node LTS policy                        |
| `jsdom`                       | 27.4.0    | 29.1.1       | Test-only                                         |
| `prettier-plugin-tailwindcss` | 0.7.4     | 0.8.1        | Dev-only formatting                               |

See [PACKAGE_HEALTH.md](./PACKAGE_HEALTH.md) for stack-specific upgrade guidance.

---

## Deprecated packages

No **direct** dependencies are deprecated. Transitive deprecation warnings observed during tooling (`inflight`, `debuglog`, `osenv`, etc.) originate from dev-only audit tooling and do not affect production builds.

---

## Peer dependency issues

`npm ls` reports **no invalid or unmet peer dependencies** at the root.

Optional peer warnings (e.g. `conventional-commits-filter` in commitlint) are benign and do not affect builds.

---

## Bundle-heavy dependencies

| Package            | Usage                              | Mitigation                                            |
| ------------------ | ---------------------------------- | ----------------------------------------------------- |
| `framer-motion`    | 20+ dashboard/animation components | `optimizePackageImports` in `next.config.ts`          |
| `recharts`         | Analytics charts                   | `optimizePackageImports` + route-level code splitting |
| `lucide-react`     | Icons across all routes            | `optimizePackageImports` (tree-shaken per icon)       |
| `react-day-picker` | Calendar/scheduler                 | Route-scoped import in `components/calendar/`         |
| `react-dropzone`   | Upload wizard                      | Route-scoped import in upload flow                    |

**Production build baseline (post-audit):**

| Route                           | First Load JS |
| ------------------------------- | ------------- |
| Shared                          | 103 kB        |
| `/scheduler` (largest)          | 271 kB        |
| `/dashboard` (smallest feature) | 221 kB        |

---

## Tree-shaking opportunities

Already implemented:

```typescript
// next.config.ts
experimental: {
  optimizePackageImports: ["lucide-react", "recharts", "framer-motion"],
},
```

Additional opportunities (future, non-breaking):

1. **Recharts:** Import individual chart primitives instead of barrel exports where possible.
2. **Lucide:** Continue named icon imports (already the project convention).
3. **Framer Motion:** `MotionConfig` at shell level reduces duplicate feature detection; lazy-load motion on below-fold panels if bundle size becomes a concern.

---

## Security

### Vulnerabilities fixed

Prior RC2 high-severity issues in `postcss` and `sharp` were already remediated via npm overrides (documented in [DEPENDENCY_SECURITY.md](./DEPENDENCY_SECURITY.md)). This audit confirms:

- `postcss@8.5.25` — above patched floor (8.5.18)
- `sharp@0.35.3` — above patched floor (0.35.0)
- **0 open advisories** in full and production-only audits

### Upgrades applied (safe)

| Action                  | Detail                                                                  |
| ----------------------- | ----------------------------------------------------------------------- |
| `npm update`            | Refreshed lockfile within semver ranges (~10 direct/transitive updates) |
| Removed unused packages | 2 production packages (~2 fewer resolved deps)                          |

### CI / automation gaps

| Gap                                    | Recommendation                                                              |
| -------------------------------------- | --------------------------------------------------------------------------- |
| Frontend `npm audit` not in CI         | Add `npm audit --omit=dev --audit-level=high` to `.github/workflows/ci.yml` |
| Security scan workflow is backend-only | Extend or mirror for frontend on `package-lock.json` changes                |

---

## Changes made in this audit

### `package.json`

- Removed `@hookform/resolvers` and `react-hook-form`
- Fixed duplicate `overrides` key introduced during lockfile regeneration

### Lockfile

- Regenerated via `npm update` + `npm install`
- 763 packages (down from ~950 pre-update snapshot)

---

## Validation results

| Check               | Status                  |
| ------------------- | ----------------------- |
| `npm install`       | Pass                    |
| `npm run typecheck` | Pass                    |
| `npm run lint`      | Pass                    |
| `npm run test:run`  | Pass (13 tests)         |
| `npm run build`     | Pass (13 static routes) |

---

## Related documents

- [PACKAGE_HEALTH.md](./PACKAGE_HEALTH.md) — Stack version matrix and upgrade roadmap
- [LICENSE_REPORT.md](./LICENSE_REPORT.md) — License compatibility analysis
- [DEPENDENCY_SECURITY.md](./DEPENDENCY_SECURITY.md) — Prior security remediation (postcss/sharp overrides)
