# Cross-Prompt Evaluations

This directory holds evaluation suites that span multiple prompt packages.

Phase 1 defines the framework only. Cross-prompt suites will be added in Phase 2 when platform prompts exist.

## Planned structure

```
evaluations/
└── <suite-name>/
    ├── suite.yaml           # Suite metadata and case references
    ├── cases/               # Individual cross-prompt cases
    └── README.md            # Suite description and run instructions
```

See [Evaluation Framework](../docs/evaluation/README.md) for the per-prompt evaluation model used in Phase 1.
