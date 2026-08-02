# Frontend License Report

**Project:** Cloud Content Hub AI  
**Report date:** 2026-08-02  
**Scope:** Direct production and development dependencies  
**Distribution model:** Private application (`"private": true`)

---

## Executive summary

All **direct production dependencies** use permissive open-source licenses compatible with a proprietary private SaaS application. No copyleft (GPL/AGPL) licenses were found in the production dependency set.

| License family | Production deps | Compatible |
| -------------- | --------------- | ---------- |
| MIT            | 20              | Yes        |
| Apache-2.0     | 1               | Yes        |
| ISC            | 1               | Yes        |

**Overall compatibility rating: PASS**

---

## Production dependency licenses

| Package                         | Version | License    | Risk |
| ------------------------------- | ------- | ---------- | ---- |
| `@radix-ui/react-avatar`        | 1.1.x   | MIT        | None |
| `@radix-ui/react-checkbox`      | 1.1.x   | MIT        | None |
| `@radix-ui/react-dialog`        | 1.1.x   | MIT        | None |
| `@radix-ui/react-dropdown-menu` | 2.1.x   | MIT        | None |
| `@radix-ui/react-label`         | 2.1.x   | MIT        | None |
| `@radix-ui/react-radio-group`   | 1.2.x   | MIT        | None |
| `@radix-ui/react-select`        | 2.1.x   | MIT        | None |
| `@radix-ui/react-slot`          | 1.1.x   | MIT        | None |
| `@radix-ui/react-switch`        | 1.1.x   | MIT        | None |
| `@radix-ui/react-toast`         | 1.2.x   | MIT        | None |
| `class-variance-authority`      | 0.7.1   | Apache-2.0 | None |
| `clsx`                          | 2.1.1   | MIT        | None |
| `framer-motion`                 | 11.18.x | MIT        | None |
| `lucide-react`                  | 0.469.x | ISC        | None |
| `next`                          | 15.5.22 | MIT        | None |
| `react`                         | 19.2.8  | MIT        | None |
| `react-day-picker`              | 9.14.x  | MIT        | None |
| `react-dom`                     | 19.2.8  | MIT        | None |
| `react-dropzone`                | 14.4.x  | MIT        | None |
| `recharts`                      | 2.15.x  | MIT        | None |
| `tailwind-merge`                | 2.6.x   | MIT        | None |
| `zod`                           | 3.25.x  | MIT        | None |

### Removed packages (no longer in tree)

| Package               | License | Removed          |
| --------------------- | ------- | ---------------- |
| `react-hook-form`     | MIT     | 2026-08-02 audit |
| `@hookform/resolvers` | MIT     | 2026-08-02 audit |

---

## Development dependency licenses

Development dependencies are not shipped in the production bundle but are included for completeness and CI compliance review.

| Package                               | Typical license | Shipped to users                  |
| ------------------------------------- | --------------- | --------------------------------- |
| `@commitlint/cli`                     | MIT             | No                                |
| `@commitlint/config-conventional`     | MIT             | No                                |
| `@eslint/eslintrc`                    | MIT             | No                                |
| `@ianvs/prettier-plugin-sort-imports` | Apache-2.0      | No                                |
| `@playwright/test`                    | Apache-2.0      | No                                |
| `@storybook/*`                        | MIT             | No (Storybook static is internal) |
| `@tailwindcss/postcss`                | MIT             | No (build-time only)              |
| `@testing-library/*`                  | MIT             | No                                |
| `@types/*`                            | MIT             | No (types stripped at build)      |
| `@vitejs/plugin-react`                | MIT             | No                                |
| `@vitest/coverage-v8`                 | MIT             | No                                |
| `eslint`                              | MIT             | No                                |
| `eslint-config-next`                  | MIT             | No                                |
| `husky`                               | MIT             | No                                |
| `jsdom`                               | MIT             | No                                |
| `lint-staged`                         | MIT             | No                                |
| `msw`                                 | MIT             | No                                |
| `prettier`                            | MIT             | No                                |
| `prettier-plugin-tailwindcss`         | MIT             | No                                |
| `storybook`                           | MIT             | No                                |
| `tailwindcss`                         | MIT             | No                                |
| `tw-animate-css`                      | MIT             | No                                |
| `typescript`                          | Apache-2.0      | No                                |
| `vitest`                              | MIT             | No                                |

