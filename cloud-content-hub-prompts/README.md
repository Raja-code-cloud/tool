# cloud-content-hub-prompts

Prompt library for the Cloud Content Hub AI platform.

This repository is **prompts-only**. It does not contain application code, infrastructure, or runtime services. It holds prompt templates, metadata, schemas, documentation, evaluations, and tests consumed by the Cloud Content Hub backend and tooling.

## Repository Philosophy

| Principle | Description |
|-----------|-------------|
| **Prompts only** | No application code, no infrastructure, no runtime dependencies |
| **Standards-first** | Conventions and schemas documented before prompt collections |
| **Versioned artifacts** | Every prompt is an immutable, semver-versioned package |
| **Evaluated by default** | New prompts ship with evaluation cases and acceptance criteria |
| **Backend-aligned** | Template syntax and metadata map to `AIPromptTemplate` in the backend |
| **Separation of concerns** | Platform prompts live here; execution lives in the backend |

## Related Repositories

| Repository | Purpose |
|------------|---------|
| `cloud-content-hub-ai` | Frontend workspace |
| `backend` | FastAPI application and AI provider integration |
| `cloud-content-hub-infra` | Azure Infrastructure as Code |

## Technology Stack

| Component | Technology |
|-----------|------------|
| Prompt templates | Markdown (`.md`) or plain text (`.txt`) |
| Metadata | YAML (`metadata.yaml`) |
| Schemas | JSON Schema (Draft 2020-12) |
| Evaluations | YAML evaluation suites |
| Validation | AJV (JSON Schema), YAML lint |

## Repository Structure

```
.
├── .github/                 # GitHub Actions and PR templates
├── docs/
│   ├── architecture/        # Platform prompt architecture
│   ├── adr/                 # Architecture Decision Records
│   ├── evaluation/          # Evaluation framework
│   └── standards/           # Prompt standards, naming, versioning
├── schemas/                 # JSON Schema definitions
├── prompts/
│   ├── _examples/           # Reference prompt packages (not for production)
│   └── <domain>/            # Production prompts by domain (Phase 2+)
├── evaluations/             # Cross-prompt evaluation suites (Phase 2+)
├── tests/                   # Prompt test harness documentation
├── scripts/                 # Validation scripts
├── CHANGELOG.md
├── CONTRIBUTING.md
└── README.md
```

## Prompt Package Layout

Each prompt is a self-contained directory:

```
prompts/<domain>/<prompt-id>/
├── metadata.yaml            # Required — identity, version, purpose, status
├── template.md              # Required — prompt body with {variable} placeholders
├── input.schema.json        # Required — JSON Schema for template variables
├── README.md                # Required — usage, constraints, changelog notes
├── examples/                # Optional — sample variable payloads
├── evaluations/             # Required for production prompts — eval cases
└── tests/                   # Optional — automated prompt tests
```

See [Prompt Standards](docs/standards/prompt-standards.md) and the [example prompt](prompts/_examples/greeting/) for the canonical format.

## Quick Start

### Validate locally

```bash
npm install
npm run validate
```

This checks:

- All `metadata.yaml` files against `schemas/prompt-metadata.schema.json`
- All `input.schema.json` files against `schemas/prompt-input.schema.json`
- Evaluation case files against evaluation schemas
- Required files exist for each prompt package

### Add a new prompt (Phase 2+)

1. Read [CONTRIBUTING.md](CONTRIBUTING.md) and [Prompt Standards](docs/standards/prompt-standards.md).
2. Copy `prompts/_examples/greeting/` as a scaffold.
3. Update `metadata.yaml`, `template.md`, and `input.schema.json`.
4. Add evaluation cases under `evaluations/`.
5. Run `npm run validate` and open a pull request.

## Versioning

Prompts use [Semantic Versioning 2.0.0](https://semver.org/). See [Versioning Strategy](docs/standards/versioning.md).

| Change type | Version bump | Example |
|-------------|--------------|---------|
| Breaking template or input schema change | MAJOR | `1.0.0` → `2.0.0` |
| New optional variables or improved instructions | MINOR | `1.0.0` → `1.1.0` |
| Typo fix, metadata-only update | PATCH | `1.0.0` → `1.0.1` |

## Documentation Index

| Document | Description |
|----------|-------------|
| [Architecture Overview](docs/architecture/overview.md) | How prompts integrate with the platform |
| [Prompt Standards](docs/standards/prompt-standards.md) | Authoring rules and template syntax |
| [Naming Conventions](docs/standards/naming-conventions.md) | IDs, domains, and file naming |
| [Versioning Strategy](docs/standards/versioning.md) | Semver rules and lifecycle |
| [Evaluation Framework](docs/evaluation/README.md) | How to write and run evaluations |
| [ADR-0001](docs/adr/adr-0001-prompt-library-foundation.md) | Foundation architecture decision |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution workflow |

## Phase 1 Scope

Phase 1 delivers repository foundation only:

- [x] Repository structure and directory layout
- [x] Prompt metadata schema
- [x] Standards, naming, and versioning documentation
- [x] Evaluation framework specification
- [x] Example prompt format
- [x] Contribution guidelines and CHANGELOG
- [ ] Platform-specific prompt collections (Phase 2)

## License

Internal use — Cloud Content Hub AI platform.
