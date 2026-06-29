# Reviewer Boundary

Default reviewer write boundary:

- `review/review-report.md`
- `review/revision-plan.md`

Reviewer must not modify:

- `workspace.json`
- `source/`
- `evidence/`
- `units/`
- `notes/`
- `threads/`
- `model/`
- `indexes/`
- `guide/`
- `README.md`
- `reports/`

If reviewer finds stale metadata, empty indexes, weak traceability, or missing
state updates, it records findings with severity, affected files, evidence, and
recommended revision. It does not repair them unless repair mode is explicitly
requested.
