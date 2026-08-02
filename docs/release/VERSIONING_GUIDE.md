# Versioning Guide — Cloud Content Hub AI Frontend

This guide defines how frontend versions are numbered, tagged, released, and communicated for Cloud Content Hub AI.

---

## Semantic versioning

The frontend follows [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

| Segment        | When to increment                                                                                | Examples                     |
| -------------- | ------------------------------------------------------------------------------------------------ | ---------------------------- |
| **MAJOR**      | Breaking UI contract, route removal, env var requirement, or incompatible deploy artifact format | `1.0.0` → `2.0.0`            |
| **MINOR**      | Backward-compatible features, new routes, new optional env vars                                  | `1.0.0` → `1.1.0`            |
| **PATCH**      | Backward-compatible fixes, dependency patches, doc-only release packaging                        | `1.0.0` → `1.0.1`            |
| **PRERELEASE** | Release candidates, betas                                                                        | `1.0.0-rc.1`, `1.1.0-beta.2` |

### Pre-1.0 history

- `0.1.0` — development baseline in `package.json` (initial workspace shell)
- **Recommended first production release:** `1.0.0`

---

## Version sources of truth

| Artifact        | Location                     | Notes                                                                        |
| --------------- | ---------------------------- | ---------------------------------------------------------------------------- |
| Package version | `package.json` `"version"`   | Updated ephemerally during release workflow; **not committed** by automation |
| Git tag         | `v<semver>` (e.g., `v1.0.0`) | Created by `release.yml` at validated `main` commit                          |
| GitHub Release  | Releases page                | Title: `Frontend v<semver>`; attaches tarball artifact                       |
| Changelog       | `docs/release/CHANGELOG.md`  | Maintained manually before release; GitHub auto-notes supplement             |

---

## Tag and release naming

| Item                 | Convention                                 |
| -------------------- | ------------------------------------------ |
| Git tag              | `v1.0.0` (with `v` prefix)                 |
| Workflow input       | `1.0.0` (without `v` prefix)               |
| Artifact filename    | `cloud-content-hub-frontend-v1.0.0.tar.gz` |
| GitHub Release title | `Frontend v1.0.0`                          |

Backend releases use a separate tag prefix (`backend-v*`) and workflow; do not collide frontend and backend tags.

---

## Release workflow

Automated via `.github/workflows/release.yml`:

1. Trigger manually: **Actions → Release Frontend → Run workflow**
2. Input semantic version (no `v` prefix)
3. Optionally mark as prerelease
4. Workflow checks out `main`, validates semver, runs quality gates, builds, packages tarball
5. Creates tag `v<version>` at the captured commit and publishes GitHub Release

**Important:** The workflow does not commit version bumps to `main`. Update `CHANGELOG.md` and `RELEASE_NOTES.md` in a pull request before triggering the release.

---

## Branching strategy

| Branch           | Purpose                                                     |
| ---------------- | ----------------------------------------------------------- |
| `main`           | Production-ready line; release tags point here              |
| Feature branches | `feature/<name>` or team convention; merge via PR           |
| Hotfix branches  | Cut from tagged release commit or `main`; merge back via PR |

Release tags are **immutable**. Never force-move or delete published tags without release-owner approval.

---

## Changelog discipline

Before each release:

1. Move `[Unreleased]` entries in `CHANGELOG.md` to a new version section with date
2. Update `RELEASE_NOTES.md` with customer-facing summary
3. Cross-reference `KNOWN_LIMITATIONS.md` for accepted gaps

Categories (Keep a Changelog):

- **Added** — new features
- **Changed** — behavior changes
- **Deprecated** — soon-to-be removed
- **Removed** — removed features
- **Fixed** — bug fixes
- **Security** — vulnerability fixes

---

## Prerelease policy

Use prerelease versions when:

- Backend integration is partial
- Breaking route or env changes need staged validation
- Release blockers are resolved but product sign-off requires staged rollout

Mark prerelease in the GitHub workflow input. Prereleases should deploy to staging only until promoted to stable.

---

## Compatibility matrix

| Frontend version | Node.js    | Next.js | React |
| ---------------- | ---------- | ------- | ----- |
| 1.0.x            | >= 22.22.1 | 15.5.x  | 19.x  |

Pin Node in CI via `NODE_VERSION: "22.22.1"` in workflow env blocks. Local development should match CI.

---

## Deprecation process

1. Announce in `CHANGELOG.md` under **Deprecated** one minor release ahead
2. Document migration in `docs/frontend/`
3. Remove in next major or agreed minor with **Removed** entry

---

## FAQ

**Q: Should I bump `package.json` locally before release?**  
A: No. The release workflow applies the version on the runner. Update changelog docs in PR instead.

**Q: Can two releases share a commit?**  
A: No. Each release tag must reference a distinct validated commit on `main`.

**Q: What if release validation fails?**  
A: No tag or GitHub Release is created. Fix issues via PR, merge to `main`, and trigger a new version.

**Q: How do hotfixes work?**  
A: Fix on `main`, validate CI, release patch version (e.g., `1.0.1`). Roll forward; do not retag.
