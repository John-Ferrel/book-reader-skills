# Run Protocol

Default Book Reader flow:

```text
intake -> reconstruct -> self-check -> independent review -> revise -> verification review
```

Repeat review/revise until reviewer marks stable or `max_review_rounds` is
reached. Default `max_review_rounds` is 3.

Do not report full completion after reconstruction. If independent review has
not run, say:

```text
Reconstruction completed, but workspace is not complete until independent review is run.
Next required action: run book-reviewer in a fresh session.
```

Ideal mode uses separate reader, reviewer, and reviser sessions. Single-agent
fallback may self-check, but self-check never equals independent review and
never marks stable.

Stable requires latest independent review pass or acceptable warning, no
unresolved high severity issues, no required revision, consistent state, and no
repeated high severity issue across rounds.

If `review_round >= max_review_rounds` and fail/warning remains, mark
`max-rounds-reached`, not stable.
