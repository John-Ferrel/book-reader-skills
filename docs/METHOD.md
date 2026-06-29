# Book Reader Method

Book Reader is an evidence-driven reading methodology for agents. It is not a
summary generator, parser framework, RAG ingestion pipeline, or checklist for
filling files.

The method converts a book’s surface text into a revisable reconstruction
workspace:

```text
source evidence -> note items -> reconstruction model -> discipline review -> revision / continuation
```

## Method equation

```text
Book Reader Method =
Evidence Discipline
+ Construction / Integration
+ Reconstruction Lenses
+ Knowledge Organization
+ Review / Revision Loop
+ Continuation Planning
```

## Evidence discipline

The core traceability invariant is:

```text
source block -> note item -> model inference
```

Source blocks are mechanical anchors in `evidence/source-map.json`. Note items
are stable reading claims inside `notes/`, such as `obs-ru-006-001` or
`inf-ru-006-001`. Model inferences in `model/` cite both whenever possible.

If a claim has no note item yet, it must say:

```text
Traceability: weak
Reason: no note item reference yet
```

## Note item distinctions

- Observation: directly visible in the supplied source.
- Paraphrase: faithful restatement of a source block.
- Inference: interpretation drawn from cited observations/paraphrases.
- Uncertainty: unresolved reading problem with a `What-would-resolve` condition.
- Question: a carried-forward inquiry, not a conclusion.
- External context: outside information, labelled so it does not pollute the
  source-supported model.

Inference items need confidence, alternative interpretation, and a revision
condition.

## Construction and integration

Reading proceeds by construction, not direct summarization:

1. Inspect source metadata, limitations, and source-map anchors.
2. Confirm, merge, split, or discard unit candidates into semantic units.
3. Build local note items from source blocks.
4. Integrate note items into threads.
5. Reconstruct the book’s backend model: author problem, reader path, concept
   system, argument architecture, book design, assumptions/tradeoffs, and
   edition/revision layers when present.
6. Build indexes as navigation and audit surfaces.
7. Plan continuation and review targets.

## Confidence, alternatives, and revision

Reconstruction is not mind-reading. Every important model claim is inferred,
evidence-linked, confidence-labelled, alternative-aware, and revisable.

Confidence labels:

- high: multiple clear anchors converge.
- medium: plausible pattern with incomplete support.
- low: tentative interpretation.
- source-limited: available source cannot support a stronger claim.

A credible alternative interpretation is not a defect. It is part of the model.

## Core invariants vs lenses

Core invariants apply to every book:

- source evidence
- note item IDs
- inference/source-fact separation
- confidence
- alternative interpretation
- revision condition
- reviewer boundary

Lenses adapt the method without changing the invariants:

- technical-book: definitions, notation, methods, examples, proof strategy.
- nonfiction-argument: claims, grounds, warrants, counterclaims, assumptions.
- fiction-narrative: scenes, character arcs, motifs, voice, rhythm.
- essay-anthology: unit independence, editorial sequence, cross-essay tension.
- reference-book: taxonomy, lookup structure, scope notes, cross references.
- source-limited: safe claims, missing modalities, recovery plan.
- edition-revision: original layer, later revision, retrospective tension.
- external-context: source model vs modern bridge/comparison/application.

Lens-specific behavior must not be forced into the core method.

## Code fallback vs document fallback

Code fallback handles extraction uncertainty:

- encoding fallback
- EPUB metadata missing
- PDF text extraction warnings
- degraded block extraction
- dependency missing

Document fallback handles interpretation uncertainty:

- author problem unresolved
- concept system has competing models
- argument architecture is weakly supported
- source-limited claims
- external context needed

Code must not automatically fill semantic conclusions.

## Artifacts are views over thinking

Artifacts are views over thinking, not boxes to fill. If an artifact does not
improve reconstruction, omit it or mark it `not-applicable`, `deferred`, or
`blocked` with a reason.

File count is not reading quality. A smaller workspace with traceable,
well-calibrated claims is better than a larger checklist-shaped workspace.

## Review and revision

Reviewer audits inference discipline, not personal agreement. It asks whether
claims trace to evidence, whether confidence is calibrated, whether alternatives
are represented, and whether source limits are honest.

Reviewer does not repair the workspace by default. Revision is a separate role:
it reads `review/revision-plan.md`, applies changes, preserves or supersedes
prior claims, updates state, and records a revision log.

Default full-read requires an independent review loop:

```text
reader reconstructs
-> independent reviewer audits
-> reviser re-reads / revises
-> independent reviewer verifies
-> repeat until stable or max rounds reached
```

Creator self-check can improve a reconstruction, but it cannot certify
completion or stability.

Artifact redundancy is reviewer-judged, not creator-self-certified. A creator
may create optional artifacts it believes are useful, but reviewer decides
whether each is useful, redundant, empty-shell, premature, duplicated,
not-applicable, deferred, or blocked.

## Revisable workspace

A Book Reader workspace is not final truth. It is a durable, inspectable,
revisable knowledge framework that lets another agent continue reading without
trusting hidden reasoning.
