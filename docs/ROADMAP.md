# Roadmap

This roadmap keeps Book Reader v2 method-first. Future work should improve
evidence-driven reading discipline without turning the project into an OCR,
RAG, or parser research project by default.

## Near-term

- Add a public-domain sample workspace that demonstrates the full
  read/review/revise/verify loop.
- Add more safe EPUB/PDF fixtures for runtime tests.
- Add better OpenCode/Codex run examples showing:
  - default reconstruction reading
  - independent reviewer audit
  - reviser re-read and repair
  - verification review
- Add optional sample transcripts from safe, redistributable texts.
- Add a contribution guide for lenses that explains how to extend reading
  viewpoints without polluting core invariants.

## Runtime and packaging

- Add a packaged CLI entry point so users can run `book-reader` without
  referencing script paths.
- Expand extraction tests with safe fixtures while keeping helpers mechanical.
- Improve dependency and installation docs for common Python environments.

## Documentation

- Add a compact architecture diagram.
- Add more examples of valid claim cards, note items, and reviewer findings.
- Add more examples of acceptable deferred / blocked / not-applicable artifacts.

## Explicitly out of default scope

- OCR is not planned by default.
- RAG and vector database ingestion are not planned by default.
- Complex parser research is not planned by default.

These may be considered later only under explicit future scope, and they should
not weaken the core rule:

```text
source block -> note item -> model inference
```
