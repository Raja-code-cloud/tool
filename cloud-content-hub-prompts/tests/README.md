# Prompt Tests

This directory documents the automated test harness for prompt packages.

## Scope

Prompt tests extend evaluations with structural and integration checks:

| Test type | Description | Phase |
|-----------|-------------|-------|
| Schema validation | Metadata and input schema conformance | 1 |
| Render tests | Template renders without error for all cases | 1 |
| Acceptance tests | Offline criteria pass against fixtures | 1 |
| Snapshot tests | Rendered output matches committed snapshots | 2 |
| Integration tests | End-to-end via backend API in staging | 3 |

## Per-prompt tests

Optional test files live within each prompt package:

```
prompts/<domain>/<prompt-id>/tests/
└── render.test.yaml
```

Phase 1 uses the repository-level validation script instead of per-prompt test files.

## Running tests

```bash
npm run validate   # Schema + structure validation
npm run eval       # Render + acceptance evaluation
```

## Phase 2 plans

- Snapshot testing for rendered template output
- Contract tests against backend import format
- Performance benchmarks for token count limits

See [Evaluation Framework](../docs/evaluation/README.md).
