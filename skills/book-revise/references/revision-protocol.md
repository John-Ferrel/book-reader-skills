# Revision Protocol

Revision applies review findings without erasing reasoning history.

1. Read `review/review-report-round-<n>.md` and
   `review/revision-plan-round-<n>.md`.
2. For each revision, inspect cited source blocks and note items.
3. Update notes/model/indexes/guide only where evidence warrants.
4. Preserve prior claims when useful; mark superseded claims explicitly.
5. Update `workspace.json` after actual state changes.
6. Write `revisions/revision-log-round-<n>.md`.
7. Set `current_required_action: run-verify`.

Revision log entries should include:

- revision ID
- review finding addressed
- files changed
- evidence inspected
- old claim status
- new or revised claim
- remaining uncertainty
