# 0001 — Code-adjacent trees are vendored at build time by a script

**Date:** 2026-08-12 · **Status:** Accepted · **Issue:** [#1](https://github.com/alexandervivas/expat-ledger-docs/issues/1)

## Context

The hybrid ownership model splits documentation by one question: does this
document change in lockstep with a commit? Contracts and ADRs do, so they stay
authoritative in `expat-ledger-backend` and `expat-ledger-frontend`. The site
still has to render them, without this repository ever owning a copy.

## Decision

`scripts/aggregate.py` performs a shallow, blobless, sparse `git clone` of both
application repositories — both are public, so no token is involved — and
copies only the needed subtrees into `docs/reference/`. That directory is
listed in `.gitignore`, so aggregated material cannot enter this repository's
history even by accident. The script runs identically in CI and locally:

```bash
python scripts/aggregate.py && mkdocs build --strict
```

The script also generates `docs/reference/SUMMARY.md`, the
[mkdocs-literate-nav](https://oprypin.github.io/mkdocs-literate-nav/) file that
supplies navigation for the aggregated pages, and wraps non-markdown contract
artifacts (`.proto`, `.avsc`, `.yaml`) in generated pages so they render rather
than merely download.

## Alternatives rejected

**A multi-repo MkDocs plugin.** Fetching happens inside the build, so a CI
failure cannot be reproduced locally by running one command, and the plugin's
fetch behaviour is not ours to adjust when an upstream layout changes.

**Git submodules.** A submodule pins a specific commit, so every upstream
documentation change needs a corresponding update commit here. That defeats the
requirement that a docs change upstream reaches the site without manual action.

**Copying the content in.** Forbidden by the ownership model: it creates a
second source of truth for documents whose authority belongs with the code.

## Consequences

- Generating the nav is what keeps `--strict` honest. A new upstream ADR enters
  the navigation automatically instead of becoming an orphan page that fails
  the build.
- A local build now needs network access, because `docs/reference/` is not
  checked in. `mkdocs serve` against a stale aggregate still works; re-run the
  script to refresh.
- Links that escape a vendored tree are rewritten by explicitly named rules in
  the script, never by a general regex, so an upstream move fails the strict
  build loudly instead of being silently patched.
