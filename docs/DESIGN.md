# Design: Book Reader Skills v2

## Thesis

**Book surface text → evidence-linked reading workspace → reconstructed author /
book design model.** The product is a usable, revisable model of how a book is
trying to work, not a pile of notes or a claim of complete comprehension.

## Goals

- Help an agent infer a book’s problem, concepts, argument, design, reader path,
  and assumptions from textual evidence.
- Make every consequential inference evidence-linked, confidence-labelled,
  alternative-aware, and revisable.
- Produce a human-readable workspace that supports the next reading decision.
- Keep the entry prompt short; the skill performs a reasonable first pass.

## Non-goals

- Exhaustive summarization, paragraph coverage accounting, or a 1:1 note for
  every heading.
- OCR, sophisticated EPUB parsing, RAG, embeddings, or vector storage.
- Helpers that decide semantic units, interpret a book, or write synthesis.
- Recovery, migration, or compatibility with v1 workspaces.

## Method-first architecture

Book Reader is now a composable skill pack:

- `book-reader` routes the user request.
- `book-intake` prepares the evidence workspace mechanically.
- `book-reconstruct` performs the core reading method.
- `book-reviewer` audits inference discipline.
- `book-revise` applies review-driven revisions.
- `lenses/*` adapt the method to book type or source condition.

Method comes first; tools come second. Runtime scripts are necessary for
practical source handling, but they are not the semantic reader.

## Agent-first boundary

Helpers may extract/normalize plain text, create the skeleton, store files, and
validate paths. The agent discovers structure, groups semantic units, judges
evidence, reconstructs models, recognizes alternatives, and plans deep reading.

Code fallback handles extraction uncertainty. Document fallback handles
interpretation uncertainty. Code must not fill semantic gaps.

## Difference from v1

v2 does not inherit v1’s helper-first workflow, chapter / reading-unit coverage
machinery, synthesis patching, contract/state complexity, or legacy surfaces.
It does not use `chapters/`, `reading-passes/`, or `projections/`. A small
manifest communicates only current workspace stage, audit status, and depth;
it does not prove understanding.

## First-run standard

A first run is useful when it makes the current reconstruction inspectable:
surface structure, core problem, concept system, argument architecture, reader
path, central versus supporting modules, confidence, alternatives, source gaps,
and an explicit next-reading route. It is allowed—and expected—to remain
partial.
