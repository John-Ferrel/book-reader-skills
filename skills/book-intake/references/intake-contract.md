# Intake Contract

Book Intake is mechanical. It prepares evidence substrate for later reading.

It may:

- decode text with encoding fallback
- extract EPUB spine text and metadata
- extract text-based PDF pages
- normalize text into Markdown-like source
- create `source/source-metadata.json`
- create `evidence/source-map.json` with block-level anchors
- create `units/unit-candidates.md`
- create initial model/index/guide/review templates
- validate required structure and obvious mechanical defects

It must not:

- decide final semantic reading units
- write note-item content beyond templates
- infer author problem, concept system, argument architecture, or book design
- resolve source-limited interpretation in code
- create v1 legacy directories

Code fallback handles extraction uncertainty: encoding fallback, metadata
missing, PDF extraction warnings, degraded block extraction, and missing
dependencies.

Document fallback handles interpretation uncertainty and belongs in notes,
model, guide, review, or revision artifacts.
