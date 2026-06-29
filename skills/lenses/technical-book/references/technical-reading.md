# Technical Reading Lens

Apply the core Book Reader method. Add technical attention:

- Track definitions and notation as first-class evidence.
- Separate examples from required proof or method dependencies.
- Record formulas/theorems with source block anchors.
- Identify prerequisite chains before reconstructing reader path.
- Put executable or mathematical verification questions in a source-check queue.

Do not validate technical truth beyond available source evidence unless the user
explicitly asks for external checking.

## Completion levels

- `technical-map-ready`
- `formal-objects-indexed`
- `selected-units-deep-read`
- `proof-details-deferred`
- `exercise-layer-not-read`

First reconstruction does not require deep reading every proof. It must not
pretend derivations, exercises, figures, or tables were understood when they
were only skimmed, missing, or extraction-limited.

## Anti-laziness minimum

Handle or explicitly defer:

- notation system
- formal objects
- definitions
- theorems / formulas / algorithms
- dependency graph / prerequisite map
- examples and what they teach
- proof / derivation status
- figures / tables / exercises limitations
- deep-reading queue

Reviewer should fail technical-book output that is only ordinary chapter
summary without notation/formal-object/dependency treatment or explicit
deferral.
