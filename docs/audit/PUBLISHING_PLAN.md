# Publishing Plan

## 1. GitHub repo structure

Publish the method-first skill pack structure:

```text
README.md
AGENTS.md
pyproject.toml
docs/
examples/
skills/
tests/
```

Do not publish local private inputs or generated workspaces unless they are
safe public-domain examples.

## 2. Suggested repo name

Suggested names:

- `book-reader-skills`
- `book-reader-method`
- `book-reconstruction-skills`

Preferred: `book-reader-skills`.

## 3. What to include

Include:

- `README.md`
- `AGENTS.md`
- `pyproject.toml`
- `docs/`
- `examples/`
- `skills/`
- `tests/`
- `.gitignore`
- `LICENSE`
- `CHANGELOG.md` or GitHub release notes

## 4. What to exclude

Exclude:

- `books/`
- copyrighted EPUB/PDF/TXT/MD sources
- generated workspaces from copyrighted books
- `.venv/`
- `__pycache__/`
- `*.pyc`
- `/tmp` outputs
- personal machine paths
- secrets or API keys

## 5. Installation instructions

Recommended README install block:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

## 6. Usage examples

Intake:

```bash
python3 skills/book-intake/scripts/book_reader.py ingest \
  --input examples/sample-nonfiction.txt \
  --output /tmp/book-reader-demo

python3 skills/book-intake/scripts/book_reader.py validate \
  --workspace /tmp/book-reader-demo \
  --strict
```

Skill prompts:

```text
用 book-reader 读 examples/sample-nonfiction.txt
用 technical-book lens 读 examples/sample-technical.md
用 fiction-narrative lens 读 examples/sample-fiction.md
用 book-reviewer 审查 /tmp/book-reader-demo
根据 review/revision-plan-round-1.md 用 book-revise 修订
```

## 7. Release tag

Suggested first beta tag:

```text
v0.1.0-beta.1
```

If using simpler semver:

```text
v0.1.0
```

## 8. Versioning

Use semver-like versioning:

- Patch: docs/tests/runtime bugfixes that do not change workspace contract.
- Minor: skill protocol changes, new templates, new validator gates.
- Major: incompatible workspace model or CLI changes.

Current `pyproject.toml` version is `0.1.0`.

## 9. License recommendation

Recommended: MIT License for broad reuse.

Alternative: Apache-2.0 if explicit patent grant language is desired.

Do not publish without a LICENSE; otherwise reuse rights are ambiguous.

## 10. Future roadmap

Suggested roadmap items:

- Public-domain sample source and sample workspace.
- More end-to-end OpenCode/Codex run transcripts.
- Better docs for reviewer/reviser multi-session workflow.
- Optional packaging of CLI entry point.
- More robust EPUB/PDF extraction tests with safe fixtures.
- Clear contribution guide for adding lenses without polluting core invariants.
