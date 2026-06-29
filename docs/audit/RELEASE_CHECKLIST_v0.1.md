# v0.1 Release Checklist

## Required

- [x] tests pass
- [x] smoke passes
- [x] README usable
- [ ] LICENSE exists
- [ ] no copyrighted book content included in release
- [ ] no generated workspaces committed or published unless public-domain
- [ ] no personal paths / secrets
- [x] pyproject / dependencies valid
- [x] examples safe
- [ ] release notes written
- [ ] CHANGELOG or GitHub release changelog prepared
- [ ] roadmap prepared
- [ ] `AGENTS.md` aligned with round-specific reviewer output convention

## Publication hygiene

- [x] `books/` ignored by git
- [ ] verify `books/` is not uploaded to GitHub
- [ ] verify `workspaces/` is excluded or contains only safe public-domain examples
- [ ] remove local `__pycache__` before packaging if building an archive manually
- [ ] confirm no `.venv`, temp output, or large binary artifacts are included

## Optional

- [ ] demo gif / screenshots
- [ ] sample workspace generated from public-domain text
- [ ] GitHub topics
- [ ] issue templates
- [ ] contributing guide
- [ ] architecture diagram
