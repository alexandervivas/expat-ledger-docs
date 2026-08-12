---
name: develop-github-issue
description: Drive an Expat Ledger GitHub issue through delivery in the documentation repository with Claude Code. Use when asked to start, develop, continue, verify, finish, or report progress on a GitHub issue while keeping the published documentation site, the issue, and the shared GitHub Project synchronized.
---

# Develop GitHub Issue (documentation repository)

Treat GitHub Project `alexandervivas/1` as the planning and delivery source of truth. Treat the published MkDocs site and this repository's content as the documentation source of truth for product-level pages, and the application repositories as the source of truth for the code-adjacent trees they own (contracts, ADRs, OpenSpec specs). This repository aggregates contracts and ADRs at build time; OpenSpec specs are not published at all. Never recreate a second backlog in repository files.

This repository deliberately does not use OpenSpec. The documentation is the artifact itself; the delivery record is the issue, the branch, and the pull request. Significant structural decisions about the site (aggregation mechanism, navigation architecture, hosting) are recorded as short decision notes under `docs/decisions/` instead of ADR tooling.

Use `.claude/skills/develop-github-issue/scripts/project_issue.sh` for project inspection and status transitions. It resolves project and field IDs dynamically.

## Agent Orchestration

Keep the parent agent as delivery lead. The parent owns issue qualification, structural decisions about the site, final quality gates, GitHub synchronization, and the completion report.

Delegation is optional in this repository — most documentation batches are small enough to execute directly. When a batch is large (bulk page moves, sweeping link rewrites), spawn a general-purpose subagent with an explicit `model` matched to the batch: `haiku` for mechanical moves and link rewrites, `sonnet` for routine page work, `opus` only for cross-cutting restructuring. Give every subagent the issue URL, the exact scope, and the validation commands. Never run more than one workspace-writing agent at once.

## Isolate And Reclaim Parallel Workspaces

Working two issues in this repository at once requires separate git worktrees. Create a worktree only when another issue is already in flight in the primary checkout.

```bash
git fetch origin
git worktree add ../expat-ledger-docs-i<number> -b issue/<number>-<slug> origin/main
```

Always name the start point explicitly. Keep the worktree a sibling of the primary checkout, never nested inside it. Record the worktree path in the same issue comment that names the branch.

Reclaim the worktree before reporting completion. Both commands must return empty, without exception:

```bash
git -C <worktree> status --short
git -C <worktree> log --oneline origin/main..HEAD
```

Merge state alone never authorizes removal: if either command returns anything, stop and report it. When both are empty:

```bash
git worktree remove <worktree>
git worktree prune
git branch -d issue/<number>-<slug>
git worktree list
```

Never remove a worktree holding uncommitted or unpushed work, never use `git worktree remove --force` or `rm -rf` on a worktree, never leave a worktree behind after its issue merges, and never touch a worktree belonging to another in-progress issue.

## Publish In Small Stacked Pull Requests

Reviewability is a delivery gate: keep every pull request within roughly 200–300 changed lines (additions plus deletions, ignoring lockfiles, generated artifacts, and bulk page moves that a reviewer checks by path rather than by line). When an issue's scope exceeds that, deliver it as a stack of dependent pull requests with `gh stack` (the `github/gh-stack` extension) rather than one large PR.

- Plan the split before implementing: partition the work into increments that each keep `mkdocs build --strict` green on their own, ordered so an increment depends only on the ones below it. Never split mid-invariant — when a cohesive change cannot be divided without leaving an increment red, publish it as one oversized PR and say why in its body.
- Initialize the stack in the issue workspace with `gh stack init` from `origin/main`, keeping the first increment on the standard `issue/<number>-<slug>` branch. After committing each increment, start the next with `gh stack add issue/<number>-<slug>-<n>-<step>`.
- Publish with `gh stack submit`, which creates or updates the entire chain of PRs. Every PR links the issue, states its stack position (for example `Stack 2/3`), and summarizes only its own increment.
- An issue whose whole diff fits the budget is a stack of one: same commands, one PR.
- Merge bottom-up, each PR on the owner's word as always. After every merge, run `gh stack sync` to restack what remains. Keep the project item `In Progress` until the top of the stack merges; the issue closes with the top PR.
- Never bundle unrelated scope to fill a PR's budget.

## 1. Inspect And Qualify

1. Require an issue URL or issue number. Infer the current repository only for a number.
2. Read `AGENTS.md` and the issue body before changing files.
3. Run:

   ```bash
   .claude/skills/develop-github-issue/scripts/project_issue.sh inspect <issue>
   git status --short --branch
   ```

