# Run Protocol

Book Reader full-read is a review loop, not a single creator pass.

```text
reader reconstructs
-> independent reviewer audits
-> reviser re-reads / revises
-> independent reviewer verifies
-> repeat until stable or max rounds reached
```

Default maximum:

```text
max_review_rounds: 3
```

## Default full-read flow

1. Intake.
2. Reconstruction read.
3. Self-check.
4. Independent review.
5. Re-read / revise.
6. Independent verification review.
7. Repeat until stable or max rounds reached.

## Status vocabulary

Workspace stage:

- `source-ready`
- `reconstructed`
- `revised`
- `verified`
- `stable`

Review status:

- `not-reviewed`
- `self-checked`
- `reviewed-fail`
- `reviewed-warning`
- `reviewed-pass`

Revision status:

- `not-started`
- `required`
- `in-progress`
- `applied`
- `not-needed`

Stability status:

- `unstable`
- `stable`
- `max-rounds-reached`

Required action:

- `run-reconstruction`
- `run-review`
- `run-revise`
- `run-verify`
- `none`

## Role rules

Reader can reconstruct and self-check, but cannot self-certify stability.

Reviewer audits independently and writes round-specific review outputs:

- `review/review-report-round-<n>.md`
- `review/revision-plan-round-<n>.md`

Reviewer may update latest copies under `review/`, but must not modify
non-review files unless the user explicitly requests repair mode.

Reviser reads `review/revision-plan-round-<n>.md`, re-reads relevant source
blocks, applies evidence-backed changes, writes
`revisions/revision-log-round-<n>.md`, and updates `workspace.json`.

## Completion rule

Full read is not complete after reconstruction alone.

If no independent review has run, report:

```text
Reconstruction completed, but workspace is not complete until independent review is run.
Next required action: run book-reviewer in a fresh session.
```

Self-check is allowed in single-agent fallback, but status remains
`self-checked`, not independently reviewed or stable.

## Stable condition

Mark `stable` only when:

- latest independent review is pass or acceptable warning
- no unresolved high severity issues remain
- revision-required = no
- workspace state is consistent
- the same high severity issue is not repeated across rounds

## Max rounds reached

Mark `max-rounds-reached` only when:

- `review_round >= max_review_rounds`
- review still has unresolved fail/warning findings
- workspace does not claim stable

Max rounds reached is an honest stop condition, not success.
