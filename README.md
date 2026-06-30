# Book Reader Skills v2

Book Reader Skills is an auditable reading workflow for agents. It organizes a
whole-book read into an evidence-linked reconstruction workspace that can be
reviewed, revised, and verified.

It is not a normal summary tool. It is not a tool that converts a book into a
reusable skill. It is not a parser framework or RAG ingestion pipeline. Runtime
scripts prepare source evidence; agent skills guide the reading workflow.

Core loop:

```text
source evidence -> claim cards / note items -> reconstruction model -> independent review -> revision -> verification review
```

Default output is a workspace, not a summary. The workspace is not complete
after reconstruction alone: an independent review and follow-up revision are
part of the method.

[中文说明](docs/README.zh-CN.md)

Anti-laziness hardening is part of the method: model essays without claim
cards, summary-only notes, decorative indexes, skipped lens obligations, and
self-certified completion are review findings, not acceptable output.

## Quickstart

Clone the repo:

```bash
git clone https://github.com/John-Ferrel/book-reader-skills.git
cd book-reader-skills
```

Create a virtual environment and install runtime dependencies:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

Run the test suite:

```bash
python3 -m unittest tests/test_helpers.py -v
python3 -m py_compile scripts/install_skills.py skills/book-intake/scripts/*.py
```

Install the agent skills globally for OpenCode:

```bash
python3 scripts/install_skills.py --target opencode-global
```

Or install them into a specific OpenCode project:

```bash
python3 scripts/install_skills.py --target opencode-project --project /path/to/project
```

Then start a new OpenCode session and ask the agent to use the skills:

```text
Use book-reader to read examples/sample-nonfiction.txt.
Use book-intake to ingest examples/sample-nonfiction.txt into a source-ready workspace.
```

The agent should use the native `skill` tool when `book-reader` or
`book-intake` appears in OpenCode `available_skills`.

## Install Details

Book Reader has two installation layers:

- Python runtime dependencies for helper scripts.
- Agent skills for OpenCode / Codex / generic agent-compatible skill layouts.

### Python runtime dependencies

Python 3.10+ is required.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

Dependencies include EPUB/PDF extraction support:

- `ebooklib`
- `beautifulsoup4`
- `lxml`
- `pypdf`

### Agent skills

OpenCode global install:

```bash
python3 scripts/install_skills.py --target opencode-global
```

OpenCode project-local install:

```bash
python3 scripts/install_skills.py --target opencode-project --project /path/to/project
```

Generic agent-compatible global install:

```bash
python3 scripts/install_skills.py --target agents-global
```

Generic project-local install:

```bash
python3 scripts/install_skills.py --target agents-project --project /path/to/project
```

By default the installer copies skill packages. Use `--mode symlink` for
development installs and `--dry-run` to preview without writing.

Copying to `.opencode/skills/` is the filesystem install step. OpenCode native
discovery is confirmed only when a new or restarted OpenCode session lists the
skills in the native `skill` tool's `available_skills` section.

If files exist but OpenCode does not list the skills, check that `SKILL.md` is
uppercase, starts with YAML frontmatter, includes `name` and `description`,
uses a `name` matching the installed directory, and is not hidden by
`permission.skill` or disabled with `tools.skill: false` in OpenCode config.

See `docs/INSTALL.md` for full install, native discovery verification,
troubleshooting, and uninstall instructions.

## Update / Upgrade

For an existing clone:

```bash
git pull
. .venv/bin/activate
pip install -e .
```

Overwrite an existing OpenCode global skill install:

```bash
python3 scripts/install_skills.py --target opencode-global --force
```

Overwrite an existing OpenCode project-local install:

```bash
python3 scripts/install_skills.py --target opencode-project --project /path/to/project --force
```

After updating skills, start a new OpenCode session or restart the current one.
Existing workspaces are not rerun automatically; ask the agent to rerun the
relevant intake, reconstruction, review, revision, or verification workflow.

## Intake CLI

Runtime intake lives under `book-intake`:

```bash
python3 skills/book-intake/scripts/book_reader.py ingest \
  --input examples/sample-nonfiction.txt \
  --output /tmp/book-reader-method-nonfiction

python3 skills/book-intake/scripts/book_reader.py validate \
  --workspace /tmp/book-reader-method-nonfiction

python3 skills/book-intake/scripts/book_reader.py validate \
  --workspace /tmp/book-reader-method-nonfiction \
  --strict

python3 skills/book-intake/scripts/book_reader.py info \
  --workspace /tmp/book-reader-method-nonfiction
```

Supported source formats:

- `.txt`
- `.md`
- `.epub`
- text-based `.pdf`

No OCR is implemented. PDF layout, figures, and tables may be degraded. EPUB
images, tables, styling, and some notes may be flattened or lost.

## Skill pack use

Use `book-reader` as the orchestrator:

```text
用 book-reader 读 examples/sample-nonfiction.txt
用 book-intake ingest examples/sample-nonfiction.txt into a source-ready workspace
用 technical-book lens 读这本概率论教材
用 fiction-narrative lens 读这本小说
用 book-reviewer 审查 workspaces/book-x
根据 review/revision-plan.md 用 book-revise 修订
```

Core skills:

- `skills/book-reader/`: orchestrator and lens routing
- `skills/book-intake/`: mechanical ingest / validate / info
- `skills/book-reconstruct/`: core reading and reconstruction method
- `skills/book-reviewer/`: inference discipline audit
- `skills/book-revise/`: review-driven revision protocol
- `skills/lenses/`: optional reading lenses

Lens skills are installed flat under the target skills directory. For example,
`skills/lenses/technical-book/SKILL.md` installs as
`.opencode/skills/technical-book/SKILL.md`, and its frontmatter name is
`technical-book`.

## Method invariants

The core traceability chain is:

```text
source block -> note item -> model inference
```

Every important model claim should cite:

- source block
- note item
- unit
- confidence
- alternative interpretation
- what would change the model

Model files use claim cards. Essay-only model prose should be flagged in
review.

Strict validation catches mechanical laziness such as active model files
without claim cards, missing claim-card fields, note files without note item
IDs, template-only indexes, self-audit treated as stable, and README/dashboard
state mismatch. Reviewer catches semantic laziness.

Artifacts are views over thinking, not boxes to fill. If an artifact does not
improve reconstruction, omit it or mark it deferred/blocked/not-applicable with
a reason.

## Code fallback vs document fallback

Code fallback handles extraction uncertainty:

- encoding fallback
- EPUB metadata missing
- PDF text extraction warning
- degraded block extraction
- dependency missing

Document fallback handles interpretation uncertainty:

- unresolved author problem
- competing concept models
- weak argument architecture
- source-limited claims
- external context needed

Scripts must not write author models, concept systems, argument architecture,
or semantic conclusions.

## Tests

```bash
python3 -m unittest tests/test_helpers.py -v
python3 -m py_compile scripts/install_skills.py skills/book-intake/scripts/*.py
```

## Current limits

- Intake supports common text formats but not OCR.
- Helpers validate mechanical structure, not reading quality.
- Reviewer audits do not repair workspaces by default.
- Reviewer/reviser loops run up to `max_review_rounds` unless stable earlier.
- Lenses adapt the method; they are not required for every book.
