# Reconstruction Model

## What “reconstructing the back end” means

The visible book is a surface: headings, paragraphs, examples, scenes,
footnotes, figures, and sequence. Reconstruction asks what design those
surfaces plausibly implement. It is an evidence-linked interpretation, not
mind-reading.

Each model artifact must distinguish source facts, paraphrases, inferences,
speculation, and external context. It names its evidence, confidence,
alternatives, and the observations that would revise it.

## Model dimensions

| Artifact | Question |
| --- | --- |
| Author problem | What problem does the book appear designed to solve? |
| Reader model | What does it assume, teach, correct, or withhold from its reader? |
| Concept system | What are the underlying concepts and relations? |
| Argument architecture | How do claims, dependencies, objections, examples, and turns work? |
| Book design | What kind of book is it, and which modules are core or supporting? |
| Reader path | How does sequencing change the reader’s understanding? |
| Assumptions and tradeoffs | What constraints, choices, omissions, historical limits, or self-corrections matter? |
| Edition / revision layers | Do original, revised, retrospective, appendix, editor, or translator layers change the model? |

`model/` stores author problem, concept system, argument architecture, book
design, reader path, assumptions/tradeoffs, and edition/revision layers. The
reader model is recorded in `reader-path.md` and may be expanded when material
warrants it.

Every material model claim should cite both a note item and a source block. If
only the source block is available, mark `Traceability: weak` and explain that
no note item exists yet.

## Confidence and alternatives

Use `high` when several clear anchors converge, `medium` for a plausible but
incomplete pattern, `low` for a tentative reading, and `source-limited` when
the available source cannot carry the conclusion. A strong alternative reading
is not a defect: it belongs beside the main inference. Historical or reception
claims are external context and require a source or explicit uncertainty.

## Revision logic

The model changes when new units, counter-evidence, source corrections, or a
better explanation changes the interpretation. The agent records what would
change a claim before treating it as settled.
