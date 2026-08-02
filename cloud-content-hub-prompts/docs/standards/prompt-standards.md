# Prompt Standards

This document defines authoring rules for Cloud Content Hub prompt packages.

## Design Principles

| Principle | Rule |
|-----------|------|
| **Single purpose** | One prompt accomplishes one task |
| **Explicit inputs** | Every variable is documented in `input.schema.json` |
| **Strict rendering** | Template placeholders must match schema exactly |
| **Immutable versions** | Never edit a released version in place — bump semver |
| **Evaluated** | Production prompts include objective acceptance criteria |
| **Safe by default** | No instructions that bypass platform guardrails |

## Template Syntax

Prompts use the **python-format** engine, matching the backend `render_prompt()` function.

### Placeholders

```
Hello {recipient_name}, welcome to {product_name}.
```

| Rule | Detail |
|------|--------|
| Variable names | `snake_case` only |
| Required variables | Must appear in both template and `input.schema.json` `required` array |
| Unknown variables | Renderer rejects variables not in the template |
| Missing variables | Renderer rejects missing required variables |
| Literal braces | Not supported in Phase 1 |

### Template file

| Property | Value |
|----------|-------|
| Filename | `template.md` or `template.txt` |
| Format | Markdown (preferred) or plain text |
| Location | Root of the prompt package directory |

Markdown formatting is preserved in the rendered output. Use headings and lists when they improve LLM comprehension.

## Metadata

Every prompt package requires `metadata.yaml` validated against `schemas/prompt-metadata.schema.json`.

### Required fields

| Field | Description | Backend mapping |
|-------|-------------|-----------------|
| `id` | Unique kebab-case identifier | Used as lookup key during import |
| `name` | Display name | `AIPromptTemplate.name` |
| `version` | Semver string | Encoded to `template_version` integer |
| `purpose` | One-line description | `AIPromptTemplate.purpose` |
| `domain` | Functional grouping | Organizational only |
| `status` | Lifecycle state | `AIPromptTemplate.is_active` |
| `template` | Template file reference | Source for `template_text` |
| `input_schema` | Schema file reference | `AIPromptTemplate.input_schema` |
| `authors` | Author list | Metadata only |
| `created_at` | Creation date | Metadata only |
| `updated_at` | Last update date | Metadata only |

### Status lifecycle

```
draft → active → deprecated → archived
```

| Status | `is_active` | Usage |
|--------|-------------|-------|
| `draft` | false | Work in progress, not deployed |
| `active` | true | Production-ready, may be deployed |
| `deprecated` | false | Superseded, existing references still resolve |
| `archived` | false | Retained for audit, not deployable |

## Input Schema

Each prompt includes `input.schema.json` defining template variables.

### Rules

1. Root type must be `object`.
2. `additionalProperties` must be `false`.
3. Every property uses `snake_case`.
4. Every property requires a `description`.
5. The `required` array lists mandatory variables.
6. Validate against `schemas/prompt-input.schema.json` wrapper.

### Example

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Greeting Prompt Inputs",
  "type": "object",
  "additionalProperties": false,
  "required": ["recipient_name", "tone"],
  "properties": {
    "recipient_name": {
      "type": "string",
      "description": "Name of the person being greeted",
      "minLength": 1,
      "maxLength": 100
    },
    "tone": {
      "type": "string",
      "description": "Desired tone of the greeting",
      "enum": ["formal", "casual", "friendly"]
    }
  }
}
```

## Prompt Package README

Each prompt package includes a `README.md` with:

1. **Overview** — What the prompt does
2. **Inputs** — Table of variables with descriptions
3. **Constraints** — Token limits, supported models
4. **Examples** — How to render with sample inputs
5. **Changelog** — Version history for this prompt
6. **Evaluation** — Summary of eval cases and pass criteria

## Safety Guidelines

- Do not include instructions to ignore prior rules or bypass safety filters.
- Do not embed secrets, API keys, or credentials in templates or examples.
- Do not use real customer data in examples — use synthetic fixtures.
- Document PII handling requirements when prompts process user content.
- Prefer structured output instructions when downstream parsing is required.

## Anti-Patterns

| Anti-pattern | Correct approach |
|--------------|------------------|
| Editing a released version in place | Bump semver, add changelog entry |
| Variables in template but not in schema | Add to `input.schema.json` |
| Schema properties not used in template | Remove or document as `required_variables` |
| Vague acceptance criteria ("good output") | Use measurable criteria |
| Monolithic multi-task prompts | Split into focused prompt packages |

## Related Documents

- [Naming Conventions](naming-conventions.md)
- [Versioning Strategy](versioning.md)
- [Evaluation Framework](../evaluation/README.md)
- [Example Prompt](../../prompts/_examples/greeting/)
