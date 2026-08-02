# Evaluation Framework

This document defines how prompt packages are evaluated for correctness, quality, and regression safety.

## Goals

| Goal | Description |
|------|-------------|
| **Correctness** | Template renders correctly for all input cases |
| **Regression safety** | Changes do not break previously passing cases |
| **Objectivity** | Acceptance criteria are measurable, not subjective |
| **CI-friendly** | Evaluations run without live LLM API calls in default CI |
| **Traceability** | Cases link to prompt version and acceptance criteria |

## Evaluation Layers

```
┌─────────────────────────────────────────────────────────┐
│  Layer 1: Schema Validation                             │
│  metadata.yaml + input.schema.json + evaluation YAML    │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 2: Template Rendering                            │
│  Render template with case inputs; verify rendered text │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 3: Output Evaluation (offline)                   │
│  Apply acceptance criteria to fixture outputs           │
└──────────────────────────┬──────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Layer 4: Live Evaluation (optional, manual/scheduled)  │
│  Run against real LLM providers in staging              │
└─────────────────────────────────────────────────────────┘
```

Phase 1 implements Layers 1–3. Layer 4 is documented for Phase 2 integration.

## Evaluation Artifacts

### Per-prompt evaluation suite

Location: `prompts/<domain>/<prompt-id>/evaluations/<suite-name>.yaml`

Validated against `schemas/evaluation-suite.schema.json`.

```yaml
prompt_id: greeting
prompt_version: "1.0.0"
description: Basic greeting prompt evaluation
pass_threshold: 1.0
cases:
  - id: formal-greeting
    name: Formal tone greeting
    inputs:
      recipient_name: "Alex"
      tone: formal
    expected_rendered: |
      Compose a formal greeting for Alex.
    acceptance:
      criteria:
        - type: rendered_contains
          value: "Alex"
        - type: rendered_contains
          value: "formal"
      fixture_output: "Dear Alex, it is a pleasure to make your acquaintance."
      criteria:
        - type: output_contains
          value: "Alex"
```

Note: The example above shows structure — see the [greeting example](../../prompts/_examples/greeting/evaluations/basic.yaml) for the canonical file.

### Cross-prompt evaluation suites (Phase 2+)

Location: `evaluations/<suite-name>/`

Used for integration scenarios spanning multiple prompts.

## Acceptance Criteria Types

| Type | Layer | Description |
|------|-------|-------------|
| `rendered_equals` | 2 | Rendered template exactly matches `value` |
| `rendered_contains` | 2 | Rendered template contains `value` |
| `rendered_matches_regex` | 2 | Rendered template matches regex `value` |
| `output_contains` | 3 | Fixture output contains `value` |
| `output_not_contains` | 3 | Fixture output does not contain `value` |
| `output_matches_regex` | 3 | Fixture output matches regex `value` |
| `output_length_min` | 3 | Fixture output length ≥ `value` |
| `output_length_max` | 3 | Fixture output length ≤ `value` |
| `output_json_valid` | 3 | Fixture output parses as JSON |
| `output_json_schema` | 3 | Fixture output validates against `schema_file` |

## Case Requirements

### All prompts (`_examples/` included)

| Requirement | Minimum |
|-------------|---------|
| Evaluation cases | 1 (examples), 2 (production) |
| Happy path case | 1 |
| Edge case | 1 (production only) |

### Production prompts

- `pass_threshold` defaults to `1.0` (all cases must pass)
- Each case must have at least one acceptance criterion
- Offline cases must include `fixture_output` for Layer 3 criteria

## Scoring

Weighted pass rate:

```
score = Σ(case_passed × case_weight) / Σ(case_weight)
suite_passed = score >= pass_threshold
```

Default `case.weight` is `1.0`.

## Running Evaluations

### Local (Phase 1)

```bash
npm run validate    # Layer 1: schema validation
npm run eval        # Layers 2–3: render + offline acceptance
```

### CI

GitHub Actions runs `validate` on every pull request. Live LLM evaluation is not part of default CI.

## Adding Evaluation Cases

1. Create or update a file in `evaluations/` within the prompt package.
2. Define cases with unique `id` values.
3. Provide `inputs` matching `input.schema.json`.
4. Set `expected_rendered` for render-layer checks.
5. Provide `fixture_output` for output-layer checks.
6. Run `npm run eval` locally before opening a PR.

## Live Evaluation (Phase 2+)

For staging environments:

- Use backend AI provider integration with mock-safe staging keys
- Store live eval results as CI artifacts (not in the repository)
- Compare against baseline scores; fail on regression beyond threshold

## Related Documents

- [Prompt Standards](../standards/prompt-standards.md)
- [Evaluation Schemas](../../schemas/evaluation-case.schema.json)
- [Tests Directory](../../tests/README.md)
