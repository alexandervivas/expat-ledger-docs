# 0004 — ProperDocs is rejected; MkDocs stays the build driver

**Date:** 2026-08-12 · **Status:** Accepted · **Issue:** [#4](https://github.com/alexandervivas/expat-ledger-docs/issues/4)

## Context

Every build of this site printed an advisory recommending that we abandon
MkDocs for **ProperDocs**, a fork presenting itself as a drop-in continuation
of MkDocs 1.x. The advisory did not come from MkDocs or from
`mkdocs-material`; it was emitted by `mkdocs-literate-nav`, a nav plugin this
site depends on.

The question was first framed as a migration choice — switch drivers or don't.
Investigation reframed it, because the mechanism by which the recommendation
arrived turned out to matter more than the recommendation itself.

`mkdocs-literate-nav` 0.6.2 (2025-03-18) declares exactly one dependency:

```
mkdocs>=1.4.1
```

0.6.3 (2026-03-16) declares:

```
mkdocs<=1.6.1,>=1.4.1
properdocs>=1.6.5
```

A patch release of a navigation plugin therefore did two things unrelated to
navigation: it installed a fork of MkDocs into every environment that resolved
it, and it capped real MkDocs at the then-current release, so MkDocs itself
could never be upgraded while the plugin stayed current. The pin bump delivered
in [#1](https://github.com/alexandervivas/expat-ledger-docs/issues/1) is how
`properdocs` came to be installed here — nothing in this repository ever asked
for it, and `requirements.txt` did not pin it, so it floated.

Supporting observations, verified against PyPI rather than taken from the
advisory:

- `properdocs` has three releases: 1.6.5 and 1.6.6 on 2026-03-16, and 1.6.7 on
  2026-03-20. `mkdocs-literate-nav` 0.6.3 was published nine minutes after
  `properdocs` 1.6.6.
- `properdocs` carries MkDocs's own summary verbatim ("Project documentation
  with Markdown") and its `author_email` field still names Tom Christie,
  MkDocs's original author, who is not behind the fork. The metadata is
  inherited from the forked source tree rather than authored.
- `mkdocs-material` cannot be made to drop MkDocs — it declares `mkdocs` as a
  dependency — and `properdocs` ships a parallel `properdocs` import namespace
  instead of replacing `mkdocs`. Adopting the fork was therefore never a
  removal of anything; it was a swap of which CLI drives the build, with both
  packages installed either way.
- `mkdocs-material` suppresses its own MkDocs 2.0 advisory when it detects that
  a fork is driving the build (`material/templates/__init__.py`, `is_mkdocs()`).
  Running `properdocs build` would have produced a visibly quieter build while
  actually removing our sight of Material's position.

The advisory's concrete stated danger — that a future `pip install mkdocs`
silently resolves to a breaking 2.0 — does not apply to this repository. We pin
`mkdocs==1.6.1` and CI installs from `requirements.txt`, so that path is
already closed.

## Decision

**MkDocs remains the build driver.** ProperDocs is rejected, and
`mkdocs-literate-nav` is held at **0.6.2** in `requirements.txt` so that no
resolution path pulls the fork in.

The reason is not a judgement that ProperDocs is bad software. It is that we
decline to accept a dependency we did not choose, delivered through a patch
release of an unrelated plugin, which simultaneously constrains an upgrade path
we do want to keep. Whether that pattern is opportunism, fork politics, or
something worse does not change the correct response to it: pin, and choose
deliberately.

Two further facts made rejection cheap. 0.6.2 renders this site *byte-identical*
to 0.6.3 across all 174 built files, so the pin costs no functionality. And
because we pin MkDocs, staying put carries no exposure to MkDocs 2.0.

`NO_MKDOCS_2_WARNING=true` is set on the CI build step to silence the remaining
advisory, which comes from `mkdocs-material` and predates this issue. That
warning is advocacy about an unreleased version, not a build diagnostic, and it
is unactionable for a repository that pins its toolchain. Silencing it keeps
real `--strict` warnings legible. This note is the record that it is suppressed
on purpose.

Two similarly named variables are easy to confuse, so for the record: the
ProperDocs advisory offered `DISABLE_MKDOCS_2_WARNING`, and issue #4 quotes that
name. It belonged to `mkdocs-literate-nav` 0.6.3 and is now dead — no package in
this dependency set reads it, because the plugin that did has been pinned away.
`NO_MKDOCS_2_WARNING` is a different variable belonging to `mkdocs-material`,
and it is the only one worth setting here. Setting both would imply a dependency
this decision deliberately removed.

## Revisit trigger

Reopen this decision when any of the following holds:

- `mkdocs-literate-nav` publishes a release that drops the `properdocs`
  dependency and the `mkdocs<=1.6.1` cap. Then the pin can move forward
  normally and this note only explains the gap in versions.
- MkDocs itself is genuinely abandoned *and* a successor emerges with
  maintainership we can identify and assess on its own terms — rather than one
  that arrives through another package's dependency list.
- `mkdocs-material` adopts the fork, or drops its `mkdocs` dependency. Material
  is the constraint that makes the current arrangement stable; if it moves, the
  ground for this decision moves with it.
- The 0.6.2 pin starts costing something real — a needed `literate-nav` fix
  landing only in 0.6.3 or later.

Until then the pin holds and the advisory is not re-litigated per build.

## Consequences

- `requirements.txt` pins `mkdocs-literate-nav==0.6.2` with an inline comment
  explaining why the version is held below latest, so a routine dependency
  bump cannot quietly undo this.
- `properdocs` is absent from a clean install: rebuilding the virtualenv from
  `requirements.txt` resolves 30 packages, none of them the fork.
- `mkdocs build --strict` stays the mandatory gate, unchanged in `AGENTS.md`,
  `README.md`, `docs/index.md`, and the `develop-github-issue` skill. No
  document needed updating, because the driver did not change.
- Builds are quiet again: no ProperDocs advisory, and Material's advisory
  deliberately suppressed with the reason recorded here.
- A dependency-review habit is implied for this repository: a transitive
  package appearing in the lock surface is a change to review, not noise.
