# Example: Greeting Prompt

Reference prompt package demonstrating the canonical format for Cloud Content Hub prompts.

**This is not a production prompt.** It exists solely to illustrate structure, metadata, schemas, and evaluations.

## Overview

Generates a simple greeting instruction for a named recipient with a specified tone. Used to validate template rendering and evaluation framework wiring.

## Inputs

| Variable         | Type   | Required | Description                                     |
| ---------------- | ------ | -------- | ----------------------------------------------- |
| `recipient_name` | string | Yes      | Name of the person being greeted (1–100 chars)  |
| `tone`           | string | Yes      | Desired tone: `formal`, `casual`, or `friendly` |

## Usage

Render the template with sample inputs from `examples/`:

```json
{
  "recipient_name": "Alex",
  "tone": "formal"
}
```

Expected rendered output:

```
Compose a greeting for Alex.

Use a formal tone. Address the recipient by name.
Keep the greeting concise (one to two sentences).
```

## Constraints

| Constraint            | Value              |
| --------------------- | ------------------ |
| Template engine       | python-format      |
| Max prompt characters | 2000 (recommended) |

## Changelog

| Version | Date       | Summary                |
| ------- | ---------- | ---------------------- |
| 1.0.0   | 2026-08-03 | Initial example prompt |

## Evaluation

See `evaluations/basic.yaml` — two cases covering formal and casual tones.
