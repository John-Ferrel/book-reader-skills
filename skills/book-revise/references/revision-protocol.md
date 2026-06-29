# Revision Protocol

Revision applies review findings without erasing reasoning history.

1. Read `review/review-report-round-<n>.md` and
   `review/revision-plan-round-<n>.md`.
2. For each revision, inspect cited source blocks and note items.
3. Update notes/model/indexes/guide only where evidence warrants.
4. For unsupported claims: add evidence, lower confidence, convert to
   uncertainty, mark deferred, or delete.
5. For redundant artifacts: merge, move-to-guide, defer, remove, or collapse as
   the review plan requires.
6. Preserve prior claims when useful; mark superseded claims explicitly.
7. Update `workspace.json` after actual state changes.
8. Write `revisions/revision-log-round-<n>.md`.
9. Set `workspace_stage: revised`, `revision_status: applied`, and
   `current_required_action: run-verify`.

Do not merely add Evidence/Confidence labels without re-reading source. Do not
claim stable after review fail.

Revision log entries should include:

- revision ID
- review finding addressed
- files changed
- evidence inspected
- old claim status
- new or revised claim
- remaining uncertainty
