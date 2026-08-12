# CI Quality Gates

What `.github/workflows/ci.yml` actually enforces, how to reproduce each gate locally, and how
the two suppression paths are governed.

Authoritative decisions: [ADR-026](/reference/backend/decisions/ADR-026-ci-security-gates.md).
Introduced by [#78](https://github.com/alexandervivas/expat-ledger-backend/issues/78).

This document is deliberately precise about the _limits_ of each gate. It replaces a pipeline
whose security step was named `Security Audit (Fake step for T2.11)` and whose coverage step
was an `echo`, so a gate description that overstates what it enforces would repeat the
original failure.

## Jobs at a glance

| Job               | Triggers                                             | Fails when                                                                                                                        |
| ----------------- | ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `build`           | PR to `main`, push to `main`                         | Compilation fails, a test fails, or a gated module is below the 90% statement minimum                                             |
| `dependency-scan` | PR to `main`, push to `main`, weekly (Mon 04:17 UTC) | An unsuppressed `HIGH`/`CRITICAL` dependency vulnerability, a collapsed dependency inventory, or an unavailable advisory database |
| `secret-scan`     | PR to `main`, push to `main`                         | Any secret is detected anywhere in git history                                                                                    |

`build` and `secret-scan` are skipped on scheduled runs: nothing changes between them, and git
history only moves on a push, which triggers the scan directly. The weekly run exists so a CVE
published against a dependency that did not change is still surfaced.

### Failing a check is not the same as blocking a merge

A job that fails turns its check red. Whether that red check actually _prevents_ merging is decided
separately, by the `main` ruleset's **required status checks**. A gate that reports without blocking
is only half a gate, so the two are kept aligned deliberately.

**Required status checks on `main`** (ruleset `main`, active, no bypass actors):

| Context           | Required | Notes                                                           |
| ----------------- | -------- | --------------------------------------------------------------- |
| `build`           | yes      | Tests and the per-module coverage minimum                       |
| `dependency-scan` | yes      | HIGH/CRITICAL vulnerabilities and the non-vacuity guard         |
| `secret-scan`     | yes      | Secrets anywhere in git history                                 |
| `qodana`          | no       | Still runs and still comments, but advisory — it does not block |

`strict_required_status_checks_policy` is enabled, so a branch must also be up to date with `main`
before it can merge. Merges are squash-only, and `required_approving_review_count` is 0.

Two operational notes about how these contexts behave:

- A check-run context is the job's `name:` when one is set, otherwise the job id. Jobs in `ci.yml`
  therefore deliberately carry **no** `name:`, so contexts stay equal to the stable ids `build`,
  `dependency-scan`, and `secret-scan`. Naming a job renames its check, the required context stops
  being reported, and every merge blocks with all checks apparently green — this happened once
  during #78 and cost a debugging cycle. Rename a job only together with the ruleset.
- `build` and `secret-scan` are skipped on scheduled runs. A skipped check reports neutral rather
  than failing, which does not block a merge — but scheduled runs do not merge anything, so this
  only matters if the triggers change.

## Gate 1 — Tests and coverage

```bash
sbt coverage test coverageReport coverageAggregate
```

**Where enforcement lives.** `build.sbt`, via `coverageMinimumStmtTotal := 90` and
`coverageFailOnMinimum := true`. The workflow deliberately does **not** restate the number, so
there is exactly one source of truth for it. A CI step that re-checks the threshold would be a
second place to keep in sync — and the previous `Check coverage threshold` step, which only
echoed `"Coverage check completed."`, is what that intention decayed into.

**Enforcement is per module, at `coverageReport`.** This is stronger than an aggregate check: if
every gated module clears 90%, the weighted aggregate necessarily does, whereas an
aggregate-only gate would let a weak module hide behind a strong one.

**The gate binds 6 of 9 modules.** These three opt out with `coverageEnabled := false`,
`coverageFailOnMinimum := false`, `coverageMinimumStmtTotal := 0`:

| Module               | Why it is excluded                                                                 |
| -------------------- | ---------------------------------------------------------------------------------- |
| `maintenance-worker` | Privileged operational CLI for Vault rotation/maintenance                          |
| `shared-test-kernel` | Test-support code; it exists to be used _by_ tests                                 |
| `integration-tests`  | Testcontainers harness whose value is the specs it runs, not its own line coverage |

Gated: `shared-kernel`, `api-gateway`, `tenant-service`, `fx-service`, `account-service`,
`transaction-service`.

The exclusions are defensible, but "90% coverage enforced" without this qualifier would be an
overclaim, so it is stated here.

**Current state** (measured 2026-08-05): aggregate statement coverage **94.16%**.

**Reproducing a failure** — confirm for yourself that the gate can fail, without editing
`build.sbt`:

```bash
sbt 'set ThisBuild / coverageMinimumStmtTotal := 99.9' coverage test coverageReport coverageAggregate
# => [error] (sharedKernel / coverageReport) Coverage minimum was not reached
# => exit 1
```

**Documented conflict — partially resolved.** Four different coverage targets used to appear in
repository documentation. Two of them lived in `.junie/guidelines.md` (100% for domain logic
_and_ a ≥70% goal), which was deleted on 2026-08-06 as outdated; `AGENTS.md` §1.9 now states
explicitly that `build.sbt` is authoritative. What remains is `README.md`, which still describes
100% for domain logic as an aspiration while noting the enforced figure. The **enforced** number
is and has always been the 90% statement minimum in `build.sbt`. Fully reconciling the remaining
documented aspiration is still a governance decision, tracked by
[#93](https://github.com/alexandervivas/expat-ledger-backend/issues/93).

## Gate 2 — Dependency vulnerabilities

Fails the build on any `HIGH` or `CRITICAL` finding not covered by an unexpired allowlist entry.

**Local prerequisites:** `docker` and `python3`. The guard script parses the SBOM JSON with
`python3` — present on the CI runner, but macOS has not bundled it since 12.3, so install it via
`xcode-select --install` or `brew install python` if `python3` is missing. The script checks for
it up front and says so plainly rather than failing obscurely.

```bash
# 1. Generate the dependency inventory from sbt's own resolution
sbt makeBom

# 2. Refuse to trust a scan whose inventory has collapsed
bash scripts/check_sbom_inventory.sh

# 3. Scan every module's SBOM
for bom in modules/*/target/*.bom.json; do
  docker run --rm -v "$PWD:/work" -w /work aquasec/trivy:0.73.0 \
    sbom --scanners vuln --severity HIGH,CRITICAL --exit-code 1 \
    --ignorefile .trivyignore.yaml "$bom"
done
```

**Why an SBOM rather than a filesystem scan.** This repository has no `pom.xml` and no lockfile
of any kind — dependency truth lives in `project/Dependencies.scala` and sbt's resolver, which
no off-the-shelf scanner parses. `trivy fs .` therefore finds **zero dependencies and exits 0**.
It would look exactly like a passing security gate while scanning nothing at all. The inventory
is instead generated by `sbt makeBom` (the `sbt-sbom` plugin) as one CycloneDX SBOM per module,
carrying exact coordinates from sbt's own resolution.

**The non-vacuity guard.** `scripts/check_sbom_inventory.sh` fails unless at least 9 SBOMs exist
containing at least 500 components in total, and fails on a malformed SBOM rather than counting
it as zero. Current baseline: **9 SBOMs, 1592 components**.

If this guard fails, **fix the inventory — do not lower the floors.** The floors sit far below
the baseline precisely so that ordinary dependency pruning never trips them. A guard failure
means a module stopped emitting an SBOM, an output path changed, or generation failed silently
— in every one of those cases the scan that follows would be vacuous and its green result
meaningless.

**Advisory database.** Downloaded in its own step with bounded retries, then used with
`--skip-db-update`. If the database cannot be fetched, the job **fails**. A scan that could not
obtain advisory data must never report a pass.

`--ignore-unfixed` is deliberately not used: an unfixed `HIGH` is something to hold consciously
in an allowlist entry, not something the scanner should silently drop.

## Gate 3 — Secrets

Fails on any detected secret anywhere in git history.

```bash
docker run --rm -v "$PWD:/repo" \
  -e GIT_CONFIG_COUNT=1 -e GIT_CONFIG_KEY_0=safe.directory -e GIT_CONFIG_VALUE_0=/repo \
  zricethezav/gitleaks:v8.30.1 \
  git /repo --config /repo/.gitleaks.toml --redact --no-banner --exit-code 1
```

Run from a full (non-shallow) clone. Inside a `git worktree`, `.git` is a file pointing into the
parent repository, so scan a full clone instead of the worktree if you need identical results
to CI.

**Full history, not the diff.** CI checks out with `fetch-depth: 0`. A secret committed and
later deleted is still leaked, and a shallow checkout would not see it. Verified: a token
committed and then deleted is still caught, with the tip of the tree clean.

**`--redact` is mandatory.** A detection reports the rule, file, and commit but never the secret
value, so triaging a finding never spreads it into CI logs.

**Current state** (measured in CI, 2026-08-05): **81 commits, 3.95 MB, no leaks found**.

81 is the full history reachable from `main`. A local clone that also carries unmerged feature
branches will report a much larger count (~292) because `git clone` brings every branch with it;
that figure includes commits that are not mainline history. When comparing a local run against
CI, compare `git rev-list --count origin/main`, not `git rev-list --all --count`.

**If the gate fires,** rotate the credential first. Removing the commit does not unleak a secret
that has been pushed — treat it as compromised, rotate, and only then clean history.

## Suppressing a finding

Suppression is **only ever a committed entry** in `.trivyignore.yaml` or `.gitleaks.toml`. It is
never a command-line flag, an environment variable, `--ignore-unfixed`, or a workflow-level
severity adjustment. If it does not appear in a diff, it is not an allowed suppression — the
point is that a reviewer sees it.

Every entry must record the finding identifier, a justification, an owner, and an expiry date,
and must never contain a secret value, bank identifier, account identifier, or any personal
financial datum.

### The two paths are not equally strong

|                    | `.trivyignore.yaml`             | `.gitleaks.toml`                                         |
| ------------------ | ------------------------------- | -------------------------------------------------------- |
| Scope              | One named advisory id per entry | Named path/rule allowlist entry                          |
| Expiry field       | `expired_at`                    | Documented in the required comment block                 |
| Expiry enforcement | **Enforced by trivy itself**    | **Review-enforced only** — gitleaks has no native expiry |

Verified for trivy: a future `expired_at` suppresses and exits 0; a past one reports the finding
and exits 1. So dependency suppressions lapse on their own, and CI going red on the expiry date
is intended behavior, not a breakage to work around.

For gitleaks, nothing mechanical enforces the date. An entry past its expiry must be removed or
re-justified by a reviewer. This asymmetry is stated rather than glossed over, because a reader
who assumed parity would over-trust the gitleaks allowlist.

### Currently seeded dependency suppressions

These 7 `HIGH` findings pre-date the gate. Remediation was out of scope for #78 and is tracked
by [#99](https://github.com/alexandervivas/expat-ledger-backend/issues/99). All expire
**2026-11-05**, after which CI fails until each is fixed or re-justified.

| Advisory              | Package                                       | Installed      | Fixed in |
| --------------------- | --------------------------------------------- | -------------- | -------- |
| `GHSA-r7wm-3cxj-wff9` | `com.fasterxml.jackson.core:jackson-core`     | 2.19.1, 2.20.0 | 2.21.4   |
| `CVE-2026-54512`      | `com.fasterxml.jackson.core:jackson-databind` | 2.19.1, 2.20.0 | 2.21.4   |
| `CVE-2026-54513`      | `com.fasterxml.jackson.core:jackson-databind` | 2.19.1, 2.20.0 | 2.21.4   |
| `CVE-2025-55163`      | `io.grpc:grpc-netty-shaded`                   | 1.58.0         | 1.75.0   |
| `CVE-2026-42198`      | `org.postgresql:postgresql`                   | 42.7.8         | 42.7.11  |
| `CVE-2026-54291`      | `org.postgresql:postgresql`                   | 42.7.8         | 42.7.12  |
| `CVE-2024-21634`      | `software.amazon.ion:ion-java`                | 1.0.2          | 1.10.5   |

No secret-scan suppressions are currently seeded; `.gitleaks.toml` has an empty allowlist because
the baseline scan found nothing.

## What these gates do not cover

- **SAST, DAST, penetration testing, container-image scanning, runtime hardening.** None are in
  this pipeline. Do not read a green CI as evidence of any of them.
- **Severities below `HIGH`.** Not reported, to keep the signal actionable.
- **Test-scoped dependencies.** `sbt makeBom` emits the **`Compile` scope**, so dependencies
  declared `% Test` (munit, ScalaCheck, Testcontainers, and their transitives) do not appear in
  the SBOM and are never scanned. This is deliberate — those artifacts do not ship, so including
  them would add findings that carry no production risk — but it does mean a green
  `dependency-scan` says nothing about the test toolchain. Verified: no test framework appears in
  any generated SBOM.
- **Frontend CI.** Tracked separately in `expat-ledger-frontend#27`.
- **The three coverage-excluded modules** listed under Gate 1.
- **Reachability.** A suppressed or reported finding says a vulnerable version is on the
  classpath, not that the vulnerable code path is executed. If a suppression rests on
  unreachability, the argument belongs in the entry — written down, not assumed.

## Requirement traceability

No FR or NFR mandates CI-level scanning directly. That gap is recorded rather than closed with
an invented identifier. These gates protect enforcement of **FR-007** (RBAC security),
**FR-008** (data encryption), and **FR-012** (secure authentication), and support the
`AGENTS.md` OWASP ASVS 5.0.0 Level 2 posture as amended by ADR-027.
