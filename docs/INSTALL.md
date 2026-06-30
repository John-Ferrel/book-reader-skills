# Install Book Reader Skills

Book Reader is both a Python helper/runtime project and an agent skill pack.
These are installed separately:

- `pip install -e .` installs Python runtime dependencies for intake helpers.
- `scripts/install_skills.py` installs agent skills into an OpenCode or generic
  agent-compatible skills directory.

Copying skill directories is only the filesystem install step. OpenCode native
discovery happens when OpenCode loads valid `SKILL.md` files and lists them in
the native `skill` tool's `available_skills` section.

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

First verify the skill directories were copied.

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

For OpenCode native discovery, start a new OpenCode session or restart the
current one after installing. The native `skill` tool description should include
an `available_skills` section with entries such as:

```text
book-reader
book-intake
technical-book
```

Filesystem visibility alone does not prove OpenCode has registered the skills
for the active session.

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

Each installed `SKILL.md` starts with OpenCode-compatible YAML frontmatter. The
frontmatter `name` must match the installed directory name, so flattened lens
skills use names such as `technical-book`, not `lenses/technical-book`.

## Troubleshooting OpenCode discovery

If the directory exists but the skill does not appear in native
`available_skills`, check:

- `SKILL.md` is spelled exactly in uppercase.
- `SKILL.md` starts with YAML frontmatter.
- Frontmatter contains both `name` and `description`.
- Frontmatter `name` equals the installed directory name.
- `description` is non-empty.
- A new or restarted OpenCode session is using the project where skills were
  installed.
- `opencode.jsonc`, `opencode.json`, or agent config does not set
  `permission.skill` to `deny` for these names.
- The agent has not disabled the native skill tool with `tools.skill: false`.

Seeing files under `.opencode/skills/` means the copy step worked; it does not
by itself confirm native skill discovery.

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
