# expat-ledger-docs

The published Expat Ledger documentation site — MkDocs Material on GitHub Pages.

**Site:** <https://alexandervivas.github.io/expat-ledger-docs/>

## The hybrid split

Documentation for Expat Ledger lives in three repositories. What goes where is
decided by one question: **does this document change in lockstep with a
commit?**

| | Owner | On the site |
| --- | --- | --- |
| Glossary, architecture overviews and narratives, requirements, ops runbooks, governance | **this repository** | Yes, sources live here |
| `docs/contracts/` (backend), ADRs (`docs/architecture/decisions/`, both app repos) | the application repository | Yes, pulled in at build time |
| OpenSpec capability specs (`openspec/specs/`, both app repos) | the application repository | No — [decision 0002](docs/decisions/0002-openspec-specs-not-published.md) |

A document that changes with the code stays with the code, because moving it
would break the same-PR documentation gates in the application repositories.
Everything product-level moves here outright, and the application repositories
keep only a pointer.

Contracts and ADRs are **never copied into this repository**. They are vendored
into `docs/reference/` at build time, and that directory is gitignored, so
aggregated material cannot enter this repository's history even by accident.

## Building locally

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt

.venv/bin/python scripts/aggregate.py   # pull contracts + ADRs (needs network)
.venv/bin/mkdocs build --strict         # the mandatory quality gate
.venv/bin/mkdocs serve                  # preview at http://127.0.0.1:8000
```

Python is pinned in `.tool-versions` (asdf). The aggregation step needs network
access because `docs/reference/` is not checked in; `mkdocs serve` will happily
run against a previously-pulled aggregate.

`mkdocs build --strict` is the gate, in CI and locally. A broken nav entry, a
missing file, a dangling link, or an orphaned page fails the build. Fix the
cause rather than loosening the gate.

## How aggregation works

`scripts/aggregate.py` does a shallow, blobless, sparse `git clone` of both
application repositories and copies only the needed subtrees into
`docs/reference/`. Both repositories are private, so CI authenticates the
clone with a fine-grained PAT (`DOCS_SOURCE_REPOS_TOKEN`, Contents:
Read-only, scoped to just those two repositories); local development relies
instead on the developer's own git credentials already having read access.
It then:

- generates `docs/reference/SUMMARY.md`, the
  [mkdocs-literate-nav](https://oprypin.github.io/mkdocs-literate-nav/) file
  that navigates the aggregated pages, so a new upstream ADR appears in the nav
  automatically instead of becoming an orphan that fails the build;
- wraps non-markdown contract artifacts (`.proto`, `.avsc`, `.yaml`) in
  generated pages so they render on the site, leaving the raw file in place so
  it stays downloadable.

Adding a source repository or a subtree means editing the `SOURCES` list at the
top of that script. Rationale and rejected alternatives are in
[decision 0001](docs/decisions/0001-aggregation-mechanism.md).

## Staying fresh

The site rebuilds on push to `main`, on a daily schedule, on manual dispatch,
and on a `repository_dispatch` of type `docs-updated`.

> **Known gap.** The `repository_dispatch` **sender** in `expat-ledger-backend`
> and `expat-ledger-frontend` does not exist yet, so a docs change in an
> application repository currently reaches the site via the daily schedule
> rather than immediately. Tracked as deferred work on
> [issue #1](https://github.com/alexandervivas/expat-ledger-docs/issues/1); it
> must be delivered through each application repository's own workflow.

A scheduled run is unattended, so a red one gets no PR check for a human to
see — only a workflow-failure email, which has already gone unnoticed for
eight consecutive runs. The `notify-on-schedule-failure` job in
`.github/workflows/docs.yml` turns a red scheduled (or manually dispatched)
run into a single reused GitHub issue titled "Scheduled Docs build is red on
main": the first failure files it and adds it to the Project board, repeat
failures each get a comment instead of a new issue, and the next green run
closes it automatically. PR-triggered runs already surface red checks on the
PR and are excluded.

## Working in this repository

- Read `AGENTS.md` first. It is the repository-wide instruction set.
- Use the `develop-github-issue` skill as the entry point for issue work.
- This repository does not use OpenSpec —
  [decision 0003](docs/decisions/0003-no-openspec-in-this-repository.md)
  records why, and names the trigger that would reopen it.
- Structural decisions about the site are short notes in `docs/decisions/`.

## This site is public

Never commit or publish credentials, tokens, tenant identifiers, account
identifiers, real financial data, raw bank statements, or internal-only
operational detail. Review every page for sensitivity before it lands,
including pages moved in from the application repositories.

That the site is public is also what makes it useful as an **evidence
archive**: the application repositories are private, so their screenshots
cannot render in an issue, while anything under `docs/evidence/` gets a stable
public URL that renders in all three. Adding a run means following
[the archive convention](docs/governance/evidence-archive.md) — dated folders,
synthetic identities, destructive redaction, and runs that are never edited
after the fact.
