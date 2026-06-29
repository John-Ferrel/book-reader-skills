# Examples

These samples are deliberately tiny. They exercise mechanical intake paths and
provide safe prompt targets; they are not benchmarks for full reconstruction.

```bash
python3 skills/book-intake/scripts/book_reader.py ingest \
  --input examples/sample-nonfiction.txt \
  --output /tmp/example-workspace
```

Then use a normal book-reader prompt and inspect how the agent turns source
blocks into note items and provisional `model/` claims.

Samples:

- `sample-nonfiction.txt`
- `sample-fiction.md`
- `sample-technical.md`

Legacy tiny samples `sample.txt` and `sample.md` may remain for compatibility
with local ad-hoc smoke commands, but tests and docs use the method-first names.
