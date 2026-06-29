# Skill Architecture

Book Reader v2 is a method-first skill pack. Runtime scripts prepare evidence;
skills guide reading, reconstruction, review, and revision.

## Skill pack overview

| Skill | Responsibility |
| --- | --- |
| `book-reader` | Orchestrator and router. Chooses intake, reconstruction, review, revision, and lenses. |
| `book-intake` | Mechanical source processing: ingest, normalize, source metadata, source map, validation, info. |
| `book-reconstruct` | Core evidence-driven reading method and reconstruction workflow. |
| `book-reviewer` | Inference discipline audit; writes review outputs only. |
| `book-revise` | Applies review-driven revisions and records revision logs. |
| `lenses/*` | Optional adaptations for book type or reading situation. |

## Handoff

Default read:

```text
book-reader -> book-intake -> book-reconstruct -> optional lens -> self-check -> book-reviewer
```

Review:

```text
book-reader -> book-reviewer
```

Revision:

```text
book-reader -> book-revise -> book-reviewer verification
```

Full read loop:

```text
reader reconstructs -> independent reviewer audits -> reviser re-reads/revises -> independent reviewer verifies
```

Repeat until stable or `max_review_rounds` is reached. Creator self-check is
not independent review.

Lenses can be selected by user request (`technical-book lens`) or by clear
source signals. They add attention patterns and optional artifacts; they do not
replace evidence discipline.

## Agent usage

Codex, OpenCode, or a generic agent should treat `skills/book-reader/SKILL.md`
as the entry point. The user prompt can stay short:

```text
用 book-reader 读 examples/input/book.epub
用 technical-book lens 读这本概率论教材
用 book-reviewer 审查 workspaces/book-x
根据 review/revision-plan.md 用 book-revise 修订
```

## Progressive disclosure

`SKILL.md` files should be short. They route work and name the references to
read. Long theory goes into `references/`. Reusable output forms go into
`templates/`. Mechanical code goes into `scripts/`.

This keeps zero-shot use simple while preserving detailed guidance for agents
that need it.

## Boundaries

- Scripts extract and validate; they do not infer author intent.
- References describe method and judgment discipline.
- Templates shape human-readable artifacts; they are not semantic conclusions.
- Reviewer writes only `review/` outputs unless repair mode is explicitly
  requested.
- Reviser applies changes and records what changed.

Do not reintroduce v1 compatibility surfaces such as `chapters/`,
`reading-passes/`, or `projections/`.
