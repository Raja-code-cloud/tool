# Dependency Security

## RC2 findings (H-01)

The RC2 review identified high-severity vulnerabilities in transitive production dependencies:

| Package            | Advisory                                                      | Severity |
| ------------------ | ------------------------------------------------------------- | -------- |
| `postcss` ≤ 8.5.17 | GHSA-6g55-p6wh-862q, GHSA-r28c-9q8g-f849, GHSA-qx2v-qp2m-jg93 | High     |
| `sharp` < 0.35.0   | GHSA-f88m-g3jw-g9cj (libvips CVEs)                            | High     |

Both are pulled in by `next` for CSS processing and image optimization.

## Remediation applied

`package.json` includes npm **overrides** to force patched versions without downgrading Next.js:

```json
"overrides": {
  "postcss": "^8.5.18",
  "sharp": "^0.35.0"
}
```

After changing overrides, regenerate the lockfile:

```bash
npm install
npm audit --omit=dev
```

## Audit commands

```bash
# Production dependencies only (matches RC2 scope)
npm audit --omit=dev

# Full tree including devDependencies
npm audit
```

## CI recommendation

Add to the frontend CI pipeline:

```bash
npm audit --omit=dev --audit-level=high
```

Fail the build on new high or critical production vulnerabilities.

## Remaining risk

| Risk                                                                 | Mitigation                                     |
| -------------------------------------------------------------------- | ---------------------------------------------- |
| Future Next.js releases may pin vulnerable transitive versions again | Re-run `npm audit` on every dependency upgrade |
| `npm audit fix --force` suggests Next.js 9.x downgrade               | **Never use** — breaking and incorrect         |
| DevDependency vulnerabilities (Storybook, ESLint, etc.)              | Track separately; lower runtime exposure       |

## Unused packages

No packages were removed during this security sprint. Unused-package review is a maintenance task, not a vulnerability unless an unmaintained package with known CVEs is present.

## Upgrade policy

1. Prefer framework-supported dependency resolution (Next.js upgrades)
2. Use narrowly scoped `overrides` when the framework lags behind patched transitives
3. Run `npm run verify` (format, typecheck, lint, unit tests) after any override change
4. Run `npm run build` to validate image optimization (sharp) and CSS pipeline (postcss)
