# Method-Level Acceptance

Acceptance is not a file-existence check. A passing full read shows that the
method produced an inspectable, revisable reconstruction workspace and completed
the review/revise/verify loop honestly.

## Pass for reconstruction workspace

- Source evidence exists.
- Source map is usable and contains block-level anchors when extraction allows.
- Semantic units are confirmed or clearly pending.
- Note items distinguish observation, paraphrase, inference, uncertainty,
  question, and external context.
- Important model claims use claim cards and cite source block, note item, and
  unit.
- Confidence, alternative interpretation, and revision condition are present.
- Indexes are useful or explicitly deferred/blocked/not-applicable with reason.
- Dashboard tells the next reader what exists, what is weak, and what to do.
- Workspace state is honest and not promoted by validation alone.

## Pass for full read

- Reconstruction exists.
- Independent review completed.
- Fail findings revised or explicitly accepted/deferred with evidence.
- Verification review is pass or warning.
- Workspace is marked `stable` or `max-rounds-reached` honestly.
- Creator did not self-certify artifact usefulness or completion.

## Fail cases

- Reader claims complete without independent review.
- Self-audit is treated as fresh independent review.
- Reviewer modifies non-review files without explicit repair instruction.
- Revise happens without a review plan.
- Repeated review finds the same high severity issues without escalation.
- Optional artifacts are self-certified useful without reviewer judgment.
- Max rounds reached but workspace claims stable.
- Output is only a summary.
- `model/` contains unsupported claims or essay-only prose without claim cards.
- Author intention is asserted as fact.
- Notes are only chapter summaries.
- Indexes are empty placeholders.
- Scripts create semantic conclusions.
- Process is treated as checklist rather than method.
- Lens-specific rule is forced into the core method.
- v1 legacy directories appear: `chapters/`, `reading-passes/`,
  `projections/`.

## Mechanical smoke

Mechanical smoke checks intake/runtime behavior only:

```bash
python3 -m unittest tests/test_helpers.py -v
python3 -m py_compile skills/book-intake/scripts/*.py
python3 skills/book-intake/scripts/book_reader.py ingest --input examples/sample-nonfiction.txt --output /tmp/book-reader-loop-nonfiction
python3 skills/book-intake/scripts/book_reader.py validate --workspace /tmp/book-reader-loop-nonfiction
python3 skills/book-intake/scripts/book_reader.py validate --workspace /tmp/book-reader-loop-nonfiction --strict
python3 skills/book-intake/scripts/book_reader.py info --workspace /tmp/book-reader-loop-nonfiction
```

Smoke passing does not prove reconstruction quality.
