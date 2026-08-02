# Versioning

Content versioning in the application module enforces immutability, provenance, and history
preservation.

## Concepts

| Concept           | Description                                                                       |
| ----------------- | --------------------------------------------------------------------------------- |
| Content aggregate | Mutable projection (`ContentRecord`) pointing at the current version              |
| Content version   | Immutable snapshot (`ContentVersionDetailRecord`) with monotonic `version_number` |
| Generation output | Mutable candidate (`GenerationOutputRecord`) until approved or rejected           |
| Origin            | `user`, `ai`, `import`, or `regeneration`                                         |

## Rules

1. **Every materialized change creates a new version.** Approving AI output or committing user edits
   via `CreateContentVersion` appends a version; nothing is updated in place.
2. **Versions are immutable.** Repository ports expose versions as read-only detail records.
3. **Regeneration never overwrites.** Each regeneration request produces new outputs; prior outputs
   remain for audit.
4. **History is preserved.** Compare, list, and get-version queries read the full chain.
5. **Soft delete applies to aggregates only.** Deleting content sets `deleted_at` on the aggregate;
   versions and generation artifacts remain for compliance.

## Creating versions

### User-origin (`CreateContentVersionHandler`)

```
validate content state
→ create_version(NewContentVersion, origin=user)
→ set_current_version(content_id, version_id)
→ return ContentVersionResponse
```

### AI-origin (`ApproveContentHandler`)

```
validate pending generation output
→ create_version(NewContentVersion, origin=ai, body from output)
→ approve output
→ set_current_version
→ publish ContentApproved
```

## Querying versions

| Query               | Result                                                    |
| ------------------- | --------------------------------------------------------- |
| `GetContentVersion` | Single immutable snapshot                                 |
| `CompareVersions`   | Title/body/metadata change flags between two version IDs  |
| `GetContent`        | Current aggregate projection including `contentVersionId` |

## Concurrency

Mutating commands carry `expected_version` (optimistic concurrency). Handlers call
`validate_expected_version` and repository methods with `expected_version=` so conflicting writes
raise `ContentVersionConflictError` (`409 version_conflict` at the API layer).

## Duplication

`DuplicateContentHandler` creates a new draft aggregate derived from the current immutable
version. The source version history is not copied; the duplicate starts a new lineage with an
initial version cloned from the source snapshot.
