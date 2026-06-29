# Anti-Laziness Taxonomy

Book Reader v2 assumes agents may produce plausible-looking but weak reading
artifacts. The method must make laziness visible, reviewable, failing, and
revisable.

## 1. Summary Masquerading as Notes

- Definition: notes summarize chapters without note item IDs.
- Symptoms: long prose, no observation/paraphrase/inference/uncertainty items.
- Why it matters: model claims cannot be traced.
- Reviewer check: sample notes for IDs, type, source, confidence, content.
- Required fix: rewrite as note items; mark coverage-level notes honestly.

## 2. Essay Masquerading as Model

- Definition: `model/` contains fluent analysis but no claim cards.
- Symptoms: paragraphs under headings, no Claim ID / Evidence / Confidence.
- Why it matters: claims cannot be audited or revised.
- Reviewer check: fail essay-only active model files.
- Required fix: convert to claim cards or mark deferred/blocked/not-applicable.

## 3. Unsupported Inference

- Definition: inference lacks source block or note item.
- Symptoms: “the author argues” without `Source` and `Note`.
- Why it matters: interpretation becomes unverifiable.
- Reviewer check: trace model claim -> note item -> source block.
- Required fix: add evidence, lower confidence, defer, or delete.

## 4. Confidence Omission

- Definition: important judgment lacks confidence.
- Symptoms: assertive model prose without high/medium/low/source-limited.
- Why it matters: weak and strong evidence look identical.
- Reviewer check: inspect claim cards and inference notes.
- Required fix: add calibrated confidence.

## 5. Alternative Omission

- Definition: inference lacks alternative interpretation.
- Symptoms: one reading presented as inevitable.
- Why it matters: reconstruction becomes brittle.
- Reviewer check: verify `Alternative Interpretation` or explain why not tested.
- Required fix: add credible alternative or mark as untested.

## 6. Completion Inflation

- Definition: reader claims complete after reconstruction without independent review.
- Symptoms: “done/stable/complete” with `review_status: not-reviewed` or self-checked.
- Why it matters: creator self-certifies quality.
- Reviewer check: workspace state and final status.
- Required fix: mark `review-required` and run fresh reviewer session.

## 7. Self-Audit Inflation

- Definition: self-audit pass is treated as independent review.
- Symptoms: `stability_status: stable` with `review_status: self-checked`.
- Why it matters: no role separation.
- Reviewer check: latest review report and workspace.json.
- Required fix: run independent review.

## 8. Artifact Inflation

- Definition: many artifacts/directories are created without cognitive value.
- Symptoms: README-only dirs, decorative files, duplicated indexes.
- Why it matters: workspace looks complete while hiding weak thinking.
- Reviewer check: artifact redundancy audit.
- Required fix: keep, populate, merge, move-to-guide, defer, remove, or collapse.

## 9. Index Decoration

- Definition: index is a word list or table with no evidence/status/role.
- Symptoms: concepts listed without source/note/confidence/role.
- Why it matters: indexes fail as navigation and audit tools.
- Reviewer check: inspect entries for evidence and cognitive value.
- Required fix: add evidence/status/role or defer.

## 10. Lens Skipping

- Definition: selected lens ignores its core objects.
- Symptoms: technical lens without notation/formal objects/dependencies; fiction
  lens without character/scene/motif tracking.
- Why it matters: lens creates false confidence.
- Reviewer check: lens compliance audit.
- Required fix: populate minimum lens objects or explicitly defer with reason.

## 11. Source Granularity Laziness

- Definition: broad chapter/page anchors support fine-grained claims.
- Symptoms: claim cites `src-006` rather than `src-006-b012`.
- Why it matters: evidence cannot be inspected precisely.
- Reviewer check: compare claim scope to source anchor granularity.
- Required fix: cite block anchors or mark source-limited.

## 12. Source-Limited Dishonesty

- Definition: extraction/source limits are ignored.
- Symptoms: claims about figures/tables/proofs when extraction warnings say lost.
- Why it matters: model overstates available evidence.
- Reviewer check: compare claims against limitations.
- Required fix: lower confidence, mark source-limited, add recovery plan.

## 13. External Context Pollution

- Definition: outside knowledge is mixed into source-supported model.
- Symptoms: modern claims presented as book evidence.
- Why it matters: source model becomes contaminated.
- Reviewer check: external-context labels and citations.
- Required fix: move to external-context note or remove from source model.

## 14. Revision Avoidance

- Definition: review issues are “fixed” by formatting without re-reading source.
- Symptoms: added labels but unchanged unsupported reasoning.
- Why it matters: review loop becomes cosmetic.
- Reviewer check: revision log lists source blocks re-read and claim changes.
- Required fix: re-read cited source/note items and revise substance.
