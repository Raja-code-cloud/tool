# ESLint CLI migration plan

## Current state (RC3)

| Surface        | Command                                   | Notes                                  |
| -------------- | ----------------------------------------- | -------------------------------------- |
| `npm run lint` | `next lint`                               | Next.js wrapper around ESLint          |
| Pre-commit     | `eslint --fix --max-warnings=0`           | Direct ESLint via lint-staged          |
| Config         | `eslint.config.mjs`                       | ESLint 9 flat config with `FlatCompat` |
| Extends        | `next/core-web-vitals`, `next/typescript` | Via `eslint-config-next`               |

The repository already uses ESLint flat config. lint-staged invokes the ESLint CLI directly; only the npm `lint` script and CI lint step still call `next lint`.

## Why migrate

Next.js is deprecating `next lint` in favor of running ESLint directly. Benefits of switching now:

- **Parity:** Local hooks, CI, and editor all use the same ESLint entry point
- **Predictability:** No Next.js CLI indirection when ESLint or plugins upgrade
- **Future-proofing:** Ready for Next.js 16 where `next lint` removal is planned

## Target state

```json
{
  "scripts": {
    "lint": "eslint . --max-warnings=0",
    "lint:fix": "eslint . --fix --max-warnings=0"
  }
}
```

The transitional `lint:eslint` script added in RC3 mirrors the target command for side-by-side validation.

## Migration phases

### Phase 1 — RC3 (complete)

- [x] Flat config in `eslint.config.mjs`
- [x] lint-staged uses ESLint CLI
- [x] Add `lint:eslint` script identical to target command
- [x] Document migration plan (this file)

### Phase 2 — RC4 validation

Run both commands locally and in a CI matrix job until outputs match:

```sh
npm run lint
npm run lint:eslint
```

Resolve any path or ignore discrepancies. Common checks:

- `.next/`, `coverage/`, `storybook-static/` remain ignored
- App Router and `_components` directories are linted
- Zero-warning policy preserved

### Phase 3 — RC4 cutover

1. Change default `lint` script to `eslint . --max-warnings=0`
2. Remove `next lint` from CI (already uses `npm run lint`)
3. Update docs referencing `next lint`
4. Keep `eslint-config-next` — it supplies rules; only the runner changes

### Phase 4 — GA cleanup

- Remove transitional `lint:eslint` alias if redundant
- Re-evaluate `FlatCompat` when `eslint-config-next` ships native flat presets

## Rollback

If ESLint CLI surfaces unexpected rule differences:

1. Revert `lint` script to `next lint`
2. File issues for rule gaps
3. Retry cutover after `eslint-config-next` alignment

## References

- [Next.js ESLint documentation](https://nextjs.org/docs/app/api-reference/config/eslint)
- Repository config: `eslint.config.mjs`, `lint-staged.config.mjs`
- Code style: [CODE_STYLE.md](./CODE_STYLE.md)
