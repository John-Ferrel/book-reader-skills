# Review Report — {{BOOK_TITLE}}

Review Round: <n>
Audit Result: pass / warning / fail
Stability Judgment: stable / unstable
Required Revision: yes / no
Next Required Action: run-revise / run-verify / none

Reviewer boundary: write only files under `review/` unless the user explicitly
requested repair mode.

## Scope and Source Limits

## Boundary Check

- Non-review files modified by reviewer: no / yes
- If yes, explicit repair instruction:

## Findings by Severity

| Severity | Finding | Affected files | Evidence | Risk to model | Required action |
| --- | --- | --- | --- | --- | --- |

## Traceability Audit

- Model claims cite note items and source blocks: pass / warning / fail
- Note items cite source blocks or source-limited reasons: pass / warning / fail
- Inference vs source fact are separated: pass / warning / fail
- Confidence and alternatives are present: pass / warning / fail
- Weak traceability is flagged: pass / warning / fail
- Claim cards are used instead of essay-only model prose: pass / warning / fail

## Anti-Laziness Audit

Check and report:

1. Model files contain substantial prose but lack claim cards.
2. Model claims lack Evidence / Confidence / Alternative.
3. Unit notes are chapter summaries rather than note items.
4. Note items lack stable IDs.
5. Source anchors are too coarse for the claim.
6. Indexes are empty, generic, duplicated, or only decorative.
7. Optional artifacts exist but add no cognitive value.
8. Directories contain only README.md without substantive artifact or clear deferred status.
9. Lens outputs were opened but not populated.
10. Technical lens skipped notation / formal objects / dependency map when needed.
11. Fiction lens skipped characters / arcs / motifs when needed.
12. External context polluted source-supported model.
13. Review/revision loop was bypassed.

## Artifact Redundancy Audit

Artifact redundancy is reviewer-judged, not creator-self-certified.

| Artifact | Purpose | Status | Evidence of Use | Cognitive Value | Redundancy Judgment | Action | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- |

Judgment: useful / redundant / empty-shell / premature / duplicated / not-applicable / deferred / blocked

Action: keep / populate / merge / move-to-guide / defer / remove / collapse

## Lens Compliance Audit

- Primary lens:
- Secondary lenses:
- Lens rationale:
- Lens creep findings:
- Lens-specific artifacts opened but not used:

## State Consistency Audit

- README stage matches `workspace.json`: pass / warning / fail
- Dashboard stage matches `workspace.json`: pass / warning / fail
- Review status matches latest review report: pass / warning / fail
- Revision status matches latest revision log: pass / warning / fail
- Current required action is consistent: pass / warning / fail

## Audit Result

pass / warning / fail
