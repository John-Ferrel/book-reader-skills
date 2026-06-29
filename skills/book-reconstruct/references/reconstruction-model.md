# Reconstruction Model

Build `model/` as the center of the workspace, but never as unsupported opinion.

Core model artifacts:

- `author-problem.md`
- `reader-path.md`
- `concept-system.md`
- `argument-architecture.md`
- `book-design.md`
- `assumptions-tradeoffs.md`
- `edition-layers.md` when applicable or explicitly not-applicable

Each important model claim uses a claim card:

```markdown
## Claim: <short claim>

Claim ID:
Type: observation | inference | synthesis | uncertainty | external-context
Status: active | tentative | superseded | deferred
Confidence: high | medium | low | source-limited

Evidence:
- Source:
- Note:
- Unit:

Reasoning:

Alternative Interpretation:

What Would Change This Model:

Revision History:
- round:
- change:
```

If a claim has only source evidence and no note item:

```text
Traceability: weak
Reason: no note item reference yet
```

Essay-only model files should fail review. A model file may be deferred,
blocked, or not-applicable, but it must say `Status`, `Reason`, and `Next
Action`.
