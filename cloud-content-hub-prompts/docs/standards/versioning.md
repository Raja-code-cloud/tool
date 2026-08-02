# Versioning Strategy

This document defines how prompt packages are versioned, released, and deprecated in the Cloud Content Hub Prompt Library.

## Semantic Versioning

All prompts use [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

| Component | When to bump                                                                                                      |
| --------- | ----------------------------------------------------------------------------------------------------------------- |
| **MAJOR** | Breaking change to template output contract, removed/renamed required variables, incompatible input schema change |
| **MINOR** | New optional variables, expanded instructions, new evaluation cases, backward-compatible improvements             |
| **PATCH** | Typo fixes, metadata corrections, documentation-only changes within the package                                   |

### Breaking changes (MAJOR)

- Renaming or removing a template variable
- Changing a variable from optional to required
- Changing variable type or enum values that alter rendering
- Changing output format expectations referenced by downstream consumers
- Removing or fundamentally altering acceptance criteria

### Non-breaking changes (MINOR)

- Adding optional template variables
- Clarifying instructions without changing behavior
- Adding evaluation cases
- Adding constraints metadata

### Patch changes (PATCH)

- Fixing spelling in template text that does not change semantics
- Updating author metadata
- Fixing example payloads

## Immutability Rule

**Released versions are immutable.**

Once a prompt version is tagged or deployed:

1. Do not modify `template.md`, `input.schema.json`, or `metadata.yaml` for that version.
2. Create a new version with an incremented semver.
3. Add a changelog entry explaining the change.

The `_examples/` directory is exempt from immutability for documentation purposes but should still follow semver for consistency.

## Backend Version Mapping

The backend stores `template_version` as a positive integer on `AIPromptTemplate`. Import tooling encodes semver as:

```
template_version = MAJOR * 10000 + MINOR * 100 + PATCH
```

| Semver  | Integer |
| ------- | ------- |
| `1.0.0` | `10000` |
| `1.2.3` | `10203` |
| `2.0.0` | `20000` |

Constraints:

- MAJOR, MINOR, PATCH each fit in their digit range (0–99 for minor/patch in this encoding)
- Import tooling must decode integers back to semver for display

## Repository Versioning

The repository itself follows semver in `CHANGELOG.md`:

| Repository version | Meaning                                      |
| ------------------ | -------------------------------------------- |
| `0.x.x`            | Foundation and scaffolding (Phase 1)         |
| `1.0.0`            | First production prompt collection released  |
| `1.x.x`            | New prompts and non-breaking library changes |
| `2.0.0`            | Breaking schema or standards change          |

Repository tags use the prefix `v` (e.g., `v0.1.0`).

## Lifecycle States

```
┌─────────┐     ┌────────┐     ┌────────────┐     ┌──────────┐
│  draft  │────▶│ active │────▶│ deprecated │────▶│ archived │
└─────────┘     └────────┘     └────────────┘     └──────────┘
```

| Transition            | Action                                                         |
| --------------------- | -------------------------------------------------------------- |
| draft → active        | Prompt passes validation and evaluation; version is finalized  |
| active → deprecated   | Set `status: deprecated`, `deprecated_at`, and `superseded_by` |
| deprecated → archived | After grace period; no new deployments                         |

### Deprecation policy

- Deprecated prompts remain in the repository for at least **90 days**
- `superseded_by` must reference the replacement prompt ID
- Backend sync skips deprecated/archived prompts for new workspace deployments

## Pre-release Versions

Pre-release suffixes are allowed for prompts under development:

```
1.0.0-alpha.1
1.0.0-beta.2
1.0.0-rc.1
```

Pre-release prompts must have `status: draft` and are not deployed to production workspaces.

## Changelog Requirements

### Repository changelog

Update `CHANGELOG.md` at the repository root for:

- Schema changes
- Standards updates
- New domains or evaluation framework changes
- Batch prompt releases

### Package changelog

Each prompt's `metadata.yaml` includes a `changelog` array:

```yaml
changelog:
  - version: "1.0.0"
    date: "2026-08-03"
    summary: "Initial release"
  - version: "1.1.0"
    date: "2026-09-01"
    summary: "Added optional locale variable"
```

## Release Process (Phase 2+)

1. Merge prompt changes to `develop`
2. Run full validation and evaluation suite
3. Update `CHANGELOG.md`
4. Tag repository version
5. Backend import job syncs `active` prompts to workspace templates

## Related Documents

- [Prompt Standards](prompt-standards.md)
- [Naming Conventions](naming-conventions.md)
- [Architecture Overview](../architecture/overview.md)
