# Git workflow

## Branches

Create a short-lived branch from an up-to-date `main`. Use a descriptive name,
such as `feat/content-search` or `fix/upload-validation`. Open a pull request;
do not push directly to `main`.

## Commits

Commit messages follow Conventional Commits:

```text
type(optional-scope): concise imperative summary
```

Common types are `feat`, `fix`, `docs`, `refactor`, `test`, `build`, `ci`,
`chore`, `style`, `perf`, and `revert`.

Examples:

```text
feat(search): add content type filtering
fix(upload): preserve filename extension
docs(workflow): explain local quality checks
```

The commit hook rejects non-conforming messages. Keep the header at or below
100 characters.

## Local hooks

- `pre-commit`: ESLint and Prettier run against staged files through lint-staged.
- `commit-msg`: commitlint validates the message.
- `pre-push`: the full local `verify` suite runs before Git sends commits.

Do not bypass hooks except to diagnose the hook itself. Fix failures and commit
the resulting staged-file changes.

## Before opening a pull request

```sh
npm run verify
npm run build
```

## Recommended `main` protection

Require pull requests, at least one approval, conversation resolution, linear
history, and the documented CI checks. Dismiss stale approvals after new commits,
block force pushes and deletion, include administrators, require branches to be
current before merge, and enable secret scanning plus push protection. Prefer
squash merge so the pull request title becomes the Conventional Commit entry.