4. Require all of the following before starting:
   - The issue is open and belongs to this repository (or is a cross-repository documentation issue explicitly assigning work here).
   - The issue is present in the shared project.
   - `Refinement` is `Ready`.
   - Acceptance criteria and scope are actionable.
   - Required dependencies are satisfied or explicitly included in the change.
5. Stop without changing project status when the issue needs a product decision, belongs to another repository, or has an unresolved dependency.
6. Preserve unrelated working-tree changes. Reuse a matching branch rather than creating duplicates.

## 2. Start The Delivery Record

1. Derive a short kebab-case slug from the issue title.
2. Use `issue/<number>-<slug>` for a new branch.
3. Create the branch only when a dedicated branch does not already exist.
4. Set the project item to `In Progress` only after preflight succeeds:

   ```bash
   .claude/skills/develop-github-issue/scripts/project_issue.sh set-status <issue> "In Progress"
   ```

5. Add one concise issue comment naming the branch. Do not repeat the comment when resuming work.

## 3. Implement

1. Work in the smallest coherent increments: a nav change with its pages, a moved tree with its redirect stubs, a workflow with the check that proves it.
2. Respect the hybrid ownership model at every step: never copy contracts, ADRs, or OpenSpec specs into this repository as content. Contracts and ADRs are pulled from the application repositories at build time into the gitignored `docs/reference/`; OpenSpec specs are not published (`docs/decisions/0002-openspec-specs-not-published.md`). Product-level pages moved here must leave a pointer behind in the source repository, delivered through that repository's own workflow.
3. Review every page that enters this repository for sensitive content before it lands: the published site is public. No credentials, tenant identifiers, real financial data, or internal-only operational detail.
4. Keep the site buildable at every commit once MkDocs is configured.

## 4. Verify The Change

1. Run the repository quality gates mandated by `AGENTS.md`. Once MkDocs is configured, the mandatory gate is:

   ```bash
   mkdocs build --strict
   ```

   A broken `nav:` entry, missing file, or orphaned page fails the build; fix it rather than loosening the gate.
2. Check every issue acceptance criterion against the built site, not just the source tree.
3. Verify no moved page left a dead reference behind in either application repository; when a pointer or reference change is needed there, deliver it through that repository's `develop-github-issue` skill.
4. Check the diff for sensitive data before publication.

## 5. Synchronize GitHub Deliberately

- **Started or resumed:** set `In Progress`; record the branch once.
- **Blocked:** keep the truthful status and add a concise comment with the blocker and required decision. Use `Todo` only when work has genuinely returned to the queue.
- **Local implementation verified:** keep `In Progress`; comment with validation evidence and state that changes remain local.
- **PR opened:** keep `In Progress`; ensure the PR links the issue and summarizes content moved, structure changed, and gates run. For stacked delivery, every PR in the stack follows these rules and names its stack position.
- **Merged and accepted:** set `Done` and close the issue as completed.
- **Evidence-only issues** (deliverable posted on the issue itself, no branch or PR): close on completion-report acceptance — set `Done` and close as completed.

Never set `Done` merely because content exists locally or a PR is open. Never close an issue with unmet acceptance criteria.

## 6. Respect Git Write Boundaries

Invoking this skill for an issue authorizes the complete delivery publication flow: create or reuse the issue branch, commit the validated issue scope, push it, and open or update a ready-for-review PR. Do not pause for separate commit, push, or PR authorization once the completion gate is satisfied.

For work outside this skill, do not commit, push, or open a PR unless the user explicitly requests publication in the current session; leave local changes uncommitted by default.

Two things always require the owner's word in the current session:

- **Merging a pull request.**
- **Closing an issue**, and any history-rewriting or destructive action — force-push, `reset --hard` on a shared branch, remote branch or tag deletion — plus release and Pages-deployment configuration changes.

Use Conventional Commits. Work on the issue branch, never directly on `main`. Never commit credentials, tokens, or personal data regardless of authorization.

## Completion Report

Report:

- Issue, branch, and project status
- Delegated batches with the actual model used, when delegation occurred
- Worktrees created, and for each whether it was reclaimed or left in place with the reason, evidenced by `git worktree list`
- Content moved, structure changed, and pointers left in source repositories
- Acceptance criteria evidence against the built site
- Quality gates run with results (`mkdocs build --strict` output once configured)
- Sensitive-content review outcome for every page that entered the repository
- Remaining blockers, the PR URLs in stack order with each PR's diff size, and whether merge or issue closure still awaits the owner's word
