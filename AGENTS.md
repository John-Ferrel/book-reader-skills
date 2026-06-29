# Agent Instructions

This repository is a method-first Book Reader v2 skill pack.

## Core rule

Book Reader is an evidence-driven reading methodology for agents:

```text
source block -> note item -> model inference
```

Runtime scripts prepare evidence workspaces. Semantic reading belongs in
skills, references, templates, and agent judgment.

## Do not reintroduce v1 legacy

Do not create or restore:

- `chapters/`
- `reading-passes/`
- `projections/`
- v1 compatibility state machines
- helper-first synthesis behavior

## Runtime scripts

Use the new intake path:

```bash
python3 skills/book-intake/scripts/book_reader.py ingest --input <book> --output <workspace>
python3 skills/book-intake/scripts/book_reader.py validate --workspace <workspace>
python3 skills/book-intake/scripts/book_reader.py info --workspace <workspace>
```

Tests must use `skills/book-intake/scripts`, not the old
`skills/book-reader/helpers` path.

Scripts are mechanical only. They may extract, normalize, build source maps,
create skeletons, and validate structure. They must not write author models,
concept systems, argument architecture, or semantic conclusions.

## Reviewer and reviser separation

Reviewer writes only:

- `review/review-report.md`
- `review/revision-plan.md`

Reviewer does not modify `workspace.json`, `source/`, `evidence/`, `units/`,
`notes/`, `threads/`, `model/`, `indexes/`, `guide/`, `reports/`, or root
`README.md` unless the user explicitly requests repair mode.

Reviser reads review outputs, applies changes, updates state, and writes a
revision log.
