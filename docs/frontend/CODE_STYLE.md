# Frontend code style

## Automated rules

Prettier is the formatting authority and ESLint is the code-quality authority.
Do not hand-format around either tool.

```sh
npm run format
npm run format:check
npm run lint
npm run lint:fix
```

VS Code formats files and applies safe ESLint fixes on save. The pre-commit hook
runs the same tools only against staged files.

## TypeScript

- Keep strict typing enabled; do not weaken `tsconfig.json` to silence errors.
- Prefer explicit domain types over `any`.
- Use the `@/` alias for imports across top-level project areas.
- Keep imports at module scope.
- Use an exhaustive `never` check when switching over unions or enums.

## Imports

Prettier sorts imports in these groups: Node built-ins, external packages,
`@/` aliases, and relative imports. Do not also enable VS Code's organize-imports
action on save; competing sorters create noisy diffs.

## Tailwind CSS

The Prettier Tailwind plugin applies canonical class ordering, including classes
passed to `cn`, `clsx`, and `cva`. Follow the repository's existing token and
responsive conventions in `docs/TAILWIND_STANDARDS.md`.

## Markdown and line endings

Text files use UTF-8, LF line endings, two-space indentation, a final newline,
and no trailing whitespace. Markdown may retain intentional trailing spaces.