---

## License compatibility analysis

### MIT / ISC / Apache-2.0 (permissive)

All production dependencies fall into this category. These licenses allow:

- Private use and modification
- Commercial distribution
- Combination with proprietary code

**Requirements:**

| License    | Attribution               | Notice file           | Patent grant |
| ---------- | ------------------------- | --------------------- | ------------ |
| MIT        | Required in distributions | Recommended           | Implicit     |
| ISC        | Required in distributions | Recommended           | Implicit     |
| Apache-2.0 | Required                  | **Required** (NOTICE) | Explicit     |

### Copyleft (GPL/AGPL/LGPL)

**None detected** in direct production dependencies.

### Weak copyleft (MPL/EPL/CDDL)

No direct production dependencies use weak copyleft licenses. Transitive packages were not exhaustively scanned; run `npx license-checker --production --summary` before external distribution if policy requires full transitive audit.

---

## Notable license considerations

### `class-variance-authority` (Apache-2.0)

Apache-2.0 requires preservation of copyright, license, and NOTICE files when redistributing **source or binary**. For a private SaaS where the library is bundled but not separately distributed, standard npm usage is compliant. If open-sourcing portions of the frontend, include Apache-2.0 attribution for this package.

### `lucide-react` (ISC)

Functionally equivalent to MIT for commercial use. Attribution required if redistributing source.

### `next` / `react` (MIT)

Meta (Next.js) and Meta/Open-source community (React) MIT licenses. Standard attribution applies for source distributions.

### Radix UI (MIT)

WorkOS-backed MIT components. No additional attribution beyond standard MIT requirements.

---

## Bundle vs. license exposure

Next.js production builds tree-shake and minify dependencies into server/client bundles. License obligations for permissive licenses in bundled SaaS deployments typically require:

1. **Internal/private deployment:** No additional action beyond maintaining `package-lock.json` audit trail.
2. **Customer-facing source distribution:** Include a `THIRD-PARTY-NOTICES` file aggregating MIT/ISC/Apache attributions.
3. **Mobile/desktop wrapper distribution:** Same as (2); consult legal for store submission requirements.

---

## Compliance checklist

| Item                                      | Status                                      |
| ----------------------------------------- | ------------------------------------------- |
| No GPL/AGPL in production deps            | Pass                                        |
| All production deps permissively licensed | Pass                                        |
| Private package flag set                  | Pass (`"private": true`)                    |
| Lockfile committed for reproducibility    | Pass                                        |
| SBOM generation in CI                     | Partial (backend container only)            |
| THIRD-PARTY-NOTICES file                  | Not present (not required for private SaaS) |

---

## Recommendations

1. **Before any public/open-source release:** Generate a full transitive license report with `npx license-checker --production --csv > licenses.csv` and produce a `THIRD-PARTY-NOTICES` file.
2. **CI enhancement:** Add a license allowlist check (e.g., `license-checker --onlyAllow "MIT;ISC;Apache-2.0;BSD-2-Clause;BSD-3-Clause"`) on PRs that modify `package-lock.json`.
3. **Dependabot:** Current weekly npm updates should include license change review via dependency-review-action (already enabled in CI).

---

## Audit trail

| Event                                                    | Date       | Action                                        |
| -------------------------------------------------------- | ---------- | --------------------------------------------- |
| Removed unused `react-hook-form` / `@hookform/resolvers` | 2026-08-02 | Reduced license surface (both MIT)            |
| Lockfile refresh                                         | 2026-08-02 | `npm update` within semver ranges             |
| License extraction method                                | 2026-08-02 | Direct deps from `package-lock.json` metadata |

---

## Related documents

- [DEPENDENCY_AUDIT.md](./DEPENDENCY_AUDIT.md) — Full dependency audit
- [PACKAGE_HEALTH.md](./PACKAGE_HEALTH.md) — Stack version health
- [DEPENDENCY_SECURITY.md](./DEPENDENCY_SECURITY.md) — Security overrides and audit policy
