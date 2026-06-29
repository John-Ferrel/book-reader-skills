# Workspace Model

The workspace is a method surface for evidence-driven reading. `model/` is the
center, but it is not a collection of unsupported opinions. Every model claim
should be inspectable through note items and source blocks.

| Layer | Location | Method role |
| --- | --- | --- |
| Source substrate | `source/` | Original source, extracted text, normalized text, metadata. |
| Evidence | `evidence/` | Source-map, block anchors, extraction warnings, source confidence. |
| Semantic units | `units/` | Agent-confirmed reading units; candidates are not final units. |
| Note items | `notes/` | Observation, paraphrase, inference, uncertainty, question, external context. |
| Integration paths | `threads/` | Cross-unit concepts, claims, motifs, examples, methods, tensions. |
| Reconstruction model | `model/` | Author problem, reader path, concept system, argument architecture, design, tradeoffs, edition layers. |
| Knowledge organization | `indexes/` | Navigation from claims/concepts/entities/design principles to notes and evidence. |
| Continuation planning | `guide/` | Dashboard, limits, review targets, next reading actions. |
| Audit | `review/` | Reviewer findings and revision plan. |
| Revision history | `revisions/` | Revision logs when a reviser applies changes. |

## Required core

Every initialized workspace has `README.md`, `workspace.json`, `source/`,
`evidence/`, `units/`, `notes/`, `threads/`, `model/`, `indexes/`, `guide/`, and
`review/`. `revisions/` appears when revision work is performed.

## Evidence anchor granularity

`evidence/source-map.json` contains both broad source anchors and block-level
anchors.

- EPUB keeps spine section anchors such as `src-006` and adds paragraph-like
  anchors such as `src-006-b012`.
- PDF keeps page anchors and adds paragraph-like anchors such as
  `src-p012-b003`.
- TXT/MD use heading/chunk anchors plus heading/paragraph/list block anchors.

Block items include `id`, `kind`, `parent`, `start_char`, `end_char`,
`block_type`, and `text_preview`. Their offsets refer to
`source/normalized.md`. They support evidence review; they are not final
semantic reading units.

## Traceability chain

The normal reconstruction chain is:

```text
source block -> note item -> model inference
```

`notes/` entries use stable item IDs (`obs-...`, `para-...`, `inf-...`,
`unc-...`, `q-...`, `ext-...`). `model/` claims cite both note item and source
block when possible.

## Optional artifacts

Technical books may add method, prerequisite, or example threads. Nonfiction
may add case or source threads. Fiction may add character, world, scene, motif,
or narration threads. These are additions, never prescribed empty folders.

Creator may create optional artifacts it believes are useful, but must include
purpose, status, and next action. Independent reviewer judges whether each is
useful, redundant, empty-shell, premature, duplicated, not-applicable,
deferred, or blocked.

## Knowledge organization and continuation

`indexes/` is a knowledge organization layer, not a checkbox. An index should
make model claims easier to inspect, compare, or revise. If it is not useful
yet, mark it deferred/blocked/not-applicable with a reason.

`guide/` is the continuation entry point for the next reader. It should say what
exists, what is weak, what is source-limited, and what to read next.

`review/` and `revisions/` are separate roles. Reviewer audits discipline and
writes review outputs. Reviser applies changes and records revision history.

## Workspace state

`workspace.json` is canonical machine-readable workspace metadata. README and
dashboard files are human-readable views. `workspace.json` contains:

- `workspace_stage`: `source-ready`, `reconstructed`, `revised`, `verified`,
  `stable`
- `audit_status`: `not-run`, `pass`, `warning`, `fail`, `source-limited`
- `coverage_depth`: `surface`, `usable`, `deep`
- `review_status`: `not-reviewed`, `self-checked`, `reviewed-fail`,
  `reviewed-warning`, `reviewed-pass`
- `revision_status`: `not-started`, `required`, `in-progress`, `applied`,
  `not-needed`
- `review_round`
- `max_review_rounds`
- `stability_status`: `unstable`, `stable`, `max-rounds-reached`
- `current_required_action`: `run-reconstruction`, `run-review`,
  `run-revise`, `run-verify`, `none`
- `last_reader_session`, `last_reviewer_session`, `last_reviser_session`
- `primary_lens`, `secondary_lenses`, `lens_rationale`
- `last_updated`
- links to `source/source-metadata.json` and `reports/validation-report.md`

Status describes current working state; it is not evidence for a model claim.
`validate` must not silently upgrade the stage. Reader/revision agents update
state after real work; reviewer agents only report stale state unless repair
mode is explicitly requested.

Strict validation checks README/dashboard state consistency against
`workspace.json` and fails on mismatch. Normal validation reports these as
warnings.
