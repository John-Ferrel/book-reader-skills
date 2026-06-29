# Lens Selection

Start with the core method. Add lenses only when they improve reconstruction.

Use one primary lens by default. Use zero to two secondary lenses by default.
Additional lenses require an explicit reason and expected payoff.

| Signal | Lens |
| --- | --- |
| Definitions, notation, formulas, algorithms, proof/method dependencies | `lenses/technical-book` |
| Claims, warrants, counterclaims, persuasion path | `lenses/nonfiction-argument` |
| Characters, scenes, motifs, narrative rhythm, style | `lenses/fiction-narrative` |
| Independent essays, editorial sequence, recurring themes | `lenses/essay-anthology` |
| Lookup structure, taxonomy, cross references | `lenses/reference-book` |
| Missing text, poor extraction, inaccessible modalities | `lenses/source-limited` |
| Preface, afterword, retrospective, revised edition, translator/editor notes | `lenses/edition-revision` |
| Modern application, external comparison, historical bridge | `lenses/external-context` |

Lens-specific behavior is not a core invariant. If a lens artifact does not
improve reconstruction, omit it or mark it deferred/blocked/not-applicable with
a reason.

Record lens use in the workspace/dashboard:

- `primary_lens`
- `secondary_lenses`
- `lens_rationale`

Reviewer checks lens creep: too many lenses opened without payoff, or
lens-specific artifacts created but not used.
