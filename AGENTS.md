# AGENTS.md

Repository-wide instructions for coding agents working on the Expat Ledger central documentation repository.

## 1. Purpose And Ownership Model

- This repository owns the published Expat Ledger documentation site (MkDocs Material on GitHub Pages) and the **product-level** documentation content: glossary, architecture overviews, requirement narratives, ops/runbooks, governance pages.
- It aggregates but does **not** own the code-adjacent trees: `docs/contracts/` (backend-authoritative) and ADRs stay in their application repositories and are pulled into the site at build time by `scripts/aggregate.py`. Never copy them here as content; fix them at their source through that repository's workflow.
- OpenSpec capability specs (`openspec/specs/`) stay in their application repositories and are **not published** on the site — see `docs/decisions/0002-openspec-specs-not-published.md`.
- The split criterion, decided 2026-08-11 (backend#144): a document that changes in lockstep with a commit lives with the code; everything else lives here.

## 2. Planning And Workflow

- The private [Expat Ledger Product project](https://github.com/users/alexandervivas/projects/1) is the planning and delivery source of truth.
- Use the repository `develop-github-issue` skill when starting, continuing, verifying, or finishing a GitHub issue. It is the sole entry point for repository work.
- This repository does not use OpenSpec; `docs/decisions/0003-no-openspec-in-this-repository.md` records why and names the trigger that would reopen the question. Structural decisions about the site are recorded as short decision notes under `docs/decisions/`.

## 3. Public Site — Sensitivity Rules

- The published site is public. Never commit or publish credentials, tokens, tenant identifiers, account identifiers, real financial data, raw bank statements, or internal-only operational detail.
- Review every page that enters this repository for sensitivity before it lands, including pages moved from the application repositories.

## 4. Quality Gates

- Once MkDocs is configured, `mkdocs build --strict` must pass locally and in CI before publication; a broken nav entry, missing file, or orphaned page fails the build.
- Keep the site buildable at every commit.

## 5. Git Write Rule

- Invoking `develop-github-issue` for an issue authorizes the complete delivery publication flow: branch, commit, push, and a ready-for-review PR.
- For work outside the skill, do not commit, push, or open a PR unless the user explicitly requests publication in the current session.
- Never merge a PR or close an issue without an explicit request in the current session. Never force-push or bypass quality gates.
- Use Conventional Commits. Work on issue branches, never directly on `main`.
