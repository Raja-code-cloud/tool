# Frontend developer workflow

## Daily loop

1. Update `main` and create a short-lived branch.
2. Install lockfile changes with `npm ci`.
3. Start the application with `npm run dev`.
4. Let VS Code and Prettier format changes on save.
5. Run focused checks while working, then `npm run verify`.
6. Run `npm run build` before opening a pull request when build behavior changed.
7. Commit with a Conventional Commit message and open a pull request.

## Quality gates

The workflow provides fast feedback in layers:

1. Editor: formatting and safe ESLint fixes on save.
2. Pre-commit: lint-staged checks only changed, staged files.
3. Commit message: commitlint enforces a readable, automatable history.
4. Pre-push: formatting, type checking, linting, and tests run locally.
5. Pull request: GitHub Actions repeats checks and produces a production build.

Never treat local hooks as the security boundary; CI remains authoritative.

## Useful commands

```sh
npm run dev
npm run typecheck
npm run lint
npm run format:check
npm run verify
npm run build
npm run storybook
```

## Staged-file behavior

The pre-commit hook may rewrite staged files. Review the resulting diff and stage
the fixes before retrying the commit if Git reports remaining changes.

## Related documentation

- [Local setup](./LOCAL_SETUP.md)
- [Code style](./CODE_STYLE.md)
- [Git workflow](./GIT_WORKFLOW.md)
- [Tooling guide](./TOOLING_GUIDE.md)
- [CI/CD guide](./CI_CD_GUIDE.md)
- [Build pipeline](./BUILD_PIPELINE.md)
- [Release process](./RELEASE_PROCESS.md)
