# 0003 — This repository does not adopt OpenSpec for its own workflow

**Date:** 2026-08-12 · **Status:** Accepted · **Issue:** [#1](https://github.com/alexandervivas/expat-ledger-docs/issues/1)

## Context

Both application repositories run OpenSpec: propose a change, write spec
deltas, apply, archive into capability specs. `AGENTS.md` states that this
repository does not. That statement predated any examination, so it was
reopened while delivering issue #1 and is now recorded as a decision rather
than an assumption.

## Decision

This repository does not adopt OpenSpec. Its delivery record is the issue, the
branch, and the pull request; its structural decisions are the notes in this
directory.

The reason is that this repository already has the executable acceptance test
that spec-driven development exists to supply. In backend, "does the code do
what we said it would?" needs a specification to answer. Here,
`mkdocs build --strict` *is* that check: a broken nav entry, a missing file, a
dangling link, or an orphaned page fails the build. A spec layer would largely
restate conditions the build already enforces mechanically, and the deliverable
itself is prose — a specification describing prose is a second copy of the
prose's intent.

## Revisit trigger

Reopen this decision when the site's build machinery acquires behaviour that
`mkdocs build --strict` cannot verify. Concretely:

- a third source repository joins the aggregation, making precedence and
  collision rules something a person must reason about; or
- aggregation becomes conditional or partial — content included on some builds
  and not others — so that a green build no longer implies a correct site.

Until one of those holds, the strict build carries the weight a spec otherwise
would.

## Consequences

- No `openspec/` tree, no propose/apply/archive cycle, no `/opsx` commands here.
- `AGENTS.md` keeps its statement, now backed by this note.
- Structural decisions continue to land in this directory as short notes.
