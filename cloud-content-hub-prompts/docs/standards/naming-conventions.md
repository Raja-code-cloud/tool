# Naming Conventions

This document defines naming rules for prompts, files, directories, and identifiers in the Cloud Content Hub Prompt Library.

## Prompt Identifiers

| Element | Convention | Example |
|---------|------------|---------|
| Prompt ID | `kebab-case`, lowercase, starts with letter | `content-summary` |
| Domain | `kebab-case`, lowercase | `content-generation` |
| Evaluation case ID | `kebab-case` | `empty-input-rejected` |
| Tags | `kebab-case`, lowercase | `social-media` |

### Prompt ID rules

- Minimum 3 characters, maximum 64 characters
- Use descriptive nouns or verb-noun pairs
- Do not include version numbers in the ID
- Do not include environment names (`dev`, `prod`)
- Do not prefix with `cch-` or `cloud-content-hub-`

### Valid examples

```
greeting
content-summary
social-caption-short
email-subject-line
hashtag-suggestions
```

### Invalid examples

```
ContentSummary        # not kebab-case
v2-content-summary    # version in ID
prod-greeting         # environment in ID
summary               # too vague without domain context
```

## Directory Layout

```
prompts/
├── _examples/                    # Reference packages (underscore prefix)
│   └── greeting/
└── <domain>/                     # Production domain
    └── <prompt-id>/              # One directory per prompt
        ├── metadata.yaml
        ├── template.md
        ├── input.schema.json
        ├── README.md
        ├── examples/
        ├── evaluations/
        └── tests/
```

### Domain naming

Domains group prompts by functional area. Reserved domains for Phase 2+:

| Domain | Purpose |
|--------|---------|
| `content-generation` | Copy, captions, summaries |
| `content-optimization` | SEO, readability, tone adjustment |
| `scheduling` | Post timing, calendar suggestions |
| `analytics` | Insight summaries, report narratives |
| `workspace` | Settings, onboarding, help text |

New domains require documentation update and reviewer approval.

### Special directories

| Directory | Prefix | Purpose |
|-----------|--------|---------|
| `_examples/` | Leading underscore | Non-production reference prompts |
| `_shared/` | Leading underscore | Shared schema fragments (Phase 2+) |

Leading underscore indicates **not for production deployment**.

## File Naming

| File | Name | Required |
|------|------|----------|
| Metadata | `metadata.yaml` | Yes |
| Template | `template.md` or `template.txt` | Yes |
| Input schema | `input.schema.json` | Yes |
| Package README | `README.md` | Yes |
| Example inputs | `examples/<case-name>.json` | Optional |
| Evaluation suite | `evaluations/<suite-name>.yaml` | Production |
| Output schema | `output.schema.json` | When structured output required |
| Tests | `tests/<test-name>.yaml` | Optional |

### Example input files

Use descriptive kebab-case names:

```
examples/
├── formal-tone.json
├── casual-tone.json
└── max-length-input.json
```

### Evaluation files

```
evaluations/
├── basic.yaml          # Happy-path cases
└── edge-cases.yaml     # Boundary and error cases
```

## Variable Naming

Template variables use `snake_case`:

| Valid | Invalid |
|-------|---------|
| `recipient_name` | `recipientName` |
| `max_length` | `max-length` |
| `content_body` | `ContentBody` |

## Schema `$id` Values

Use the canonical URI pattern:

```
https://cloud-content-hub.dev/schemas/<schema-name>.json
https://cloud-content-hub.dev/prompts/<domain>/<prompt-id>/input.schema.json
```

## Git Branch Naming

| Pattern | Use |
|---------|-----|
| `feature/<domain>-<prompt-id>` | New prompt |
| `feature/<short-description>` | Schema or docs changes |
| `fix/<prompt-id>-<short-description>` | Prompt correction |
| `chore/<short-description>` | Tooling updates |

Examples:

```
feature/content-generation-social-caption
fix/greeting-template-typo
chore/validation-script-update
```

## Related Documents

- [Prompt Standards](prompt-standards.md)
- [Versioning Strategy](versioning.md)
