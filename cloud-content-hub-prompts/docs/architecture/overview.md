# Architecture Overview

This document describes how the Cloud Content Hub Prompt Library integrates with the platform.

## System Context

```
┌──────────────────────────────┐
│  cloud-content-hub-prompts   │  ← This repository
│  (templates, metadata, evals)│
└──────────────┬───────────────┘
               │ import / sync
               ▼
┌──────────────────────────────┐
│  Backend (FastAPI)           │
│  AIPromptTemplate model      │
│  render_prompt()             │
└──────────────┬───────────────┘
               │ generation requests
               ▼
┌──────────────────────────────┐
│  AI Providers                │
│  (OpenAI, Azure OpenAI, Mock)  │
└──────────────────────────────┘
```

The prompt library is the **source of truth** for prompt content. The backend is the **runtime** that stores, versions, and executes prompts per workspace.

## Backend Integration

### AIPromptTemplate mapping

| Prompt Library                      | Backend (`AIPromptTemplate`) |
| ----------------------------------- | ---------------------------- |
| `metadata.yaml → name`              | `name`                       |
| `metadata.yaml → purpose`           | `purpose`                    |
| `template.md` content               | `template_text`              |
| `metadata.yaml → version` (encoded) | `template_version`           |
| `input.schema.json` content         | `input_schema` (JSONB)       |
| `metadata.yaml → status: active`    | `is_active: true`            |

### Template rendering

The backend uses strict Python `str.format` rendering via `render_prompt()`:

1. Parse template placeholders
2. Merge with `required_variables` from metadata
3. Validate all required variables are present
4. Reject unknown variables
5. Render final prompt text

Prompt authors must match this behavior — see [Prompt Standards](../standards/prompt-standards.md).

### Workspace scoping

Prompts are deployed per workspace. The import process:

1. Reads `active` prompts from this repository
2. Creates or updates `AIPromptTemplate` records per target workspace
3. Increments `template_version` when semver changes
4. Links `AIGenerationRequest.prompt_template_id` to the deployed template

## Repository Boundaries

| In this repository   | Not in this repository     |
| -------------------- | -------------------------- |
| Prompt template text | API endpoints              |
| Variable schemas     | Database migrations        |
| Evaluation cases     | Provider authentication    |
| Standards and docs   | Frontend UI components     |
| Validation tooling   | Infrastructure (Terraform) |

## Data Flow

```
Author ──▶ PR ──▶ CI validate ──▶ merge ──▶ tag release
                                              │
                                              ▼
                                    Backend import job
                                              │
                                              ▼
                              AIPromptTemplate (per workspace)
                                              │
                                              ▼
                              AIGenerationRequest (runtime)
```

## Phase Roadmap

| Phase       | Scope                                              | Status  |
| ----------- | -------------------------------------------------- | ------- |
| **Phase 1** | Repository foundation, schemas, standards, example | Current |
| **Phase 2** | Platform prompt collections, import tooling        | Planned |
| **Phase 3** | Live evaluation pipeline, regression baselines     | Planned |
| **Phase 4** | Workspace-specific prompt overrides                | Planned |

## Security Considerations

- Prompt templates may contain instructions that influence LLM behavior — review for injection risks
- Input schemas constrain variable types and lengths before rendering
- Backend redacts `prompt` content from logs and telemetry
- No secrets in prompt packages — use backend secret management

## Related Documents

- [ADR-0001: Prompt Library Foundation](../adr/adr-0001-prompt-library-foundation.md)
- [Prompt Standards](../standards/prompt-standards.md)
- [Versioning Strategy](../standards/versioning.md)
