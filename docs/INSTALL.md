# Install Book Reader Skills

Book Reader is both a Python helper/runtime project and an agent skill pack.
These are installed separately:

- `pip install -e .` installs Python runtime dependencies for intake helpers.
- `scripts/install_skills.py` installs agent skills into an OpenCode or generic
  agent-compatible skills directory.

## Quick install

OpenCode global:

```bash
python3 scripts/install_skills.py --target opencode-global
```

OpenCode project-local:

```bash
python3 scripts/install_skills.py --target opencode-project --project /path/to/project
```

Generic agent-compatible global:

```bash
python3 scripts/install_skills.py --target agents-global
```

Generic project-local:

```bash
python3 scripts/install_skills.py --target agents-project --project /path/to/project
```

## Python runtime dependencies

Install helper/runtime dependencies when you want to run intake commands:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

The runtime CLI remains:

```bash
python3 skills/book-intake/scripts/book_reader.py ingest --input <book-path> --output <workspace-path>
python3 skills/book-intake/scripts/book_reader.py validate --workspace <workspace-path> --strict
python3 skills/book-intake/scripts/book_reader.py info --workspace <workspace-path>
```

## Copy vs symlink

Default mode is copy:

```bash
python3 scripts/install_skills.py --target opencode-global --mode copy
```

Copy mode is more stable for normal users because the installed skills remain
available even if the cloned repo moves.

Symlink mode is useful for development:

```bash
python3 scripts/install_skills.py --target opencode-global --mode symlink
```

With symlinks, updates in this repo are immediately visible from the installed
skills directory.

## Overwrite and dry-run

Existing installed skill directories are not overwritten by default. Use
`--force` to replace them:

```bash
python3 scripts/install_skills.py --target opencode-global --force
```

Preview the installation without writing:

```bash
python3 scripts/install_skills.py --target opencode-global --dry-run
```

## Verify

OpenCode global install:

```bash
ls ~/.config/opencode/skills
```

OpenCode project-local install from the target project:

```bash
ls .opencode/skills
```

Generic agent-compatible global install:

```bash
ls ~/.agents/skills
```

Generic project-local install from the target project:

```bash
ls .agents/skills
```

Then try a skill prompt in an agent that supports this layout:

```text
用 book-reader 读 examples/sample-nonfiction.txt
```

## Installed skill names

This repo installs the following skill package names:

- `book-reader`
- `book-intake`
- `book-reconstruct`
- `book-reviewer`
- `book-revise`
- `edition-revision`
- `essay-anthology`
- `external-context`
- `fiction-narrative`
- `nonfiction-argument`
- `reference-book`
- `source-limited`
- `technical-book`

Lens skills under `skills/lenses/` are flattened during installation. For
example:

```text
skills/lenses/technical-book/SKILL.md -> <target>/technical-book/SKILL.md
```

## Uninstall

Uninstall by manually deleting the installed skill folders from the target
skills directory. Example:

```bash
rm -rf ~/.config/opencode/skills/book-reader
rm -rf ~/.config/opencode/skills/book-intake
```

Delete only the skill folders you installed. Do not delete unrelated skills in
the same target directory.

## Safety

The installer only installs directories that contain `SKILL.md` under
`skills/**/SKILL.md`. It does not install:

- `books/`
- `workspaces/`
- `docs/`
- `tests/`
- `examples/`
