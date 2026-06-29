# Tests

The test suite has no third-party dependency:

```bash
python3 -m unittest tests/test_helpers.py -v
```

It verifies only the minimal helper boundary: normalized UTF-8 text, creation
of a model-centered workspace skeleton, manifest defaults, and structural
validation. It does not—and cannot—grade an agent’s reading judgment.

Runtime tests use:

```text
skills/book-intake/scripts/book_reader.py
```

They must not depend on the old `skills/book-reader/helpers` path.
