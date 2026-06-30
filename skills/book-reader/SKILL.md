---
name: book-reader
description: Use when the user wants to read a book with the Book Reader workflow and needs routing across intake, reconstruction, review, revision, or lenses.
---

# Book Reader

Book Reader is the orchestrator for an evidence-driven reading methodology.
Default output is not a summary. Default output is an evidence-linked
reconstruction workspace.

Use this routing:

- Normal read: use `book-intake`, then `book-reconstruct`.
- Full read: after reconstruction, require independent `book-reviewer`; revise
  with `book-revise`; verify again until stable or max rounds reached.
- Existing workspace review: use `book-reviewer`.
- Revision from review: use `book-revise`.
- Technical/math/engineering/software book: add `lenses/technical-book`.
- Fiction: add `lenses/fiction-narrative`.
- Argument analysis: add `lenses/nonfiction-argument`.
- Source-limited input: add `lenses/source-limited`.
- Edition/revision signals: add `lenses/edition-revision`.
- External comparison/application: add `lenses/external-context`.

Before reading, consult:

- `references/method-overview.md`
- `references/lens-selection.md`
- `references/run-protocol.md`

Do not report a workspace complete after creator self-check. If no independent
review has run, report that the next required action is a fresh reviewer
session.
