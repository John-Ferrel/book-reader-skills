# Release Notes: v0.1.0-beta.1

Book Reader v2 v0.1.0-beta.1 is the first beta candidate of a method-first,
evidence-driven reading skill pack for agents.

## Positioning

Book Reader is not a generic summary generator, parser-only tool, OCR pipeline,
or RAG ingestion framework. It is a reading methodology that helps agents turn
book surface text into a reconstruction workspace that is evidence-linked,
reviewable, revisable, and suitable for continued deep reading.

Core method:

```text
source evidence -> note items -> reconstruction model -> independent review -> revise / re-read -> verify
```

## Included in this beta

- Method-first skill-pack architecture.
- `book-reader` orchestrator skill.
- `book-intake` runtime skill and CLI.
- `book-reconstruct` evidence-driven reconstruction method.
- `book-reviewer` inference-discipline audit skill.
- `book-revise` revision protocol skill.
- Lens skills for technical, nonfiction argument, fiction narrative, anthology,
  reference, source-limited, edition/revision, and external-context reading.
- Intake support for:
  - `.txt`
  - `.md`
  - `.epub`
  - text-based `.pdf`
- Source metadata and source-map / block-anchor generation.
- Workspace skeleton generation.
- Model claim-card discipline.
- Note item traceability expectations.
- Review / revise / verify loop protocol.
- Anti-laziness taxonomy, reviewer audit, and strict validator gates.

## Runtime CLI

Primary intake commands:

```bash
python3 skills/book-intake/scripts/book_reader.py ingest --input <book-path> --output <workspace-path>
python3 skills/book-intake/scripts/book_reader.py validate --workspace <workspace-path>
python3 skills/book-intake/scripts/book_reader.py validate --workspace <workspace-path> --strict
python3 skills/book-intake/scripts/book_reader.py info --workspace <workspace-path>
```

## Known limitations

- v0.1.0-beta.1 does not guarantee perfect zero-shot book understanding.
- The method creates a disciplined, reviewable, revisable workspace; reading
  quality still depends on agent execution and independent review.
- PDF support is text-based only. Scanned PDFs are not OCRed.
- EPUB extraction may flatten footnotes/endnotes and may lose images, tables,
  styling, or complex layout.
- Source extraction helpers are mechanical and must not infer author intent,
  concept systems, or argument architecture.
- Strict validation catches mechanical laziness; semantic laziness is handled
  by reviewer audit.
- Generated workspaces from copyrighted books should not be published.

## Release status

This is a beta release candidate intended for practical agent use, testing, and
iteration. It is stable enough to publish as v0.1.0-beta.1 after release hygiene
checks confirm that no private or copyrighted source inputs are included.
