# Contributing to cloud-content-hub-prompts

Thank you for contributing to the Cloud Content Hub Prompt Library.

## Scope

This repository contains **prompt artifacts only**:

- Prompt templates and metadata
- JSON Schemas for prompt inputs
- Evaluation cases and suites
- Documentation and standards

Do **not** submit application code (Python, FastAPI, Next.js), infrastructure (Terraform), or runtime services. Those belong in their respective repositories.

## Branching Strategy

| Branch      | Purpose                                      |
| ----------- | -------------------------------------------- |
| `main`      | Production-ready prompt library state        |
| `develop`   | Integration branch for staged prompt changes |
| `feature/*` | New prompts, schema updates, documentation   |
| `fix/*`     | Corrections to existing prompts or schemas   |
| `chore/*`   | Tooling, CI, and non-functional updates      |

## Development Workflow

1. Create a feature branch from `develop` (or `main` for hotfixes).
2. Make changes following [Prompt Standards](docs/standards/prompt-standards.md).
3. Run the local validation pipeline:

   ```bash
   npm install
   npm run validate
   ```

4. Open a pull request with a clear description and linked work item.
5. Ensure all CI checks pass and obtain required approvals.
6. Merge using squash merge unless otherwise specified.

## Adding a New Prompt (Phase 2+)

Production prompts are not part of Phase 1. When adding prompts in later phases:

1. Choose a [domain and prompt ID](docs/standards/naming-conventions.md).
2. Copy the scaffold from `prompts/_examples/greeting/`.
3. Author `metadata.yaml`, `template.md`, `input.schema.json`, and `README.md`.
4. Add at least one evaluation case under `evaluations/`.
5. Bump version according to [Versioning Strategy](docs/standards/versioning.md).
6. Update `CHANGELOG.md` under `[Unreleased]`.

## Prompt Authoring Rules

Full standards: **[docs/standards/prompt-standards.md](docs/standards/prompt-standards.md)**

### Required files per prompt package

| File                 | Required        | Description                                |
| -------------------- | --------------- | ------------------------------------------ |
| `metadata.yaml`      | Yes             | Identity, version, purpose, status         |
| `template.md`        | Yes             | Prompt body with `{variable}` placeholders |
| `input.schema.json`  | Yes             | JSON Schema for template variables         |
| `README.md`          | Yes             | Usage, constraints, local changelog        |
| `evaluations/*.yaml` | Production only | Evaluation cases with acceptance criteria  |

### Template syntax

- Use Python `str.format` placeholders: `{variable_name}`.
- Variable names must be `snake_case`.
- Every placeholder in the template must appear in `input.schema.json`.
- Do not use `{` or `}` literally — escape is not supported in Phase 1.

### Metadata

- `id` must be globally unique within the repository.
- `version` must follow semver (`MAJOR.MINOR.PATCH`).
- `status` must be one of: `draft`, `active`, `deprecated`, `archived`.

## Evaluation Requirements

All production prompts must include evaluation cases. See [Evaluation Framework](docs/evaluation/README.md).

| Requirement             | Description                                       |
| ----------------------- | ------------------------------------------------- |
| Minimum cases           | At least 2 cases: one happy path, one edge case   |
| Acceptance criteria     | Measurable checks (contains, length, format)      |
| No live API calls in CI | Evaluations use fixture outputs or mock providers |

## Pull Request Checklist

- [ ] `npm run validate` passes locally
- [ ] Prompt follows naming conventions
- [ ] Version bumped appropriately (if modifying an existing prompt)
- [ ] `CHANGELOG.md` updated
- [ ] No secrets, API keys, or real customer data in examples
- [ ] ADR added for significant architectural decisions
- [ ] README updated for the prompt package (if applicable)

## Review Criteria

Reviewers should verify:

1. **Correctness** — Template variables match input schema
2. **Safety** — No instructions that bypass platform guardrails
3. **Clarity** — Purpose and constraints are documented
4. **Evaluability** — Acceptance criteria are objective
5. **Versioning** — Semver bump matches the change type

## Architecture Decisions

Significant changes (schema redesign, template engine change, evaluation model change) require an ADR in `docs/adr/`. Use the naming pattern `adr-NNNN-short-title.md`.

## Questions

For platform integration questions, refer to the backend `AIPromptTemplate` model and the [Architecture Overview](docs/architecture/overview.md).
