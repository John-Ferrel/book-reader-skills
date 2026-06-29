# Anti-Laziness Obligations for Reader

Reader may produce an incomplete first reconstruction, but must not inflate its
status.

Minimum conditions before saying reconstruction is ready for independent review:

- active model files use claim cards
- claim cards include Evidence, Confidence, Alternative Interpretation, and
  What Would Change This Model
- notes use note item IDs with Type, Source, Confidence, and Content
- inference notes include Alternative and What Would Change This
- uncertainty notes include What Would Resolve This
- indexes are populated with evidence/status/role or explicitly deferred
- optional artifacts state purpose, status, and next action
- selected lenses handle core objects or explicitly defer them

Reader final status must distinguish:

- `source-ready`
- `reconstructed-not-reviewed`
- `self-checked`
- `review-required`
- `reviewed-fail`
- `revised-verification-required`
- `stable`
- `max-rounds-reached`

If no independent review has run, say:

```text
This workspace is reconstructed but not complete.
Next required action: run book-reviewer in a fresh session.
```

Forbidden:

- Reconstruction done => Complete
- Self-audit pass => Stable
- Files exist => Read
