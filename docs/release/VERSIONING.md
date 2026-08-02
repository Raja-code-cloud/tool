# Versioning — Cloud Content Hub AI Frontend

This document defines version numbering, tagging, and release communication for the Cloud Content Hub AI frontend.

**Related:** [VERSIONING_GUIDE.md](./VERSIONING_GUIDE.md) (extended reference) · [RELEASE_PROCESS.md](../frontend/RELEASE_PROCESS.md)

---

## Semantic versioning

The frontend follows [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

| Segment        | When to increment                                                                             | Examples                     |
| -------------- | --------------------------------------------------------------------------------------------- | ---------------------------- |
| **MAJOR**      | Breaking UI contract, route removal, required env var, or incompatible deploy artifact format | `1.0.0` → `2.0.0`            |
| **MINOR**      | Backward-compatible features, new routes, new optional env vars                               | `1.0.0` → `1.1.0`            |
| **PATCH**      | Backward-compatible fixes, dependency patches                                                 | `1.0.0` → `1.0.1`            |
| **PRERELEASE** | Release candidates, betas                                                                     | `1.0.0-rc.1`, `1.0.0-beta.2` |

---

## RC1 version recommendation

| Field               | Value                                           |
| ------------------- | ----------------------------------------------- |
| **Recommended RC**  | `1.0.0-rc.1`                                    |
| **Git tag**         | `v1.0.0-rc.1`                                   |
| **Prerelease**      | Yes                                             |
| **Current package** | `0.1.0` (unchanged until release workflow runs) |

### Why `1.0.0-rc.1` is appropriate

1. **First candidate for production** — Engineering implementation is complete; RC1 validates packaging, documentation, and deployment readiness before stable `1.0.0`.
2. **Semver prerelease convention** — `-rc.1` signals staged rollout, not a final stable release.
3. **Accepted product gaps** — Mock data layer, no authentication, and calendar placeholder are documented limitations unsuitable for an unqualified `1.0.0` stable tag.
4. **Pending principal review** — RC3 Principal Review runs separately; RC1 allows staging validation while that review completes.
5. **CI/CD alignment** — The release workflow accepts prerelease versions and marks GitHub Releases accordingly.

### Promotion path

```
0.1.0 (dev) → 1.0.0-rc.1 (RC1) → 1.0.0-rc.2 (if needed) → 1.0.0 (stable)
```

Cut `1.0.0` only after RC sign-off, RC3 Principal Review clearance, and resolution of release blockers documented in [RELEASE_SIGNOFF.md](./RELEASE_SIGNOFF.md).

---

## Version sources of truth

| Artifact        | Location                          | Notes                                                                        |
| --------------- | --------------------------------- | ---------------------------------------------------------------------------- |
| Package version | `package.json` `"version"`        | Updated ephemerally during release workflow; **not committed** by automation |
| Git tag         | `v<semver>` (e.g., `v1.0.0-rc.1`) | Created by `release.yml` at validated `main` commit                          |
| GitHub Release  | Releases page                     | Title: `Frontend v<semver>`; attaches tarball artifact                       |
| Changelog       | `docs/release/CHANGELOG.md`       | Maintained before release; GitHub auto-notes supplement                      |

---

## Tag and release naming

| Item                 | Convention                                      |
| -------------------- | ----------------------------------------------- |
| Git tag              | `v1.0.0-rc.1` (with `v` prefix)                 |
| Workflow input       | `1.0.0-rc.1` (without `v` prefix)               |
| Artifact filename    | `cloud-content-hub-frontend-v1.0.0-rc.1.tar.gz` |
| GitHub Release title | `Frontend v1.0.0-rc.1`                          |

Backend releases use a separate tag prefix (`backend-v*`) and workflow; do not collide frontend and backend tags.

---

## Release workflow

Automated via `.github/workflows/release.yml`:

1. Trigger manually: **Actions → Release Frontend → Run workflow**
2. Input semantic version (no `v` prefix): `1.0.0-rc.1`
3. Enable **prerelease** checkbox
4. Workflow checks out `main`, validates semver, runs quality gates, builds, packages tarball
5. Creates tag `v<version>` at the captured commit and publishes GitHub Release

**Important:** The workflow does not commit version bumps to `main`. Update `CHANGELOG.md` and release notes in a pull request before triggering the release.

---

## Compatibility matrix (RC1)

| Frontend version | Node.js | Next.js | React  |
| ---------------- | ------- | ------- | ------ |
| 1.0.0-rc.1       | 22.22.1 | 15.5.22 | 19.2.8 |

Pin Node in CI via `NODE_VERSION: "22.22.1"` in workflow env blocks. Local development should match CI (see `.nvmrc`).

**Note:** `package.json` `engines` currently declares `>=20.11.0`; CI and documentation standardize on **22.22.1**.

---

## Branching and immutability

| Branch           | Purpose                                         |
| ---------------- | ----------------------------------------------- |
| `main`           | Production-ready line; release tags point here  |
| Feature branches | Merge via pull request                          |
| Hotfix branches  | Cut from tagged release or `main`; merge via PR |

Release tags are **immutable**. Never force-move or delete published tags without release-owner approval.

---

## Changelog discipline

Before each release:

1. Move `[Unreleased]` entries in `CHANGELOG.md` to a new version section with date
2. Update `RELEASE_NOTES_RC1.md` (or stable `RELEASE_NOTES.md` for GA)
3. Cross-reference [KNOWN_ISSUES.md](./KNOWN_ISSUES.md) for accepted gaps

Categories (Keep a Changelog): Added, Changed, Deprecated, Removed, Fixed, Security.

---

## FAQ

**Q: Should I bump `package.json` locally before release?**  
A: No. The release workflow applies the version on the runner. Update changelog docs in PR instead.

**Q: Why RC1 instead of jumping to 1.0.0?**  
A: RC1 communicates staged validation, documents known limitations, and aligns with prerelease deployment policy.

**Q: What if release validation fails?**  
A: No tag or GitHub Release is created. Fix issues via PR, merge to `main`, and trigger a new version.

**Q: How do hotfixes work after GA?**  
A: Fix on `main`, validate CI, release patch version (e.g., `1.0.1`). Roll forward; do not retag.
