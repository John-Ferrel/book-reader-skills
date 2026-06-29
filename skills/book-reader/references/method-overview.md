# Method Overview

Book Reader turns book surface text into a revisable reconstruction workspace:

```text
source block -> note item -> model inference
```

It does not summarize first. It constructs local evidence, integrates across
units, reconstructs the book model, reviews inference discipline, and plans
continuation.

Default run loop:

```text
intake -> reconstruction -> self-check -> independent review -> revise -> verification review
```

Creator self-check is not independent review and cannot mark the workspace
stable.

Core invariant checks:

- Source evidence exists and is inspectable.
- Note items distinguish observation, paraphrase, inference, uncertainty,
  question, and external context.
- Important model claims cite source block, note item, and unit.
- Confidence, alternative interpretation, and revision condition are present.
- Source limits are explicit.
- Artifacts are useful views over thinking, not boxes to fill.
- Optional artifacts may be created by reader/reviser, but reviewer judges
  whether they are useful, redundant, premature, empty-shell, duplicated, or
  not-applicable.

Use scripts only for mechanical intake. Do not let code write semantic
conclusions.
