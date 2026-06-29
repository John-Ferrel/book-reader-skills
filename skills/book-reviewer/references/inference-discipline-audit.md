# Inference Discipline Audit

Audit whether the workspace is evidence-driven and revisable.

Use `anti-laziness-audit.md` as a required companion check.

Check:

- model claims cite note items and source blocks
- note items cite source blocks or source-limited reasons
- observation, paraphrase, inference, and uncertainty are separated
- confidence labels are calibrated
- alternative interpretations are present
- revision conditions are meaningful
- source-limited claims are honest
- indexes are useful or explicitly deferred/blocked/not-applicable
- competing models are represented when evidence supports them
- edition/revision layers are handled when present
- model files use claim cards rather than essay-only prose
- indexes have cognitive value regardless of Markdown table/list format
- optional artifacts are useful or correctly marked, rather than empty-shell or
  decorative
- review/revision loop was not bypassed

Reviewer audits method discipline, not whether it personally agrees with the
reading.

## Anti-laziness audit

Check:

1. Model files contain substantial prose but lack claim cards.
2. Model claims lack Evidence / Confidence / Alternative.
3. Unit notes are chapter summaries rather than note items.
4. Note items lack stable IDs.
5. Source anchors are too coarse for the claim.
6. Indexes are empty, generic, duplicated, or only decorative.
7. Optional artifacts exist but add no cognitive value.
8. Directories contain only README.md without substantive artifact or clear
   deferred status.
9. Lens outputs were opened but not populated.
10. Technical lens skipped notation / formal objects / dependency map when needed.
11. Fiction lens skipped characters / arcs / motifs when needed.
12. External context polluted source-supported model.
13. Review/revision loop was bypassed.

## Artifact redundancy audit

For non-core artifacts, judge:

- Artifact
- Purpose
- Status
- Evidence of Use
- Cognitive Value
- Redundancy Judgment
- Action
- Reason

Judgment: useful / redundant / empty-shell / premature / duplicated /
not-applicable / deferred / blocked.

Action: keep / populate / merge / move-to-guide / defer / remove / collapse.

Artifact redundancy is reviewer-judged, not creator-self-certified.

## Technical book checks

When the technical lens is primary or secondary, check:

- Did the reader skip notation?
- Did the reader skip formulas/theorems/algorithms?
- Did the reader pretend derivations were read?
- Are proof details honestly deferred?
- Are examples linked to concepts?
