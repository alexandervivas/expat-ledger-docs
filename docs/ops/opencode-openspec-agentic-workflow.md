# OpenCode OpenSpec Agentic Workflow (Scala)

This repository uses an OpenCode-native OpenSpec workflow with phase
orchestrators and Scala-specialized workers.

Requirement traceability for this ops setup:

- `NFR-003` Reliability
- `NFR-004` Portability

## Architecture and Phase Flow

Default flow:

1. `opsx-explore` -> `opsx-explore-orchestrator`
2. `opsx-propose` -> `opsx-propose-orchestrator`
3. `opsx-apply` -> `opsx-apply-orchestrator`
4. `opsx-archive` -> `opsx-archive-orchestrator`

Automatic phase transitions are enabled by default. Human escalation is used
only when policy triggers fire.

## Orchestrators and Workers

Orchestrators (`mode: primary`):

- `opsx-explore-orchestrator`
- `opsx-propose-orchestrator`
- `opsx-apply-orchestrator`
- `opsx-archive-orchestrator`

Workers (`mode: subagent`, `hidden: true`):

- `opsx-implementer`
- `opsx-test-fixer`
- `opsx-code-reviewer`
- `opsx-docs-refactor` (support role)

`opsx-apply-orchestrator` enforces task permission guardrails:

- `permission.task.default: deny`
- explicit allowlist:
  - `opsx-implementer`
  - `opsx-test-fixer`
  - `opsx-code-reviewer`
  - `opsx-docs-refactor`

## Scala-Specific Enrichment Decisions

Agent prompts are enriched using `AGENTS.md`,
`README.md`, `build.sbt`, ADRs, and module boundaries:

- Scala 3 idioms and immutable modeling.
- Cats Effect resource/effect safety.
- Smart constructors / `ValidatedNec` for validation patterns.
- `Try` preference for recoverable exceptions in app code.
- Module ownership alignment with current service layout.
- Security/domain invariants:
  tenant isolation, idempotency, UTC timestamps, UUID usage.

## Routing and Budget Knobs

Defined in `workflow/policy.js`:

- Routing tiers: `low`, `balanced`, `premium`.
- Default tier by phase.
- Retry budget by phase.
- Time budget by phase.
- Premium guardrails:
  - session premium budget cap,
  - minimum remaining budget floor,
  - downgrade tier when premium is blocked.

Routing and enforcement logic is implemented in `workflow/engine.js`.

## Escalation Contract

Escalation is allowed only for:

- retry budget exhausted,
- phase time budget exhausted,
- unresolved review conflicts,
- critical decision categories:
  `security`, `data_integrity`, `compliance`,
  `irreversible_architecture`.

`workflow/engine.js` provides:

- escalation classification,
- escalation packet generation,
- dry-run simulation scenarios.

## Local Validation Runbook

Run workflow tests:

```bash
node --test workflow/tests/*.test.js
```

Run repository quality gates:

```bash
sbt test
pre-commit run --all-files
```

Run docs/contracts currency check for this workflow change:

```bash
git diff --name-only -- docs/contracts
```

Expected for this setup change: no contract surface diffs.
