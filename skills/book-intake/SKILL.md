# Book Intake

Use this skill to mechanically prepare a source-ready Book Reader workspace.

CLI:

```bash
python3 skills/book-intake/scripts/book_reader.py ingest --input <book> --output <workspace>
python3 skills/book-intake/scripts/book_reader.py validate --workspace <workspace>
python3 skills/book-intake/scripts/book_reader.py info --workspace <workspace>
```

Responsibilities:

- ingest `.txt`, `.md`, `.epub`, and text-based `.pdf`
- normalize source text
- generate source metadata
- generate source-map section/page and block anchors
- generate unit candidates
- initialize workspace skeleton
- validate and report workspace facts

Forbidden:

- write author model
- infer author intention
- build concept system
- write argument architecture
- pretend source-limited material is complete

Read `references/intake-contract.md` before changing script behavior.
