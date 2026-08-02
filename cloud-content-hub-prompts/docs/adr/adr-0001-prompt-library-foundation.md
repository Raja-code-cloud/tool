# ADR-0001: Prompt Library Foundation

## Status

Accepted

## Date

2026-08-03

## Context

Cloud Content Hub AI requires a curated, versioned library of prompt templates for content generation, optimization, and workspace operations. Prompts are currently embedded implicitly in backend code paths and lack:

- Centralized authoring and review
- Semantic versioning and deprecation lifecycle
- Input validation schemas
- Evaluation and regression testing
- Separation from application runtime code

The platform already has an `AIPromptTemplate` database model and a strict `render_prompt()` function using Python `str.format` syntax. A dedicated repository must align with these existing backend contracts.

## Decision

Create a standalone repository `cloud-content-hub-prompts` with:

1. **Self-contained prompt packages** — Each prompt is a directory with `metadata.yaml`, `template.md`, `input.schema.json`, and evaluations.

2. **JSON Schema validation** — Metadata, input schemas, and evaluation cases are validated against canonical schemas in CI.

3. **Python-format template engine** — All templates use `{snake_case}` placeholders matching the backend renderer. No alternative engines in Phase 1.

4. **Semantic versioning** — Prompt versions are immutable semver strings encoded to backend `template_version` integers.

5. **Offline-first evaluation** — CI validates template rendering and applies acceptance criteria to fixture outputs without live LLM calls.

6. **Standards before content** — Phase 1 delivers structure, schemas, and documentation only. Platform-specific prompts are deferred to Phase 2.

## Consequences

### Positive

- Prompt authors can contribute without touching application code
- Version history and deprecation are explicit
- Backend import tooling has a stable, validated source format
- Evaluation framework enables regression detection before deployment

### Negative

- Two repositories to synchronize (prompts → backend)
- Semver-to-integer encoding limits minor/patch to 0–99
- Python-format syntax restricts template expressiveness (no conditionals)

### Neutral

- Import/sync tooling is deferred to Phase 2
- Live LLM evaluation requires separate staging infrastructure

## Alternatives Considered

### Prompts in the backend repository

Rejected. Mixes runtime code with content artifacts, complicates review workflows, and prevents non-engineer contributors from authoring prompts.

### Jinja2 or Handlebars template engine

Rejected for Phase 1. Would require backend renderer changes. Python-format is sufficient for current use cases and already implemented.

### Database-only prompt storage

Rejected. Git provides version control, PR review, and changelog history that database-only storage lacks.

## References

- Backend model: `backend/src/cloud_content_hub/infrastructure/database/models/ai_prompt_template.py`
- Backend renderer: `backend/src/cloud_content_hub/infrastructure/ai/prompts/renderer.py`
- [Architecture Overview](../architecture/overview.md)
- [Prompt Standards](../standards/prompt-standards.md)
