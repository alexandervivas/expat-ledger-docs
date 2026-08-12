# Scope CHANGELOG

## 2026-08-10 — Delivery Quality: The Documented Startup Command Is Proven, and Its Topology Is Guarded (issue #89)

**Summary**

- [Issue #89](https://github.com/alexandervivas/expat-ledger-backend/issues/89) asked for one documented command that starts the backend stack. Issue #88 built it — `make up-offline` and `make up-kms` — but nobody had run it from clean volumes and recorded the result, which is what `localstack-local-profile` requires acceptance to rest on. Both runs were performed on 2026-08-10 and are recorded on the issue.
- **The runs found one real defect.** `infra/prometheus/prometheus.yml` still declared a scrape job for `fx-service`, which #88 had removed from `docker-compose.yml`. Prometheus reported that target permanently `down` — `dial tcp: lookup fx-service ... no such host` — on every start of both paths. A stack that is healthy while monitoring a host that does not exist is the same class of defect #88 set out to eliminate, and it survived because the compose topology and the monitoring topology were two hand-maintained lists with nothing holding them together.
- **This closes a stated limit of the issue-87 entry below**, which recorded: "Compose parity for `METRICS_*` is verified manually via `docker compose config`, not by a test; asserting it from Scala means parsing YAML on the test classpath." A test now asserts it, without a YAML dependency: every service built from this repository's own images must declare `METRICS_HOST` and `METRICS_PORT`, bound to `0.0.0.0`, and must be scraped and waited for.
- `localstack-local-profile` is **modified**: nothing declared in the local stack — service _or_ monitoring target — may be unable to start or resolve; the documented sequence must state its prerequisites and name no compose file that does not exist; one image-build path is recorded as the only supported one; and the clean-volume proof must be evidenced for both paths.
- `local-environment-configuration` is **modified**: its metrics requirement named "all five application services" including `fx-service`, which compose has not declared since #88. Corrected to the four that exist, with the compose↔Prometheus correspondence made symmetric and stated over _targets_ rather than jobs.

**Impacts**

- **Local stack**: the dead `fx-service` scrape job is removed, with a comment naming [#115](https://github.com/alexandervivas/expat-ledger-backend/issues/115) as the owner of whether `fx-service` becomes a runnable service. This change makes no decision about `fx-service` itself.
- **Startup gate**: `EXPECT_RUNNING` now covers `prometheus` and `grafana` as well as the four application services. Previously `wait-healthy` reported the stack healthy while asserting four of six. `bootstrap` stays out deliberately — it is a one-shot that must reach `exited 0`, already gated by `service_completed_successfully`.
- **Regression guard**: `LocalStackTopologyContractSpec` in `modules/integration-tests` holds three hand-maintained copies of the topology together — `docker-compose.yml`, `infra/prometheus/prometheus.yml`, and `EXPECT_RUNNING`. It asserts every scrape target names a declared service, on that service's `METRICS_PORT`, under a job of the same name; that every metrics-bearing service is scraped and waited for; and that `EXPECT_RUNNING` invents no service. No YAML library is added: the readers are hand-written and assert both a structural anchor **and** a non-empty result, because a reader that stops matching after a reformat would otherwise pass vacuously, and a guard that silently stops guarding is worse than no guard. Each rule was verified red against a deliberate violation before being accepted.
- **Images**: `prom/prometheus` and `grafana/grafana` are pinned. They were the only unpinned **third-party** images in the compose file — the five `expatledger/*:latest` references are built locally by `make images` — and gating the documented command on both made `:latest` drift a startup failure rather than silent observability decay. The pin buys reproducibility; its cost is a manual bump that nothing watches for, since the CI dependency gate scans sbt-produced SBOMs rather than compose images and there is no Renovate or Dependabot configuration.
- **`PORT` is no longer a footgun**: compose published the gateway on a hardcoded `8080:8080` while passing `PORT=${PORT:-8080}` into the container, so setting `PORT` produced a gateway bound to one port inside a container published on another, reachable at neither. The container's port is now the literal `8080`. `PORT` keeps its meaning for running the gateway outside compose and is still emitted by the generator.
- **Documentation**: README now states the `make setup` ordering constraint (it runs an `apiGateway` task, so it needs a compiling gateway and must precede any step reading `.env`), the full set of published host ports rather than `8080` alone — a frontend dev server collides with Grafana on `3000` far more often — that `PORT` is not adjustable for this stack, the clean-clone state of the git-ignored `infra/keysets/` and its Linux ownership condition, and the recorded image-build decision.
- **Contracts**: no API, gRPC, or event surface change. The `docs/contracts/` currency check was executed for this change against `docs/contracts/openapi/v1/openapi.yaml` and the gRPC and event contracts, and confirmed no contract diff is required.
- **Stated limits**: the clean-volume evidence is a point-in-time run and cannot be re-executed by CI, which does not run Docker Compose; what can be checked statically now is, and `wait-healthy` fails the documented command itself when a local run regresses. Both recorded runs were on Docker Desktop, so the Linux bind-mount ownership condition for `infra/keysets/` is documented but unproven. Grafana starts with no provisioned datasource or dashboard; it is gated as running, not as useful, which makes the documented command depend on a component nobody has wired up — [#128](https://github.com/alexandervivas/expat-ledger-backend/issues/128) owns whether to provision it or stop gating on it.
- **Scope boundaries**: `fx-service`'s future is #115's. CORS (#90), local authentication (#91), and seed data (#92) are excluded by the issue and untouched. The duplicated outbox migrations visible in the recorded logs are #116 and were not addressed.
- **Rollback**: a revert commit. No schema, contract, configuration variable, or production code changed.

**Actions**

- Removed the `fx-service` scrape job from `infra/prometheus/prometheus.yml`, replacing it with a comment naming #115.
- Added `LocalStackTopologyContractSpec` to `modules/integration-tests`; no new dependency in any scope.
- Updated the `Makefile` (`EXPECT_RUNNING` covering `prometheus` and `grafana`) and `docker-compose.yml` (pinned `prom/prometheus` and `grafana/grafana`).
- Updated `README.md` "Getting Started" and "Infrastructure (Docker)".
- `docs/backlog/iteration-*.json` and `BACKLOG.md` remain untouched historical records. No contract file was changed.

**Requirement traceability**

No FR/NFR mandates a documented local startup command; issue #89 records this as a delivery-quality gap and it is carried as one rather than closed with an invented identifier, matching the treatment of the issue-87 entry below. Two requirements are touched in substance: **NFR-002** (observability) — a permanently `down` scrape target is an observability defect, and the symmetry guard is what keeps the metrics topology honest as services come and go; and **NFR-004** (portability) — "one documented command starts the stack from a clean clone" is the portability claim in practice, and the clean-clone prerequisites now documented are the conditions under which it holds.

## 2026-08-08 — Capability Scope: Vault Capabilities Removed, KMS/Tink/LocalStack Capabilities Added (ADR-027, issue #88)

**Summary**

- [ADR-027](/reference/backend/decisions/ADR-027-secret-management-proportionality.md) (Accepted 2026-08-06) replaced HashiCorp Vault with Google Tink AEAD/DAEAD behind the existing `SecretManager` port, keysets wrapped by AWS KMS customer managed keys, static per-environment database credentials, and LocalStack for local development. [Issue #88](https://github.com/alexandervivas/expat-ledger-backend/issues/88) executed it. **Vault no longer exists anywhere in the repository** — code, tests, configuration, `infra/vault/`, `docker-compose.security.yml`, the `vault4s` dependency, and every `VAULT_*` variable are gone.
- **Four capabilities are removed outright, not rewritten**, because their requirements mandated the mechanism ADR-027 deletes:
  - `vault-ale-runtime-cutover` — all requirements removed. It mandated Vault Transit for runtime ALE and **explicitly forbade local Tink keyset providers on the production path**; ADR-027 reverses both.
  - `vault-dynamic-db-credentials` — all requirements removed. Dynamic lease-based credentials are replaced by static per-environment secrets, and `DatabaseCredentials` no longer carries `leaseId`, `leaseDuration`, or `renewable`.
  - `vault-secret-failure-handling` — all requirements removed. Its fail-closed intent is preserved and restated provider-neutrally in the two new secret capabilities; nothing of value is dropped.
  - `vault-disaster-recovery-runbook` — all requirements removed. The 3-of-5 Shamir quorum governance it mandated is structurally unexecutable by one maintainer and describes a component that no longer exists.
- **Three capabilities are added**: `kms-envelope-encryption` (Tink AEAD/DAEAD behind `SecretManager`, KMS-wrapped keysets, tenant-scoped associated data, preserved deterministic equality, fail-closed startup when a keyset cannot be unwrapped); `static-database-credentials` (per-environment secrets, a distinct migration credential holding `CREATE`, least-privilege application credentials, credential values never logged, fail-closed startup); and `localstack-local-profile` (LocalStack in the services' own compose file and network, a non-interactive idempotent bootstrap deriving names from service configuration, a documented offline fallback needing no container or network, and a clean-volume startup proof exercising the real path).
- `local-environment-configuration` is **modified**: its default-honouring requirement enumerated "the defaulted fields of `VaultConfig`", which no longer exists, and is restated against the configuration that replaced it.
- `security-governance-alignment` is deliberately **not** modified. Its secret-management requirements were already rewritten provider-neutrally by the #101 spike, and its "documented posture MUST NOT count as aligned while the runtime contradicts it" requirement is **satisfied** by this change rather than altered by it.

**Impacts**

- **Startup**: fail-closed and ordered once in `ServiceStartup` — credentials, then keyset, then Flyway migration under a `CREATE`-holding migration credential, then bind under the DML-only application credential. A failure in either acquisition reaches neither migration nor a bound port. There is no runtime fallback from the `aws` credential provider to `static`, and none from a KMS-wrapped keyset to a plaintext one.
- **Encryption**: `TinkSecretManager` is the wired `SecretManager` — AES-256-GCM for `routing_details`, `owner_full_name`, and `tax_id`; AES-256-SIV for `account_number`; `tenant_id` bound as associated data throughout. Two KMS customer managed keys, one per keyset, addressed by **alias ARN** and unwrapped once at startup rather than per field. `transaction-service` performs no ALE and loads no keyset.
- **Credential rotation semantics changed**: a rotated secret is picked up on **restart**, not in flight. The lease/refresh loop and the credential-refresh failure race are deleted, because a static secret cannot go stale mid-run. A rotation poller is a follow-up whose trigger is before the first deployed environment runs unattended.
- **Database privileges**: `infra/postgres/init-db.sh` creates `expat_migrator` (holding `CREATE`) and `expat_app` (DML only), using `ALTER DEFAULT PRIVILEGES FOR ROLE` so later Flyway-created tables are usable by the application role. This closes the Flyway `CREATE` gap named in #88 while satisfying ASVS 13.3.2.
- **Local development**: two documented commands — `make up-offline` (plaintext local-only keysets, no container, no network) and `make up-kms` (LocalStack KMS + Secrets Manager). `make clean` is the clean-volume reset and the only supported way to switch paths. `LOCALSTACK_AUTH_TOKEN` is developer-supplied and never committed; the image exits with code 55 without it, which is precisely why the offline fallback is mandated. `infra/keysets/` is git-ignored and holds generated material only.
- **Security**: no key material, token, or production endpoint is committed. Wire-level HTTP logging (`org.apache.hc.client5.http.wire` / `.headers`) is pinned to `WARN` in every module, deliberately below root, because every service now reads credentials through the AWS SDK and raising root to `DEBUG` must not begin printing secrets.
- **Deferred, with recorded triggers — none of these is delivered**: the column-wide **rewrap** path, and with it any rotation of the Tink DAEAD primary key, which would break deterministic equality on `account_number` (trigger: before the first real user data is persisted, or before any index or unique constraint is added to that column); multi-Region KMS keys, `ScheduleKeyDeletion`/`DisableKey` alarms, and a recorded restore rehearsal; per-service IAM roles with key-usage-only grants and CloudTrail retention for KMS `Decrypt`; the **KMS-oriented recovery runbook** replacing `docs/ops/vault-recovery.md`, which means there is currently **no in-force secret-recovery runbook**; and the decision on whether the deterministic capability is exercised at all, accounting for the masked-reference constraint.
- **Determinism is a capability preserved, not a behaviour protected**: `accounts.account_number` still has no index, no unique constraint, and no query behind it. The "indexed exact-match lookups" and "reconciliation and duplicate detection" FR-008 cited as justification do not exist. ADR-027 §3 additionally records that the delivered `statement-import-reconciliation-contracts` capability permits only a masked (`****` plus last four) account reference, which full-value deterministic ciphertext cannot serve — so a keyed blind index over a normalized suffix is the likelier eventual mechanism.
- **Assurance target**: unchanged from the ADR-027 record — OWASP ASVS 5.0.0 **Level 2**, with 13.3.4, 13.1.4, and the hardware-backed elevation of 13.3.1 adopted above it, 13.3.3 deferred on the NFR-001 P95 budget, and a recorded 13.2.1 deviation for static database credentials. Any surviving L3 claim in the requirement set is corrected to L2.
- **Contracts**: no API, gRPC, or event surface change. The `docs/contracts/` currency check was executed for this change against `docs/contracts/openapi/v1/openapi.yaml` and the gRPC and event contracts, and confirmed no contract diff is required.
- **Rollback**: a revert commit. ADR-027's two-adapters-coexist step was a cutover convenience, not a compatibility obligation, and this change completes the deletion step. The configuration seam that survives is `DB_CREDENTIALS_PROVIDER`, which switches credential sourcing without a rebuild.

**Actions**

- Added the `kms-envelope-encryption`, `static-database-credentials`, and `localstack-local-profile` capability specs and removed all requirements from the four `vault-*` capabilities; the retired spec directories are cleared when the change is archived.
- Added `docs/ops/vault-recovery.md`'s **not-in-force** banner. The file is retained, not deleted, because its body records a real tabletop exercise.
- Rewrote `docs/architecture/security-encryption-guide.md` for Tink keysets under KMS master keys, with the master-key-versus-deterministic-key rotation trap stated prominently, discharging that entry in ADR-027's follow-up table.
- Updated `docs/requirements/FR-008-data-encryption.md` (status Implemented; the delivered mechanism; determinism recorded as a preserved capability with the masked-reference constraint; the deterministic-key rotation deferral and its trigger) and the FR-008 row of `docs/requirements/TRACEABILITY.md`.
- Updated `README.md` (secret and ALE stack, the two startup commands, `make clean`, the LocalStack token requirement, the removal of `docker-compose.security.yml` and `.vault.env`), `AGENTS.md` §1.9, and the `openspec/config.yaml` context snapshot (dated 2026-08-08).
- `docs/backlog/iteration-*.json` and `BACKLOG.md` remain untouched historical records. No contract file was changed.

**Requirement traceability**

**FR-008** (data encryption) is the primary requirement; **FR-007** (RBAC security, via ASVS 13.3.2 least privilege and the collapse of Vault's separate authentication domain onto IAM); **NFR-001** (performance, via the ASVS 13.3.3 latency deferral); **NFR-004** (portability, via the retained `SecretManager` port); **USP-007** (zero-knowledge ledger). The proportionality question itself remains a documented traceability gap, recorded in `docs/requirements/TRACEABILITY.md` rather than closed with an invented identifier.

## 2026-08-06 — Delivery Quality: A Fresh Clone Can Boot the Backend (issue #87)

**Summary**

- Closed the gap between the documented local setup path (`make setup`, then `docker compose up`) and the environment the services actually require at load time. Every service reads its configuration through `ConfigSource.default.loadOrThrow`, and every `application.conf` expresses its values as bare optional overrides (`host = ${?HOST}`) with no literal fallback — so any required, non-`Option`, non-defaulted field whose variable is unset kills startup with a pureconfig `KeyNotFound` rather than a diagnosable failure. Three values had fallen out of the emitted environment: `JWT_JWKS_URL` (emitted by nothing), and `METRICS_HOST`/`METRICS_PORT` (passed by compose to `api-gateway` only).
- Corrected the emitted JWT values to the shape Auth0 actually issues. The generator emitted `JWT_ISSUER=expat-ledger` and `JWT_AUDIENCE=expat-ledger-api`; `JwtServiceLive` matches `iss` by exact string and requires `aud` to contain the configured audience, so no Auth0 token could ever have passed. All three values are now consistent Auth0-shaped placeholders naming one tenant, with the issuer's trailing slash preserved, and `make setup` accepts `--auth0-domain`/`--auth0-audience` so a developer with a real tenant produces a working `.env` in one command.
- Removed dead JWT key configuration and the local token-signing tooling built on it, as a product decision recorded on the issue and beyond the issue's literal scope line. Neither `JWT_PUBLIC_KEY` nor `JWT_PRIVATE_KEY` was read by any config class. `scripts/generate_test_token.sh` appeared to make `JWT_PRIVATE_KEY` live, but the path it drove was provably non-functional: `JwtTokenGenerator` signed with no `kid` header, which `JwtServiceLive` rejects before any JWKS lookup, and a locally generated key can never appear in an Auth0 JWKS. Both variables, both scripts, and `JwtTokenGenerator.scala` are gone.
- Found and closed two further classes of boot-blocker that the new guard exposed rather than the issue described: fields whose Scala case classes declare a default that the pureconfig Scala 3 derivation does not apply and `application.conf` never states as a literal (`GrpcServiceConfig.useTls`, `MetricsConfig.enabled`, `TenantServiceConfig.useTls`, `DatabaseConfig.poolSize`, most of `VaultConfig`); and `RabbitMQConfig.ssl`, which nothing supplied at all, plus an unconditional empty `tls { }` block that made `TenantServiceConfig.tls: Option[TlsConfig]` structurally incapable of resolving to `None`.
- Stated one supported JDK. `README.md` said Java 21 while `.tool-versions` pinned `corretto-25.0.1.8.1` and both CI jobs used Temurin 25.

**Impacts**

- **Delivery**: Unblocks the founder validation of R1.1 and the browser verification of R1.2, both of which need a locally running stack.
- **Environment**: `.env.example` is now tracked at the repository root as the single self-describing reference for every variable the services read, classified as required-with-no-default, defaulted in `application.conf`, or genuinely optional. That set was previously discoverable only by reading four `application.conf` files against every config case class. `.env` remains gitignored.
- **Observability**: Container metrics now bind `0.0.0.0` rather than the container loopback the generator's `METRICS_HOST=localhost` produced, so the Prometheus scrape targets already declared in `infra/prometheus/prometheus.yml` can succeed. The missing `transaction-service` scrape target was added.
- **Security**: No key material is added. After the removals the only credential-shaped entries in `.env.example` are `DB_PASSWORD=postgres`, `RABBITMQ_PASSWORD=guest`, and a `GRAFANA_ADMIN_PASSWORD` placeholder — non-secret local defaults already present in `docker-compose.yml`. `detect-private-key` and the gitleaks full-history gate stay clean.
- **Regression guard**: Two pure test suites hold the contract — one in `modules/api-gateway` asserting that `.env.example` and `LocalEnvGenerator` declare the same variable set and that the generated environment loads `ApiGatewayConfig`, and one in `modules/integration-tests` asserting all four services load from an environment containing only the generator's output. A future required-non-`Option` field cannot silently reintroduce this defect.
- **Stated limits**: Authentication against the placeholder values still does not work, and is not meant to; that is the difference between a stack that boots and a stack that authenticates. `db.name` and `vault.address` remain supplied only by `docker-compose.yml`, so running a single service outside compose still needs `DB_NAME` set by hand — documented in `.env.example` rather than papered over. Compose parity for `METRICS_*` is verified manually via `docker compose config`, not by a test; asserting it from Scala means parsing YAML on the test classpath. Env-driven tenant-service TLS is no longer possible and is deferred to its own issue.
- **Contracts**: No API, gRPC, or event surface change. The `docs/contracts/` currency check was executed for this change and confirmed no contract diff is required.
- **Scope boundaries**: All Vault configuration — credentials, role grants, the `.vault.env` `env_file` dependency, and network topology — remains untouched (#88, blocked on #101). Writing `VaultConfig`'s already-declared Scala defaults as HOCON literals makes no Vault decision. Restructuring `application.conf` to carry literal defaults for `host`, `port`, and `metrics.*` is deliberately not done here.

**Actions**

- Added `.env.example`, tracked at the repository root.
- Renamed `JwtKeyGenerator.scala` to `LocalEnvGenerator.scala` and restructured it as a pure `envOnlyLines` plus a `main`; deleted `JwtTokenGenerator.scala`, `scripts/generate_test_token.sh`, and `scripts/generate_jwt_keys.sh`.
- Updated `scripts/setup_local_env.sh` and the `make setup` help text to forward `SETUP_ARGS` to the generator.
- Updated `docker-compose.yml` (literal `METRICS_HOST=0.0.0.0` and `METRICS_PORT` on all five application services, `JWT_JWKS_URL` added to and `JWT_PUBLIC_KEY` removed from `api-gateway`, `RABBITMQ_SSL` added to `tenant-service`) and `infra/prometheus/prometheus.yml`.
- Wrote declared defaults as literals into all four service `application.conf` files and removed the tenant-service `tls { }` block.
- Added `LocalEnvironmentContractSpec` and `ServiceConfigurationBootstrapSpec`, with the supporting `Test / resourceGenerators` entries and coverage-exclusion update in `build.sbt`.
- Updated `README.md` (JDK 25, the `.env.example` pointer, the re-run-`make setup` note, and the Auth0 flow) and `docs/requirements/NFR-004-portability.md` (naming JDK 25 as the supported toolchain while keeping the OpenJDK 21+ runtime floor). `ADR-009`'s Java 21 mention is historical narrative and was left untouched.
- No schema, contract, or deployed-configuration change. `docs/backlog/iteration-*.json` and `BACKLOG.md` remain untouched historical records.

**Requirement traceability**

No FR/NFR mandates local developer environment configuration — recorded as a documented gap rather than closed with an invented identifier. The JDK reconciliation touches **NFR-004** (portability); the Auth0-shaped JWT values align the emitted environment with **FR-012** (JWT RS256 validated against the Auth0 JWKS endpoint); the metrics wiring supports the `AGENTS.md` §2 observability posture without changing a requirement.

## 2026-08-06 — Governance: Standing Authorization for Commit, Push, and Pull-Request Creation

**Summary**

- The repository owner granted **standing authorization for `commit`, `push`, and pull-request creation across all sessions**, replacing the previous rule that required explicit per-session permission for each. Agents must no longer ask for those three operations or pause work to request them.
- **The rationale is that the pull request is the review surface.** The owner comments on implementation choices there and reverts anything they are not comfortable with, so asking beforehand added a round trip without adding oversight.
- **Standing authorization removes the asking, not the verifying.** `sbt test` and `pre-commit run --all-files` must still pass before every commit, hook-applied formatting must be kept, Conventional Commits still apply, and work happens on an issue or feature branch — never directly on `main`.
- **Deliberately excluded from the standing grant**: merging a pull request, because merging closes the review window the owner relies on; closing an issue; history-rewriting and destructive actions (force-push, `reset --hard` on shared branches, remote branch or tag deletion); and release or tag writes. Committing credentials or private keys remains forbidden regardless of authorization.

**Impacts**

- **Governance**: `AGENTS.md` §1.6 changes from a prohibition into a standing grant with a narrow exclusion list, and explicitly supersedes any skill, agent, or tooling prompt that still demands per-action approval. §4 and §5 step 8 are aligned to match, so the three statements of the rule cannot drift apart again.
- **Agent behavior**: the `develop-github-issue` skill §7 previously stated that developing an issue "does not implicitly authorize publication". That is now inverted for the three pre-authorized operations, in all three skill copies (`.claude`, `.opencode`, `.codex`), and its completion report no longer asks whether commit, push, or PR await authorization.
- **Scope**: no requirement, contract, or runtime behavior is affected. No code, contract, migration, compose, or build file is touched.

**Actions**

- Updated `AGENTS.md` (§1.6, §4, §5 step 8) and `develop-github-issue/SKILL.md` in `.claude`, `.opencode`, and `.codex`.

## 2026-08-06 — Governance: Resolve the Conflicting Hosting Decisions (ADR-007 vs ADR-027)

**Summary**

- The decision record contained **two `Accepted` ADRs that contradicted each other on platform**: ADR-007 selected Render Free Tier, while ADR-027 selected AWS for key and secret management. A reader had no way to tell which was current. Resolved by correcting statuses and cross-references — **no new hosting decision is made here.**
- **ADR-007 is now marked `Not in force`**, for two independent reasons recorded in the ADR itself: it was **never executed** — its own Actions call for a `render.yaml` at the repository root that was never committed, and no deployed environment ever existed — and **Render provides no managed KMS**, so a Render deployment would have to reach into AWS for the master key regardless, contradicting the zero-cost premise that was ADR-007's entire rationale. Its body is retained as the historical record of September 2025 intent and explicitly marked as not current guidance.
- **A full hosting decision is recorded as owed and not yet made**, covering compute, database, networking, and the SLO consequences of leaving a free tier. Until it exists, the platform is undecided beyond ADR-027's key-and-secret scope. This is stated in ADR-007, ADR-027, `docs/ops/deployment-render.md`, and `docs/governance/SLOs-SLIs.md` so no reader infers a platform that was never chosen.
- **`docs/ops/deployment-render.md` carries a do-not-follow banner.** It documented a runbook whose first step was to commit a `render.yaml` that never existed, so the procedure never worked — it was never carried out rather than having broken later.
- **`docs/governance/SLOs-SLIs.md` cold-start exclusion is now host-neutral.** It previously excluded "first-hit-after-idle on Render Free" from the P95 SLO, naming a platform that is not in force. The exclusion is retained because JVM warmup (class loading and JIT) is real after any restart on any host, but it is restated without naming a host, and flagged for restatement once hosting is decided — whether idle-suspend must also be excluded depends entirely on whether the platform scales to zero.

**Impacts**

- **Governance**: exactly one live direction on platform, plus an acknowledged gap. Removes the contradiction without inventing a decision that was not made.
- **Scope**: unchanged. No requirement, contract, or runtime behavior is affected. No code, contract, migration, compose, or build file is touched.
- **Checked and deliberately left alone**: ADR-019 remains `Proposed`, which is accurate — its own Context correctly states that OpenTelemetry metrics are implemented while tracing is not, and no `Tracer` or `Span` code exists. ADR-008, ADR-016, and ADR-017 use a `Status:` / `Date:` header style that differs from the `## Status` convention, but all three do declare `Accepted`; this is a formatting inconsistency, not a conflict. ADR-013 → ADR-014 → ADR-015 form a correctly annotated supersession chain.

**Actions**

- Updated `ADR-007-render-hosting.md`, `ADR-027-secret-management-proportionality.md`, `docs/architecture/decisions/index.md`, `docs/ops/deployment-render.md`, `docs/governance/SLOs-SLIs.md`, and the `mkdocs.yml` nav label.

**Requirement traceability**

- NFR-001 (performance — the SLO cold-start exclusion), NFR-004 (portability). Hosting platform selection has no mapped requirement and is recorded as a documented traceability gap.

## 2026-08-06 — Governance: `.junie/guidelines.md` Removed; `AGENTS.md` Becomes the Single Source of Agent Rules

**Summary**

- Removed `.junie/guidelines.md` by user decision: it was outdated and Junie is no longer used. `AGENTS.md` is now the single source of truth for agent operating rules, and its instruction-precedence section no longer names a second file.
- **Migrated the rules that existed only in the deleted file** into `AGENTS.md` rather than dropping them: consumer retry with exponential backoff via fs2 retry logic and mandatory Dead Letter Exchanges for unprocessable messages; avoid N+1 queries, declare critical indexes in an ADR, respect pagination defaults; structured JSON logging with correlation and tenant identifiers and never secrets or PII; the idempotency detail that `(route, key, response_hash)` is persisted and ingestion deduplicates on `(tenant_id, source_id)`; and the prohibition on force-pushing to `main`. Added a new `AGENTS.md` §1.9 "Repository Facts" carrying the durable CI, tooling, MkDocs-YAML-exclusion, and contract-location facts.
- **Deliberately not migrated:** the deleted file's two coverage targets (100% for domain logic and a ≥70% goal), because they conflicted with each other and with the enforced gate. `AGENTS.md` §1.9 now states that `build.sbt` is authoritative at 90% aggregate statement coverage per ADR-026. Also not migrated: the `feat/<scope>-<short>` branch convention, which conflicts with the `issue/<number>-<slug>` convention the `develop-github-issue` skill uses for issue work, and the reference to a `docker-compose.app.yml` that does not exist.
- Removed the now-dangling references in `mkdocs.yml` navigation, all three `develop-github-issue` skill definitions, and the `.claude/`, `.codex/`, and `.opencode/` agent definitions.
- **Incidental fix:** the removed `mkdocs.yml` nav entry `Agents Operating Manual: .junie/guidelines.md` had **always been broken**. `docs_dir` defaults to `docs/`, so that path resolved to `docs/.junie/guidelines.md`, which never existed. Removing it repaired a latent dead link rather than dropping a published page; `AGENTS.md` lives at the repository root and is deliberately outside the docs site.

**Impacts**

- **Governance**: instruction precedence is now single-source, removing the possibility of two mandatory files disagreeing — which had already occurred, since the deleted file asserted an ASVS L3 posture that ADR-027 amends.
- **Coverage reconciliation**: this closes two of the four conflicting documented coverage targets tracked by [#93](https://github.com/alexandervivas/expat-ledger-backend/issues/93). `README.md` retains a 100%-for-domain-logic aspiration, so #93 remains open but narrower. `docs/ops/ci-quality-gates.md` is updated to describe the reduced conflict accurately.
- **Not in scope of issue #101.** This was a user-directed change made in the same session and is recorded separately so the #101 delivery record stays accurate.

**Actions**

- Deleted `.junie/guidelines.md` and the empty `.junie/` directory.
- Updated `AGENTS.md`, `mkdocs.yml`, `docs/ops/ci-quality-gates.md`, `docs/ops/opencode-openspec-agentic-workflow.md`, and 15 agent/skill definition files.
- Left the archived OpenSpec change `2026-08-06-issue-78-real-ci-security-gates` untouched; its references are a historical record of what was true when it shipped.

## 2026-08-06 — Scope: Secret Management Proportionality — Vault Removed, ASVS Target Amended to L2 (issue #101)

**Summary**

- **Amended the declared assurance level.** The inherited `AGENTS.md` claim of an "OWASP ASVS L3 posture" is replaced by **OWASP ASVS 5.0.0 Level 2** as the verified target, recorded in ADR-027. Adopted above L2 deliberately: **13.3.4** and **13.1.4** (documented secret expiry and rotation schedule) and the **hardware-backed elevation of 13.3.1** (managed HSM-backed KMS). Deferred with a revisit condition: **13.3.3** (all cryptographic operations inside an isolated security module), on the NFR-001 P95 < 200 ms budget — revisit when there are real users and a measured latency budget, or when regulatory scope changes. The L3 claim was never delivered: a self-signed, single-node Vault container is software-only and so never satisfied 13.3.1's hardware-backed elevation.
- **Decided the posture.** HashiCorp Vault is removed from every path, not deprecated. Application-level encryption becomes Google Tink AEAD (AES-256-GCM) and DAEAD (AES-256-SIV) behind the retained `SecretManager` port, with keysets wrapped by AWS KMS customer managed keys through Tink's KMS envelope integration. Database credentials become **static per-environment secrets in AWS Secrets Manager** on a documented rotation schedule, a **deliberate recorded deviation from ASVS 13.2.1 (L2)** with RDS IAM database authentication named as the clean upgrade. Local development uses **LocalStack** in the same compose file and network, with a non-interactive idempotent init and a documented offline fallback.
- **Deterministic encryption of queryable fields is preserved.** AES-256-SIV is deterministic authenticated encryption with `tenant_id` retained as associated data, so an index or unique constraint on `account_number` remains possible and cross-tenant collision remains impossible.
- **Answered the archived open question.** The archived change `2026-02-18-vault-runtime-cutover-and-dynamic-db-creds` shipped asking whether local development should always require Vault DB secrets engine setup or have an explicit non-production fallback profile. The answer is recorded: **no to Vault, yes to an explicit non-production profile** — LocalStack, plus a documented offline fallback needing no container and no network.
- **Selected AWS as the platform for key and secret management**, on HSM backing for 13.3.1, native rotation for 13.3.4, the already-declared `tinkAwsKms` dependency, RDS IAM as the 13.2.1 upgrade, and faithful LocalStack emulation. This **conflicts with ADR-007 (Hosting on Render Free Tier), which is `Accepted`**; ADR-027 supersedes it **only** as to key and secret management, and a hosting ADR covering compute, database, networking, and the SLO consequences of leaving a free tier is owed.
- **Corrected premises found during the spike**, recorded rather than repeated: `infra/keysets/` **does not exist at all** (the compose mount would silently create an empty directory); **no index, unique constraint, or query backs the determinism claim** (`accounts.account_number` is plain `TEXT NOT NULL` and reads key on `id`/`tenant_id` only), so FR-008's justification is forward-looking; **nothing is deployed** — there is no `Dockerfile` and no `render.yaml`, so Vault was a local-development tax rather than a production dependency; **ADR-020 was never accepted** and stood at `Proposed` while a runtime and four capability specs were built on it; and `docs/ops/vault-recovery.md` commits the project to a **3-of-5 Shamir quorum with at least two distinct custodians**, which a single maintainer cannot form, making the committed runbook structurally unexecutable and a sealed Vault an unrecoverable outage.
- **Cost evidence, whole-solution rather than component-only.** Key management is **0.4–2.4% of the monthly bill on every platform** evaluated; compute and Postgres dominate. The Vault question was therefore never a cost question but an operability and assurance question. Self-hosting Vault would add ~$36–40/month, more than the entire rest of the security stack.

**Impacts**

- **Security**: The assurance claim now cites its standard version, its adopted additions, its deferral with a revisit condition, and its one deviation by identifier, instead of asserting a level. Master key material moves to an HSM-backed managed KMS; keysets are never plaintext at rest in a deployed environment; ADR-018's prohibition on plaintext master keys in environment variables remains in force and is the stated reason unwrapped keysets in platform secret storage were rejected.
- **Risks accepted and recorded**: key material now exists in application memory (the deliberate 13.3.3 deferral); losing a KMS master key makes all ciphertext unrecoverable, requiring multi-Region keys, deletion protection, a long deletion waiting period, alarms on `ScheduleKeyDeletion` and `DisableKey`, and a rehearsed restore; and AWS account compromise now reaches both keys and secrets, giving up Vault's separate authentication domain, mitigated per 13.3.2 by per-service IAM roles with key-usage-only grants, key policies denying administrative actions to runtime roles, MFA on administrative principals, and retained decrypt audit logging.
- **Delivery**: [#88](https://github.com/alexandervivas/expat-ledger-backend/issues/88) is unblocked and most of its scope disappears — the `backend-role` drift, the Flyway `CREATE` privilege gap, and the Vault TLS-trust problem are resolved by removal, and the split compose networks stop mattering; its remaining work is the LocalStack profile and a clean-volume proof. [#89](https://github.com/alexandervivas/expat-ledger-backend/issues/89) inherits a simpler single startup command. [#91](https://github.com/alexandervivas/expat-ledger-backend/issues/91) and [#92](https://github.com/alexandervivas/expat-ledger-backend/issues/92) are unaffected except through the startup path.
- **Migration**: **Re-encryption of data at rest is not required.** No deployed environment and no persisted production ciphertext exist; local and test data are synthetic and disposable. This is the strongest reason to decide now — the migration is free today and will not be once real ciphertext exists.
- **Documentation superseded in direction**: `docs/ops/vault-recovery.md` and `docs/architecture/security-encryption-guide.md` both carry status banners and are not deleted, because the first records a real tabletop exercise. A KMS-oriented recovery runbook whose custodianship model is executable by one person, and a Tink keyset-rotation rewrite of the encryption guide, are owed by the implementing change.
- **Process**: ADR-027 introduces the requirement that a declared assurance level cite its standard and its evidence, and that documented posture does **not** count as aligned while the runtime contradicts it.
- **Scope boundaries**: this change implements nothing. No Scala source, contract, migration, compose, or build file is touched. Migrating or re-encrypting data, changing the deployed runtime (there is none), fixing #88's concrete defects, and superseding ADR-007 in full all remain out of scope. Messaging (the ~5-line AMQP surface behind the existing `EventPublisher[F]` port) and the missing `account_number` index are recorded as findings deserving their own issues.

**Actions**

- Added `docs/architecture/decisions/ADR-027-secret-management-proportionality.md` (Accepted) and its `docs/architecture/decisions/index.md` entry.
- Set `docs/architecture/decisions/ADR-020-centralized-secret-management.md` to `Superseded by ADR-027`, noting that it was never accepted.
- Retargeted `docs/architecture/decisions/ADR-018-application-level-encryption.md` to `Partially superseded by ADR-027`: its Tink AEAD/DAEAD mechanism is reinstated, its key-management sections remain superseded, and its prohibition on plaintext master keys remains in force.
- Amended the `AGENTS.md` §2 assurance claim and the `openspec/config.yaml` generated-artifact context, with no other guardrail changed.
- Rewrote `docs/requirements/FR-008-data-encryption.md` to the ADR-027 posture, marked it forward-looking with status `In progress`, and restated the deterministic-encryption justification as forward-looking.
- Updated `docs/requirements/USP-007-zero-knowledge-ledger.md` to name ADR-027 and to state that "zero-knowledge" means application-layer encryption with host-blind storage, not a zero-knowledge proof system.
- Updated `docs/requirements/TRACEABILITY.md` for FR-007 and FR-008 and added a `Documented Traceability Gaps` subsection recording the proportionality question.
- Added status banners to `docs/ops/vault-recovery.md` and `docs/architecture/security-encryption-guide.md` without rewriting either body.
- `docs/backlog/iteration-*.json` and `BACKLOG.md` remain untouched historical records.

**Requirement traceability**

**FR-008** (data encryption), **FR-007** (RBAC security), **NFR-001** (performance, via the ASVS 13.3.3 latency deferral), **NFR-004** (portability, via the retained `SecretManager` port), **USP-007** (zero-knowledge ledger). The proportionality question itself has no mapped requirement and is recorded as a documented traceability gap in `docs/requirements/TRACEABILITY.md` rather than closed with an invented identifier.

## 2026-08-05 — Scope: Real CI Security Gates Replace the Fake T2.11 Step (issue #78)

**Summary**

- Added CI-level verification as a delivered capability: dependency vulnerability scanning and secret scanning now gate every pull request and every push to `main`, with the dependency scan additionally running weekly. Recorded in ADR-026.
- Removed the step named `Security Audit (Fake step for T2.11)`, whose entire body re-ran four security specs that had already executed in the preceding `sbt coverage test`, and the `Check coverage threshold` step, whose body was `echo "Coverage check completed."`. Neither could fail. Historical backlog task T2.11 was closed as delivered on the strength of those two steps, so the recorded claim ("automated security suite in CI/CD pipeline… 90% coverage gate") did not match behavior on `main`.
- Corrected a premise recorded in the issue: the 90% coverage gate was **already genuinely enforced** by `build.sbt` (`coverageMinimumStmtTotal := 90`, `coverageFailOnMinimum := true`). Verified by evidence — aggregate statement coverage 94.16% passes at the committed minimum, and the same command exits non-zero when the minimum is unreachable. What was hollow was the CI step, not the enforcement, so no coverage configuration was changed.
- Deliberately pulled forward from R4 into R1 by product decision on 2026-08-04, recorded on issue #78: R1.2 places real bank-statement handling (#79–#83) onto this pipeline, so the gate must exist before that data does.

**Impacts**

- **Security**: The pipeline now fails on unsuppressed High/Critical dependency vulnerabilities and on any secret detected anywhere in git history. Suppression is only ever a committed, justified, expiring allowlist entry — never a flag, environment variable, or workflow-level severity adjustment. `--ignore-unfixed` is deliberately not used.
- **Verification integrity**: A non-vacuity guard (`scripts/check_sbom_inventory.sh`) fails the job when the dependency inventory collapses. Because this repository has no lockfile or `pom.xml`, a naive filesystem scan finds zero dependencies and exits 0 — which would have reproduced the exact T2.11 failure mode. The inventory is therefore generated from sbt's own resolution as a CycloneDX SBOM per module.
- **Known accepted debt**: The new gate surfaces 7 pre-existing High findings (0 Critical) on `main`, all with published fixes. Remediation was out of scope for #78 and is tracked by #99. They are suppressed in `.trivyignore.yaml` with `expired_at: 2026-11-05`, which trivy enforces natively — CI will fail on that date unless each is fixed or re-justified.
- **Documented limits**: The 90% coverage gate binds 6 of 9 modules; `maintenance-worker`, `shared-test-kernel`, and `integration-tests` opt out. This is now stated in documentation rather than implied away, since "90% enforced" without the qualifier is the same species of overclaim this change corrects.
- **Contracts**: No API, gRPC, or event surface change. The `docs/contracts/` currency check was executed for this change and confirmed no contract diff is required.
- **Scope boundaries**: SAST, DAST, penetration testing, container-image scanning, and runtime hardening remain out of scope. Frontend CI is tracked in `expat-ledger-frontend#27`. Reconciliation of the four conflicting documented coverage targets is tracked in #93; this change states the enforced number and defers the rest, leaving `AGENTS.md` and `.junie/guidelines.md` unedited.

**Actions**

- Added `docs/architecture/decisions/ADR-026-ci-security-gates.md` (Accepted) and its `docs/architecture/decisions/index.md` entry.
- Added `docs/ops/ci-quality-gates.md` describing every gate, its local reproduction command, both suppression paths and their unequal expiry enforcement, the seeded-debt list, and what the gates explicitly do not cover.
- Rewrote `.github/workflows/ci.yml` into three jobs — `build`, `dependency-scan`, `secret-scan` — with every step named for the verification it performs.
- Added `.trivyignore.yaml`, `.gitleaks.toml`, `scripts/check_sbom_inventory.sh`, and the build-time-only `sbt-sbom` plugin.
- Updated the `README.md` testing and CI description to match delivered behavior.
- Filed #99 for the 7 pre-existing High dependency findings.
- No Scala source, module, or database change. `docs/backlog/iteration-*.json` and `BACKLOG.md` remain untouched historical records; T2.11's record is not rewritten.

**Requirement traceability**

No FR/NFR mandates CI-level scanning directly — recorded as a documented gap rather than closed with an invented identifier. The gates protect enforcement of **FR-007** (RBAC security), **FR-008** (data encryption), and **FR-012** (secure authentication), and support the `AGENTS.md` OWASP ASVS L3 posture.

## 2026-08-04 — Scope: PDF Statement Import Moved Into R1 (issue #79)

**Summary**

- Reversed FR-005's recorded deferral of PDF import. Direct PDF bank-statement ingestion is now **in scope for R1**, delivered by the R1.2 "ABN Happy Path" slice (ABN AMRO layout only).
- Approved explicitly by the product owner on 2026-08-04 on issue [#79](https://github.com/alexandervivas/expat-ledger-backend/issues/79). Stated rationale: the investigation into how to parse statement PDFs is complete, and direct PDF ingestion materially accelerates getting real data into the platform, so the original "high implementation complexity and low immediate ROI" basis for the deferral no longer holds.
- Fixed the authoritative public contract for the flow — statement upload, import-draft retrieval and lifecycle, reconciliation outcome, confirmation, and discard — as five additive `/v1/statement-imports` OpenAPI operations, with no implementation in this change.
- Recorded the accompanying architectural decisions in ADR-025: the durable import-draft aggregate and its `AWAITING_REVIEW`/`CONFIRMED`/`DISCARDED`/`EXPIRED` lifecycle, transient-only raw-file handling with a 24-hour review window and no durable or backup retention, safe-metadata-only provenance with a fixed-width masking rule, an idempotency fingerprint over `(accountId, fileHash)`, the two-state reconciliation with an always-present exact decimal difference, the `urn:expat-ledger:problem:statement-import:*` failure namespace, and a deliberate NFR-001 P95 carve-out for synchronous parse.

**Impacts**

- **Scope**: FR-005 no longer defers PDF import. Excel/CSV ingestion is unchanged; PDF import adds a review-and-confirm workflow that Excel/CSV ingestion does not have. Row-level preview and correction, automatic account matching, overlapping-period detection, and the Bancolombia and ING PDF layouts remain deferred beyond R1.2.
- **Privacy**: Raw statement content is made structurally unrepresentable rather than merely prohibited by policy — binary content may appear only in the upload request part, no response media type is binary, no artifact-retrieval operation exists, and every new object schema forbids additional properties. Persisted provenance is safe metadata only, with account references masked at fixed width so the masked value leaks nothing about the original's length, country, or format.
- **Security**: All five operations require bearer authentication plus the membership-validated `X-Tenant-Id` selector (ADR-022); cross-tenant drafts are concealed behind the same not-found outcome as nonexistent identifiers, and all three mutations require `Idempotency-Key` (ADR-004, FR-009).
- **Contracts**: Purely additive, non-breaking `/v1` change; `info.version` bumped `1.3.0` → `1.4.0`. No authoritative gRPC or Avro event contract change. This is the backend/frontend agreement for the R1.2 upload, review, and confirmation screens, so `expat-ledger-frontend` must be notified through the shared product project before it builds against these shapes.
- **Delivery**: Unblocks the four queued R1.2 implementation issues — #80 (transient intake), #81 (ABN AMRO parser), #82 (exact reconciliation), and #83 (atomic confirmation).

**Actions**

- Added `docs/architecture/decisions/ADR-025-statement-import-draft-lifecycle.md` (Accepted) and its `docs/architecture/decisions/index.md` entry.
- Added the five `/v1/statement-imports` paths and nine `Statement*` component schemas to `docs/contracts/openapi/v1/openapi.yaml`, and appended the dated `docs/contracts/openapi/v1/CHANGELOG.md` entry.
- Amended `docs/requirements/FR-005-ingestion-engine.md` to record PDF statement import as in scope for R1 with pointers to R1.2 and ADR-025, replacing the "PDF Import deferred" clause.
- Updated `docs/requirements/TRACEABILITY.md` for FR-003, FR-005, FR-009, FR-011, and NFR-002.
- No Scala source, build, or database change; `docs/backlog/iteration-*.json` and `BACKLOG.md` remain untouched historical records.

## 2026-03-10 — Maintenance: Compliance Report Worker (T5.5)

**Summary**

- Added a first implementation slice for privileged compliance exports in `maintenance-worker`.
- Introduced tenant-scoped FBAR and Model 720 export commands backed by Vault-mediated decryption, direct Skunk reads, deterministic CSV/PDF rendering, and artifact manifest generation.
- Defined provenance and integrity metadata for generated compliance artifacts and added focused tests for tenant isolation, decrypt-path enforcement, and output structure.

**Impacts**

- **Security**: Keeps decrypted compliance export handling inside the privileged maintenance boundary with Vault-only decrypt operations and explicit cross-tenant rejection.
- **Compliance**: Establishes a concrete operational path for FBAR and Model 720 artifact generation tied to `FR-015` and `USP-001`.
- **Governance**: Aligns export requirements with auditable artifact provenance and integrity expectations.

**Actions**

- Updated `maintenance-worker` build/runtime wiring to reuse `shared-kernel` Vault and persistence primitives.
- Added compliance report domain, repository, service, renderers, sink, and focused tests in `modules/maintenance-worker`.
- Updated `docs/requirements/FR-015-automated-export.md` and `docs/requirements/USP-001-tax-residency-ready-exports.md`.

## 2026-02-18 — Infra: Open Banking (Plaid/PSD2) Adapter (T5.1)

**Summary**

- Added a vendor-neutral Open Banking adapter boundary for Plaid/PSD2 ingestion using normalized account/transaction models.
- Implemented strict mapping from provider payloads to internal `Account` and `Transaction` domain entities, including fail-closed validation paths.
- Added tenant-context guards, structured mapping error semantics, and transaction reconciliation deduplication by external transaction ID.
- Wired Open Banking adapter/mapping boundaries into account and transaction service composition roots.

**Impacts**

- **Architecture**: Reinforces anti-corruption boundary by isolating provider payloads to infrastructure-only types.
- **Security**: Maintains tenant isolation with explicit tenant-context enforcement for mapping paths.
- **Reliability**: Prevents partial persistence on unmappable payloads and improves sync idempotency for repeated external records.

**Actions**

- Added Open Banking port/model contract in `modules/shared-kernel`.
- Added Plaid/PSD2 adapter and transaction mapping/reconciliation in `modules/transaction-service`.
- Added account mapping from normalized external data in `modules/account-service`.
- Added mapper/adapter/reconciliation tests in account/transaction service test suites.
- Updated `docs/backlog/iteration-5.json` (`T5.1` status `done`, iteration status `in_progress`) and re-rendered `BACKLOG.md`.

## 2026-02-18 — Governance: Vault Disaster Recovery Runbook (T4.6)

**Summary**

- Added an operational Vault disaster recovery runbook for breach and catastrophic recovery scenarios.
- Standardized manual unseal guidance with Shamir quorum controls, role separation, and audit evidence capture.
- Defined backup/restore, post-restore validation gates, and containment-first incident sequencing before service re-entry.
- Synchronized backlog/governance traceability for Iteration 4 task `T4.6`.

**Impacts**

- **Security**: Improves incident response posture for compromised credentials/tokens by enforcing containment before rotation and restart.
- **Reliability**: Adds deterministic recovery gates to reduce partial-restore failures and unsafe re-entry of dependent services.
- **Governance**: Documents auditable responder roles and decision checkpoints for Tier 0 Vault operations.

**Actions**

- Added `docs/ops/vault-recovery.md`.
- Updated `docs/backlog/iteration-4.json` (`T4.6` status to `done`) and re-rendered `BACKLOG.md`.

## 2026-02-18 — Vault Runtime Cutover and Dynamic DB Credentials

**Summary**

- Implemented Vault Transit runtime wiring for cryptographic operations in service composition roots, replacing Tink as the runtime provider in target services.
- Added Vault Database Secrets Engine-based credential bootstrap for service startup in `tenant-service` and `account-service`.
- Introduced lease-aware credential refresh management with bounded retries and controlled failure signaling when refresh is exhausted.
- Updated FR-008/traceability/backlog artifacts to align governance language with ADR-020 execution.

**Impacts**

- **Security**: Removes runtime fallback to local keyset crypto in target services and enforces fail-closed startup when Vault-backed secret operations are unavailable.
- **Reliability**: Adds explicit runtime signaling for credential refresh exhaustion, making failure modes observable and deterministic.
- **Governance**: Brings requirements and backlog status in sync with implemented Vault-centric architecture.

**Actions**

- Added `VaultDatabaseCredentialsManager` and `VaultRuntimeError` in `shared-kernel`.
- Updated `tenant-service` and `account-service` runtime wiring to consume `VaultAdapter` and dynamic DB credentials.
- Updated `docs/requirements/FR-008-data-encryption.md`, `docs/requirements/index.md`, `docs/requirements/TRACEABILITY.md`, and `docs/backlog/iteration-4.json`.

## 2026-01-11 — Vault Hardening: Misconfiguration Fix for Vault-Agent

**Summary**

- Fixed `vault-agent` misconfiguration in `docker-compose.security.yml` by mounting the `vault_keys` volume and correctly mapping the configuration file.
- Updated `infra/vault/agent-config.hcl` to point to the correct secret paths (`/secrets/role_id` and `/secrets/secret_id`) in the dedicated `/secrets` volume.
- Applied the Principle of Least Privilege by using read-only mounts and restricting directory access.

**Impacts**

- **Reliability**: Ensures the `vault-agent` can correctly authenticate using the AppRole credentials generated by the `vault-init` service.
- **Security**: Hardened container mounts by making them read-only and avoiding mounting entire host directories.

**Actions**

- Modified `docker-compose.security.yml` to update `vault-agent` volumes.
- Refactored `infra/vault/agent-config.hcl` with correct paths and security settings.

## 2026-01-11 — Vault Hardening: Suppressed Sensitive Output

**Summary**

- Removed the printing of the Vault Unseal Key and Root Token to standard output during initialization.
- Secrets are now only stored in the secure `/secrets` volume, preventing exposure in container logs.

**Impacts**

- **Security**: Prevents accidental exposure of highly sensitive bootstrap credentials in log aggregation systems.

**Actions**

- Refactored `infra/vault/init-vault.sh` to remove `echo` statements for `UNSEAL_KEY` and `ROOT_TOKEN`.

## 2026-01-11 — Vault Hardening: Minimized Root Session Exposure

**Summary**

- Reduced the exposure of the Vault Root Token by eliminating the redundant re-login session at the end of the initialization process.
- Ensured the `vault-init` container terminates immediately after revoking its own ephemeral bootstrap token.

**Impacts**

- **Security**: Aligns with the Principle of Least Privilege by ensuring no highly privileged root sessions remain active in the Vault server's state after infrastructure setup is complete.

**Actions**

- Refactored `infra/vault/init-vault.sh` to remove the unnecessary `vault login $ROOT_TOKEN` step after bootstrap cleanup.

## 2026-01-11 — Vault Hardening: Isolated Secret Storage

**Summary**

- Moved sensitive Vault credentials (unseal keys, root tokens, AppRole IDs) from host-bound mounts to an isolated Docker named volume (`vault_keys`).
- Hardened the `vault-init` service by making the script directory mount read-only (`:ro`).
- Updated the initialization script to use the secure `/secrets` mount path for persistent data.

**Impacts**

- **Security**: Prevents accidental leakage of sensitive credentials onto the host filesystem and reduces the risk of committing secrets to version control.
- **Compliance**: Aligns with container security best practices by isolating secrets from the application source code.

**Actions**

- Modified `docker-compose.security.yml` to define `vault_keys` volume and update mount points.
- Updated `infra/vault/init-vault.sh` to write/read from `/secrets/`.

## 2026-01-11 — Vault Hardening: Refined Bootstrap Policy

**Summary**

- Hardened the temporary "Bootstrap" policy used during Vault initialization by applying the Principle of Least Privilege.
- Replaced broad wildcard permissions (`sys/auth/*`, `sys/policies/acl/*`, `sys/mounts/*`) with targeted paths specific to the initialization script.
- Removed unnecessary `sudo` capabilities from the bootstrap token.

**Impacts**

- **Security**: Significantly reduces the potential impact of a compromised bootstrap token by restricting it to only the operations required for the initial setup (e.g., enabling Transit/KV engines and configuring the `backend` policy).
- **Compliance**: Adheres to strict security standards regarding ephemeral privileged access.

**Actions**

- Modified `infra/vault/init-vault.sh` to refine the `bootstrap` policy with granular path-level permissions.

## 2026-01-11 — Vault Hardening: Infrastructure Health Checks

**Summary**

- Implemented Docker Health Checks for the HashiCorp Vault service.
- Replaced the manual waiting loop in `init-vault.sh` with a native `service_healthy` dependency in Docker Compose.
- Standardized service orchestration in the security stack.

**Impacts**

- **Reliability**: Ensures that bootstrapping scripts and dependent services only attempt to connect to Vault when its API is fully responsive.
- **Maintainability**: Cleaner initialization scripts by removing redundant infrastructure-level polling.

**Actions**

- Modified `docker-compose.security.yml` to include a `healthcheck` for the `vault` service.
- Updated `vault-init` dependency to use `condition: service_healthy`.
- Simplified `infra/vault/init-vault.sh` by removing the manual retry loop.

## 2026-01-11 — Vault Hardening: Privileged Access Management

**Summary**

- Reduced reliance on the Vault Root Token during the automated initialization process.
- Implemented a "Bootstrap" token pattern: the root token is used only to create a constrained bootstrap policy and token.
- All subsequent setup (Transit engine, AppRole, policies) is performed using the temporary bootstrap token.
- Automated revocation of the bootstrap token after the initialization is complete.

**Impacts**

- **Security**: Aligns with the Principle of Least Privilege. Limits the exposure of the root token during service bootstrapping.
- **Compliance**: Follows HashiCorp's recommended best practices for production-ready Vault deployments.

**Actions**

- Modified `infra/vault/init-vault.sh` to include a multi-stage login and token lifecycle.
- Created a `bootstrap` policy with minimal permissions required for the initial setup.

## 2026-01-11 — Vault Hardening: TLS Implementation

**Summary**

- Hardened HashiCorp Vault infrastructure by enabling TLS (HTTPS) for all communications.
- Removed insecure `tls_disable = 1` configuration in `docker-compose.security.yml`.
- Implemented self-signed certificate generation for local development.
- Automated certificate generation as part of the `make setup` workflow.

**Impacts**

- **Security**: Mitigated risk of secret leakage in transit. All tokens and sensitive data are now encrypted.
- **Compliance**: Aligns with security best practices even for development environments.

**Actions**

- Generated self-signed certificates in `infra/vault/tls/`.
- Created `infra/vault/generate-certs.sh` and integrated it into `Makefile` (`make setup`).
- Modified `docker-compose.security.yml` to mount certificates and configure the TCP listener for TLS.
- Updated `infra/vault/init-vault.sh` to support HTTPS and trust the local CA.

## 2026-01-11 — Vault Infrastructure & Bootstrapping

**Summary**

- Implemented T4.1: "Infra: Vault Persistence, Bootstrapping & Auto-Unseal".
- Established HashiCorp Vault as a Tier 0 service in the security stack.
- Automated Vault initialization, unsealing, and engine configuration via shell scripting.

**Impacts**

- **Security**: Centralized secret management with automated Transit Engine setup for ALE.
- **Resilience**: Persistent volumes for Vault data ensure stability across container restarts.
- **Portability**: Provided templates for Auto-Unseal and AppRole authentication (Vault Agent).

**Actions**

- Created `infra/vault/init-vault.sh` (Bootstrapping script).
- Created `docker-compose.security.yml` (Security infrastructure orchestration).
- Created `infra/vault/agent-config.hcl` (Vault Agent & Auto-Unseal documentation).
- Updated `docs/backlog/iteration-4.json` and re-rendered `BACKLOG.md`.

## 2026-01-11 — Refinement of SecretManager Port

**Summary**

- Restored deterministic encryption methods (`encryptDeterministic`, `decryptDeterministic`) to the `SecretManager` port to fulfill ADR-018 requirements for searchable encrypted fields.
- Decoupled administrative operations by moving `rotateKey` from `SecretManager` to a new `AdministrativeSecretManager` trait.
- Updated ADR-020 and Iteration 4 backlog to reflect the split between application-facing and administrative security ports.

**Impacts**

- **Functionality**: Re-enables support for exact-match searching on sensitive fields like account numbers.
- **Security**: Reduces the attack surface of the primary application port by isolating administrative tasks.
- **Clean Architecture**: Better alignment with the Interface Segregation Principle.

**Actions**

- Modified `modules/shared-kernel/src/main/scala/com/expatledger/kernel/domain/auth/SecretManager.scala`.
- Created `modules/shared-kernel/src/main/scala/com/expatledger/kernel/domain/auth/AdministrativeSecretManager.scala`.
- Modified `docs/architecture/decisions/ADR-020-centralized-secret-management.md`.
- Updated `docs/backlog/iteration-4.json` and re-rendered `BACKLOG.md`.

## 2026-01-11 — Ports & Adapters for Security Layer

**Summary**

- Decoupled the security layer by introducing the implementation-agnostic `SecretManager` Port.
- Updated ADR-020 to reflect the Hexagonal Architecture approach for ALE and secret management.
- Transitioned ALE strategy from direct library dependencies (Tink) to a Port-based abstraction to avoid vendor lock-in.

**Impacts**

- **Portability**: The system can now transition between different secret providers (Vault, AWS KMS, Local Mocks) without modifying business logic.
- **Maintainability**: Centralized the ALE interface in the `shared-kernel` domain layer.

**Actions**

- Created `modules/shared-kernel/src/main/scala/com/expatledger/kernel/domain/auth/SecretManager.scala`.
- Modified `docs/architecture/decisions/ADR-020-centralized-secret-management.md`.
- Updated `docs/backlog/iteration-4.json`.

## 2026-01-11 — Centralized Secret Management Policy

**Summary**

- Added ADR-020: Centralized Secret Management via HashiCorp Vault.
- Proposed the integration of HashiCorp Vault as the primary Secrets-as-a-Service provider.
- Defined the use of Vault's Transit Secret Engine for App-Level Encryption (ALE), explicitly superseding the library choice in ADR-018 (Tink) while preserving its security principles.
- Outlined plans for local development (Docker-based Vault), key rotation, and secret storage (DB credentials, Auth0 secrets using KV Secrets Engine and AppRole/K8s authentication).

**Impacts**

- **Security**: Raw keys and secrets are never stored in the application environment or logs; centralized control and auditing.
- **Complexity**: Introduces a new system dependency and requires a Vault client in the backend modules.
- **Availability**: Vault becomes a "Tier 0" service critical for system operation; High Availability (HA) configuration mandatory for production.

**Actions**

- Created `docs/architecture/decisions/ADR-020-centralized-secret-management.md`.
- Modified `docs/architecture/decisions/index.md`.
- Updated `docs/backlog/iteration-3.json`.
- Re-rendered `BACKLOG.md`.

## 2026-01-11 — Iteration 3: Financial Operations & The Ledger Completed

**Summary**

- Successfully completed all tasks for Iteration 3, establishing the core financial infrastructure.
- Implemented **Account Service** with bank catalog and encrypted persistence for sensitive data.
- Implemented **Transaction Service** with multi-currency ledger, balance snapshotting, and RabbitMQ event consumers.
- Developed a **Config-Driven Ingestion Engine** for parsing bank statements (XLS, XLSX, CSV) with support for international number formats and custom templates.
- Implemented **Remittance Linkage** with a heuristic matcher (date proximity + FX equivalence) and human-in-the-loop confirmation flow.
- Integrated **Application-Level Encryption (ALE)** across all persistent layers for PII and financial identifiers.
- Enhanced observability with structured logging and Prometheus metrics for database and gRPC performance.
- Hardened the domain models using Scala 3 opaque types and smart constructors for all sensitive fields.

**Impacts**

- **Functionality**: The system can now handle the full lifecycle of cross-border financial data ingestion and reconciliation.
- **Security**: Achieved high-rigor data protection at rest, even in the event of database compromise.
- **Performance**: Validated balance snapshotting strategy to meet P95 latency targets (< 200ms) for large ledgers.
- **Resilience**: Improved outbox polling and event publishing with better error handling and retries.

**Actions**

- Updated `docs/backlog/iteration-3.json` status to `done`.
- Re-rendered `BACKLOG.md`.
- Completely overhauled `README.md` to reflect the current multi-service architecture and setup process.
- Verified all 150+ tests across all modules.

## 2026-01-09 — Application-Level Encryption (ALE) Policy

**Summary**

- Added ADR-018: Application-Level Encryption (ALE) for Sensitive Data.
- Defined the use of AES-256-GCM and Google Tink for protecting PII (account numbers, tax IDs, etc.).
- Established the key management strategy (file-based keys for local dev, KMS for Production), forbidding the use of plaintext environment variables for keys.
- Updated the architecture decision index and the project backlog.

**Impacts**

- **Security**: Ensures multi-tenant isolation at the data level, complying with GDPR and local regulations.
- **Development**: Requires implementation of encryption/decryption layers in the upcoming Account and Transaction services.
- **Performance**: Introduces minor CPU overhead for cryptographic operations.

**Actions**

- Created `docs/architecture/decisions/ADR-018-application-level-encryption.md`.
- Modified `.junie/guidelines.md`.
- Modified `docs/architecture/decisions/index.md`.
- Updated `docs/backlog/iteration-3.json`.
- Re-rendered `BACKLOG.md`.

## 2026-01-08 — CI/CD Security Gates & Reporting

**Summary**

- Automated a dedicated "Security Audit" step in the CI/CD pipeline to explicitly run security-focused tests (JWT, RBAC, Tenant Isolation).
- Enhanced test coverage reporting by enabling HTML/XML output and highlighting in `sbt-scoverage`.
- Configured CI to archive and upload full coverage reports as artifacts for traceability and audit.
- Enforced a 90% total statement coverage gate, ensuring authorization logic is rigorously tested.

**Impacts**

- **Governance**: Provides tangible evidence of security testing for every PR.
- **Reliability**: Prevents regressions in authorization logic by making security tests a first-class citizen in CI.
- **Observability**: Detailed coverage reports allow identifying "blind spots" in security-critical code.

**Actions**

- Modified `.github/workflows/ci.yml`.
- Modified `build.sbt`.
- Updated `docs/backlog/iteration-2.json`.
- Re-rendered `BACKLOG.md`.

## 2026-01-08 — Update Docker Compose to 'Expat Stack' v2

**Summary**

- Synchronized `docker-compose.yml` with Iteration 2 requirements.
- Added infrastructure services: **PostgreSQL 16** (with healthcheck and persistence) and **RabbitMQ 3.12** (with management plugin).
- Included placeholders for **FX Service** and **Account Service**.
- Configured **JWT** environment variables (`JWT_PUBLIC_KEY`, `JWT_ISSUER`, `JWT_AUDIENCE`) in the API Gateway.
  - _Superseded 2026-08-06 (issue #87): `JWT_PUBLIC_KEY` was never read by any configuration class and was removed, along with the local token-signing tooling that appeared to depend on it. `JWT_ISSUER` and `JWT_AUDIENCE` remain, joined by `JWT_JWKS_URL`, and are now Auth0-shaped. The statement above records what this change did on 2026-01-08 and is left as written._
- Improved service orchestration with `depends_on` healthcheck conditions.

**Impacts**

- **Environment**: Enables local development and testing of the full system stack.
- **Reliability**: Ensures services start only after their infrastructure dependencies are healthy.

**Actions**

- Modified `docker-compose.yml`.
- Updated `docs/backlog/iteration-2.json`.
- Re-rendered `BACKLOG.md`.

## 2026-01-08 — Thread-safe EventType Serialization Registry

**Summary**

- Refactored `EventType` in `shared-kernel` to use `java.util.concurrent.ConcurrentHashMap` for storing serializers.
- Added `clearSerializers()` method to `EventType` for testing purposes.
- Updated `RabbitMQPublisherSpec` to use `beforeEach` fixture to reset the `EventType` state, ensuring test isolation and preventing flakiness.

**Impacts**

- **Stability**: Eliminates potential race conditions and flaky tests caused by shared mutable state in `EventType`.
- **Maintainability**: Clearer testing patterns for polymorphic event serialization.

**Actions**

- Modified `modules/shared-kernel/src/main/scala/com/expatledger/kernel/domain/events/EventType.scala`.
- Modified `modules/tenant-service/src/test/scala/com/expatledger/tenants/infrastructure/messaging/RabbitMQPublisherSpec.scala`.
- Updated `docs/backlog/iteration-2.json`.
- Re-rendered `BACKLOG.md`.

## 2026-01-08 — Enforced ISO 3166-1 alpha-2 Validation in OpenAPI

**Summary**

- Added regex pattern `^[A-Z]{2}$` to `taxResidencies` items in the OpenAPI v1 specification.
- Ensured that only two-letter uppercase country codes are accepted at the API level.

**Impacts**

- **Data Quality**: Improves validation of incoming requests by enforcing international standards for country codes.
- **Consistency**: Aligns the API contract with business requirements for tax residency reporting.

**Actions**

- Modified `docs/contracts/openapi/v1/openapi.yaml`.
- Updated `docs/contracts/openapi/v1/CHANGELOG.md`.
- Updated `docs/backlog/iteration-2.json`.

## 2026-01-08 — Synchronized Tax Residencies across API and Backend

**Summary**

- Updated the `TenantService` gRPC contract to support multiple tax residencies.
- Migrated `initial_tax_residency` (string) to `tax_residencies` (repeated string) in `tenant.proto`.
- Refactored `TenantServiceLive` and `OnboardTenantRequest` to process a list of tax residencies.
- Aligned the backend implementation with the OpenAPI v1 specification.

**Impacts**

- **Consistency**: Eliminated the mismatch between the public OpenAPI contract and the internal gRPC/Backend implementation.
- **Flexibility**: Allows onboarding tenants with multiple initial tax residencies.

**Actions**

- Modified `modules/shared-kernel/src/main/protobuf/tenant.proto`.
- Modified `modules/tenant-service/src/main/scala/com/expatledger/tenants/application/OnboardTenantRequest.scala`.
- Modified `modules/tenant-service/src/main/scala/com/expatledger/tenants/application/TenantServiceLive.scala`.
- Modified `modules/tenant-service/src/main/scala/com/expatledger/tenants/infrastructure/api/grpc/TenantGrpcAdapter.scala`.
- Updated `modules/tenant-service/src/test/scala/com/expatledger/tenants/infrastructure/api/grpc/TenantGrpcAdapterSpec.scala`.
- Updated `modules/tenant-service/src/test/scala/com/expatledger/tenants/application/TenantServiceSpec.scala`.
- Updated `docs/backlog/iteration-2.json`.

## 2026-01-07 — RBAC & ACL Framework Implementation

**Summary**

- Implemented a standard **Role-Based Access Control (RBAC)** framework.
- Defined granular `Permission` enum (e.g., `ViewTenant`, `ManageMembers`, `CreateTransaction`) in `shared-kernel`.
- Created `Authorizer[F]` trait and `TenantAuthorizer` implementation for centralized authorization checks.
- Added `CachedTenantAuthorizer` using Scaffeine for optimized permission lookups (P95 latency target < 200ms).
- Integrated authorization checks in `TenantService` to enforce tenant isolation.

**Impacts**

- **Security**: Achieved fine-grained access control, ensuring users only perform authorized actions within their tenants.
- **Performance**: High-speed authorization checks via Scaffeine-based caching.
- **Maintainability**: Consistent authorization pattern across all services.

**Actions**

- Created `modules/shared-kernel/src/main/scala/com/expatledger/kernel/domain/auth/Permission.scala`.
- Created `modules/shared-kernel/src/main/scala/com/expatledger/kernel/domain/auth/Authorizer.scala`.
- Created `modules/tenant-service/src/main/scala/com/expatledger/tenants/application/TenantAuthorizer.scala`.
- Created `modules/tenant-service/src/main/scala/com/expatledger/tenants/application/CachedTenantAuthorizer.scala`.
- Modified `modules/tenant-service/src/main/scala/com/expatledger/tenants/application/TenantServiceLive.scala`.
- Updated `docs/architecture/decisions/ADR-016-rbac-acl-framework.md`.
- Updated `docs/architecture/decisions/ADR-017-tenant-authorization-caching.md`.
- Updated `docs/backlog/iteration-2.json` (Tasks T2.7, T2.8).

## 2026-01-07 — Separated User/Tenant Concerns & Enforced One-Owner Rule

**Summary**

- Split `TenantService` into `TenantService` and `UserService` to separate administrative concerns.
- Enforced that a user can be the `Owner` of at most one tenant using a partial unique index in PostgreSQL.
- Updated `onboardTenant` to automatically assign the creator as the `Owner` within the same transaction.
- Added application-level validation to provide meaningful error messages for "one owner" rule violations.

**Impacts**

- **Security**: Prevented users from claiming ownership of multiple tenants, aligning with business rules.
- **Maintainability**: Cleaner code structure by separating user and tenant management logic.
- **Atomic Operations**: Guaranteed that every new tenant has an owner assigned immediately upon creation.

**Actions**

- Created `modules/tenant-service/src/main/resources/db/migration/V4__Enforce_Single_Owner.sql`.
- Modified `modules/tenant-service/src/main/scala/com/expatledger/tenants/application/TenantService.scala`.
- Modified `modules/tenant-service/src/main/scala/com/expatledger/tenants/application/TenantServiceLive.scala`.
- Modified `modules/tenant-service/src/main/scala/com/expatledger/tenants/application/OnboardTenantRequest.scala`.
- Modified `modules/tenant-service/src/main/scala/com/expatledger/tenants/infrastructure/api/grpc/TenantGrpcAdapter.scala`.
- Modified `modules/tenant-service/src/main/scala/com/expatledger/tenants/Main.scala`.
- Updated `modules/tenant-service/src/test/scala/com/expatledger/tenants/application/TenantServiceSpec.scala`.
- Updated `modules/tenant-service/src/test/scala/com/expatledger/tenants/infrastructure/api/grpc/TenantGrpcAdapterSpec.scala`.
- Updated `modules/tenant-service/src/test/scala/com/expatledger/tenants/infrastructure/persistence/TenantRepositorySpec.scala`.
- Increased test coverage for `TenantServiceLive`, `TenantGrpcAdapter`, and `OutboxPoller` to >98% for application logic.
- Updated `docs/backlog/iteration-2.json` (Task T2.6).

## 2026-01-07 — FX Service: Refactor to Domain Errors

**Summary**

- Replaced `String`-based errors with a dedicated `FxError` ADT (Algebraic Data Type) in the `fx-service` module.
- Defined `FxError` with specific cases: `RateNotFound`, `ProviderFailure`, and `InvalidRate`.
- Updated `FxProvider` trait and its implementations (`MemoryFxProvider`, `CachedFxProvider`) to return `Either[FxError, FxRate]`.

**Impacts**

- **Maintainability**: Improved error handling by allowing pattern matching on specific error types instead of parsing strings.
- **Robustness**: Better structured error reporting throughout the FX service stack.

**Actions**

- Created `modules/fx-service/src/main/scala/com/expatledger/fx/domain/model/FxError.scala`.
- Modified `modules/fx-service/src/main/scala/com/expatledger/fx/domain/port/FxProvider.scala`.
- Modified `modules/fx-service/src/main/scala/com/expatledger/fx/infrastructure/provider/MemoryFxProvider.scala`.
- Modified `modules/fx-service/src/main/scala/com/expatledger/fx/infrastructure/provider/CachedFxProvider.scala`.
- Updated `modules/fx-service/src/test/scala/com/expatledger/fx/infrastructure/provider/MemoryFxProviderSpec.scala`.
- Updated `modules/fx-service/src/test/scala/com/expatledger/fx/infrastructure/provider/CachedFxProviderSpec.scala`.
- Updated `docs/backlog/iteration-2.json` (Task T2.13).

## 2026-01-05 — Configurable gRPC Transport Security

**Summary**

- Replaced hardcoded `.usePlaintext()` in `GrpcClientFactory` with configurable TLS support.
- Updated `GrpcServiceConfig` and `StaticServiceDiscovery` to handle `useTls` flag.
- Added environment variable `TENANT_SERVICE_USE_TLS` and `use-tls` configuration in `application.conf`.

**Impacts**

- **Security**: Allows enabling TLS for gRPC communication between services, mitigating cleartext data risks in production.
- **Flexibility**: Maintains support for plaintext communication for local development and non-production environments.

**Actions**

- Modified `modules/api-gateway/src/main/scala/com/expatledger/api/config/GrpcServiceConfig.scala` to add `useTls` field.
- Modified `modules/api-gateway/src/main/scala/com/expatledger/api/infrastructure/grpc/GrpcClientFactory.scala` to respect the `useTls` flag.
- Modified `modules/api-gateway/src/main/scala/com/expatledger/api/discovery/ServiceDiscovery.scala` to read `TENANT_SERVICE_USE_TLS`.
- Modified `modules/api-gateway/src/main/resources/application.conf` to add `use-tls` setting.
- Updated `modules/api-gateway/src/test/scala/com/expatledger/api/infrastructure/grpc/GrpcClientFactorySpec.scala` and `StaticServiceDiscoverySpec.scala`.
- Updated `docs/backlog/iteration-2.json` (Task T2.12).

## 2026-01-05 — Refactored gRPC Identity Propagation to use Context

**Summary**

- Centralized gRPC `UserId` extraction from `io.grpc.Context` in `MetadataUtils`.
- Refactored `TenantGrpcAdapter` to use the new `MetadataUtils.getUserIdFromContext` method, eliminating redundant metadata parsing.
- Improved `TenantGrpcAdapterSpec` to properly test context-bound requests using `IO.bracket` and `Context.attach/detach`.

**Impacts**

- **Performance**: Reduced overhead by avoiding repeated metadata extraction and parsing in the service layer.
- **Maintainability**: Unified identity handling logic; cleaner service implementation.
- **Reliability**: Ensured identity is validated early by the interceptor and correctly propagated through the context.

**Actions**

- Modified `modules/shared-kernel/src/main/scala/com/expatledger/kernel/infrastructure/grpc/MetadataUtils.scala` to add `getUserIdFromContext`.
- Modified `modules/tenant-service/src/main/scala/com/expatledger/tenants/infrastructure/api/grpc/TenantGrpcAdapter.scala` to use the new context-based extraction.
- Updated `modules/tenant-service/src/test/scala/com/expatledger/tenants/infrastructure/api/grpc/TenantGrpcAdapterSpec.scala` with context-aware tests.
- Updated `docs/backlog/iteration-2.json` (Task T2.2).

## 2026-01-05 — Fixed gRPC Identity Propagation Security Risk

**Summary**

- Refactored `IdentityInterceptor` to use `io.grpc.Context` for `UserId` propagation instead of `unsafeRunAndForget`.
- Eliminated security race conditions and stability risks from unhandled exceptions in asynchronous interceptor logic.
- Simplified `IdentityInterceptor.server` signature by removing the unused `logic` callback.

**Impacts**

- **Security**: Ensures `UserId` is available throughout the gRPC call lifecycle in a thread-safe manner.
- **Stability**: Prevents potential crashes in the global execution context by removing `unsafeRunAndForget`.
- **Maintainability**: Aligns with gRPC best practices for context propagation.

**Actions**

- Modified `modules/shared-kernel/src/main/scala/com/expatledger/kernel/infrastructure/grpc/IdentityMetadata.scala` to include `UserIdContextKey`.
- Modified `modules/shared-kernel/src/main/scala/com/expatledger/kernel/infrastructure/grpc/IdentityInterceptor.scala` to use `Contexts.interceptCall`.
- Modified `modules/tenant-service/src/main/scala/com/expatledger/tenants/Main.scala` to adapt to the new interceptor signature.
- Modified `modules/shared-kernel/src/test/scala/com/expatledger/kernel/infrastructure/grpc/IdentityInterceptorSpec.scala` to verify context propagation and remove unused dependencies.
- Updated `docs/backlog/iteration-2.json` (Task T2.2).

## 2026-01-04 — Optimized Outbox Serialization with Polymorphism

**Summary**

- Implemented polymorphic event serialization to improve efficiency and maintainability in `RabbitMQPublisher`.
- Added `avro_payload` persistence in the `outbox` table to avoid redundant JSON-to-Avro re-serialization for events loaded from the database.
- Introduced a registry-based polymorphic serialization mechanism using an `EventSerializer` trait and `EventType` enum.
- Removed hardcoded pattern matching on event types in the messaging infrastructure.

**Impacts**

- **Performance**: Reduced CPU usage and latency during event publishing by eliminating redundant JSON decoding and Avro re-serialization.
- **Maintainability**: New event types can now be added by implementing an `EventSerializer` and registering it, without modifying the shared messaging logic.
- **Type Safety**: Serialization logic is now decoupled from the generic `OutboxEvent` structure.

**Actions**

- Created `modules/shared-kernel/src/main/scala/com/expatledger/kernel/domain/events/EventSerializer.scala`.
- Created `modules/tenant-service/src/main/scala/com/expatledger/tenants/domain/events/TenantCreatedSerializer.scala`.
- Created `modules/tenant-service/src/test/scala/com/expatledger/tenants/infrastructure/messaging/RabbitMQPublisherTest.scala`.
- Modified `modules/shared-kernel/src/main/scala/com/expatledger/kernel/domain/events/EventType.scala` to support serializer registration.
- Modified `modules/tenant-service/src/main/scala/com/expatledger/tenants/infrastructure/persistence/OutboxRepositoryLive.scala` to persist `avroPayload`.
- Modified `modules/tenant-service/src/main/scala/com/expatledger/tenants/infrastructure/messaging/RabbitMQPublisher.scala` to use polymorphic serialization.
- Modified `modules/tenant-service/src/main/scala/com/expatledger/tenants/Main.scala` to register serializers at startup.

## 2026-01-04 — Adopted Manual Dependency Injection

**Summary**

- Discarded Google Guice in favor of **Manual Dependency Injection** orchestrated through a "Resource Tree".
- Removed `guice` and `jakarta.inject` dependencies.
- Refactored `TenantServiceLive` and `TenantGrpcAdapter` to use plain constructor injection without annotations.
- Updated `Main.scala` to perform explicit component wiring within the `cats.effect.Resource` lifecycle.

**Impacts**

- **Type Safety**: 100% compile-time safety for dependency wiring.
- **Resource Management**: Guaranteed cleanup of database pools and other resources.
- **Maintainability**: Improved transparency of the dependency graph; removed reflection-based "magic".

**Actions**

- Created `docs/architecture/decisions/ADR-015-manual-dependency-injection.md`.
- Updated `docs/architecture/decisions/ADR-014-google-guice-standardization.md` (marked as superseded).
- Modified `project/Dependencies.scala` to remove Guice.
- Refactored `Main.scala`, `TenantServiceLive.scala`, and `TenantGrpcAdapter.scala` in `tenant-service`.
- Deleted `TenantModule.scala`.
- Updated `docs/backlog/iteration-1.json` (T1.25 marked as done).

## 2026-01-04 — Improved AvroSchemaLoader Error Handling

**Summary**

- Replaced generic `RuntimeException` with `java.io.FileNotFoundException` when an Avro schema file is missing in the classpath.
- Added unit tests for `AvroSchemaLoader`.

**Impacts**

- **Maintainability**: Better error context for debugging missing schema files.
- **Robustness**: Added test coverage for infrastructure messaging components.

**Actions**

- Modified `modules/shared-kernel/src/main/scala/com/expatledger/kernel/infrastructure/messaging/AvroSchemaLoader.scala`.
- Created `modules/shared-kernel/src/test/scala/com/expatledger/kernel/infrastructure/messaging/AvroSchemaLoaderSpec.scala`.
- Updated `docs/backlog/iteration-1.json` (TASK-15 marked as completed).

## 2026-01-04 — Improved OutboxPoller retry implementation

**Summary**

- Refactored the recursive `retry` implementation in `OutboxPoller` to use a tail-recursive helper.
- Improved clarity and ensured idiomatic usage of Cats Effect's `Async[F].sleep` and `flatMap`.

**Impacts**

- **Maintainability**: Clearer retry logic in the outbox polling mechanism.
- **Reliability**: Ensured stack-safe and idiomatic retry behavior.

**Actions**

- Modified `modules/tenant-service/src/main/scala/com/expatledger/tenants/application/OutboxPoller.scala`.
- Updated `docs/backlog/iteration-1.json` with TASK-18.

## 2026-01-04 — Refactored EventType to use Enumeratum

**Summary**

- Replaced hardcoded string-based `eventType` with an `enumeratum` enum `EventType`.
- Improved type safety in `OutboxEvent` and `DomainEvent`.
- Updated `RabbitMQPublisher` to use exhaustive pattern matching on `EventType`.
- Implemented a Skunk codec for `EventType` to handle database persistence.

**Impacts**

- **Type Safety**: Reduced risk of runtime errors due to typoed event names.
- **Maintainability**: Centralized event type definitions in `EventType` enum.
- **Interoperability**: Maintained string-based representation for external messaging (CloudEvents) while using rich types internally.

**Actions**

- Added `enumeratum` and `enumeratum-circe` to `project/Dependencies.scala`.
- Created `modules/shared-kernel/src/main/scala/com/expatledger/kernel/domain/events/EventType.scala`.
- Updated `DomainEvent` and `OutboxEvent` in `shared-kernel`.
- Updated `RabbitMQPublisher`, `OutboxRepositoryLive`, and `TenantCreated` in `tenant-service`.
- Fixed missing test dependencies in `apiGatewayDependencies` and `tenantServiceDependencies`.

## 2026-01-03 — Outbox Poller Enhanced (Error Handling & Logging)

**Summary**

- Refactored `OutboxPoller` to ensure stack safety by replacing recursive restarts with fs2's `.repeat`.
- Integrated `log4cats` with `slf4j` and `logback` for structured logging across the project.
- Implemented exponential backoff retries for outbox event publishing.

**Impacts**

- **Reliability**: Improved poller stability for long-running processes; reduced risk of `StackOverflowError`.
- **Observability**: Structured JSON-ready logging enabled.
- **Resilience**: Added retries for transient messaging failures.

**Actions**

- Updated `project/Dependencies.scala` with `log4cats` and `logback`.
- Refactored `modules/tenant-service/src/main/scala/com/expatledger/tenants/application/OutboxPoller.scala`.
- Created `modules/tenant-service/src/test/scala/com/expatledger/tenants/application/OutboxPollerTest.scala`.
- Updated `docs/backlog/iteration-1.json` (T1.22 marked as done).

## 2026-01-03 — Pre-commit Hook Standardized

**Summary**

- Standardized pre-commit hook execution to use `python -m pre_commit` to support `asdf` environments.
- Removed obsolete `google-java-format` hook (project is Scala-only).
- Updated `README.md` and `Makefile` to reflect standardized setup.

**Impacts**

- **Developer Experience**: Improved first-time environment setup reliability.
- **Repository Hygiene**: Removed unused formatting scripts and configurations.

**Actions**

- Updated `.pre-commit-config.yaml` (removed `google-java-format`).
- Updated `Makefile` (standardized `lint` and `format` targets).
- Updated `README.md` (updated prerequisites and setup instructions).
- Updated `docs/backlog/iteration-1.json` with task T1.23.

## 2026-01-02 — Guidelines Consolidation

**Summary**

- Consolidated `.junierules` and `docs/governance/AGENTS.md` into `.junie/guidelines.md`.
- Established a single source of truth for Junie's operational rules and agent guidelines.

**Impacts**

- **Documentation**: `.junie/guidelines.md` is now the primary reference for agents.
- **Repository Hygiene**: Removed redundant `.junierules` and `AGENTS.md`.

**Actions**

- Removed `.junierules`.
- Removed `docs/governance/AGENTS.md`.
- Updated `mkdocs.yml` and `README.md` to point to `.junie/guidelines.md`.

## 2026-01-02 — Build Tool Pivot: sbt adoption

**Summary**

- Replaced **Gradle** with **sbt** as the primary build tool for the Scala 3 project.
- Aligned with Scala ecosystem standards and user preference.

**Impacts**

- **Build**: sbt (Scala Build Tool) used for compilation, testing, and formatting.
- **Documentation**: README, AGENTS.md, and .junierules updated to reflect sbt usage.
- **Backlog**: Tasks updated to reflect sbt setup.

**Actions**

- ADR-010 created: Use sbt as the Build Tool.
- `README.md` and `docs/governance/AGENTS.md` updated.
- `.junierules` updated to enforce sbt.
- `docs/backlog/iteration-0.json` updated with sbt tasks.

## 2026-01-02 — Scala-Native Pivot & Name Correction

**Summary**

- Corrected project name to **The Expat Ledger**.
- Pivot to **Scala-native frameworks** (discarding Spring Boot) to avoid interoperability friction.
- Adopted Typelevel/ZIO stacks for service implementation.

**Impacts**

- **Language**: Pure Scala 3 with functional effect systems (Cats Effect/ZIO).
- **Architecture**: Distributed Modular Monolith using Scala-native libraries for Gateway and Discovery.
- **Documentation**: Updated README, ADRs, and .junierules to reflect pure Scala stack.
- **Tech Stack**: Scala 3, Cats Effect, Http4s, Doobie/Skunk, fs2-grpc.

**Actions**

- ADR-009 updated: Transition to Scala 3 and Native Frameworks.
- `docs/architecture/scala-frameworks.md` updated with pure Scala recommendations.
- `README.md` and `.junierules` updated (removed NomadLedger and Spring Boot).

## 2026-01-02 — NomadLedger Pivot & Scala 3 Transition (Superseded)

## 2025-09-29 — Bank attribution + multi-currency balances

**Summary**

- Add bank identifier on every transaction (FR-10).
- Maintain running balances in EUR and COP (FR-11).

**Impacts**

- Contracts: +`bankId` in Transaction resource (backward-compatible).
- Data: new `bank` table and `bank_id` FK in `transaction`.
- Security/Privacy: no new PII; ensure bank names are tenant-scoped.
- Operations: FX cache must cover USD/EUR/COP by date.

**Actions**

- ADR-005 created to justify schema & projection approach.
- Migrations added (e.g., `V5__bank_and_tx_fk.sql`).
- OpenAPI updated: `/v1/transactions` includes `bankId`.

## 2025-09-29 — Hosting on Render (Free tier) + UX design workflow (Stitch + Figma)

**Summary**

- Decide to deploy API (Docker) and Web (Next.js SSR) on **Render Free** for public demos.
- Establish **Stitch → Figma** pipeline for UI generation + storyboard.

**Impacts**

- **Ops**: Free Postgres has ~1 GB and **expires ~30 days** → add seed/export scripts; non-prod only.
- **SLOs**: Free web services may idle; exclude **first-hit-after-idle** from latency SLO, track separately.
- **Security**: Keep secrets in Render dashboard; no prod data.
- **Docs**: Add `render.yaml`, ADR-007, and `docs/ops/deployment-render.md`; add `docs/ux/stitch-prompt.md` with the prompt.

**Actions**

- ADR-007 accepted (Render hosting decision & mitigations).
- Added `render.yaml` blueprint at repo root.
- Updated `docs/governance/SLOs-SLIs.md` with cold-start note and metric.
- Created `docs/ops/deployment-render.md` and `docs/ux/stitch-prompt.md`.

## 2026-01-15 — Infrastructure: Vault Integration Refactor (vault4s)

**Summary**

- Replaced custom Vault implementation with `vault4s` library.
- Hardened `VaultAdapter` with circuit breaking and automated health sentinel.
  **Impacts**
- **Security**: Aligns with ADR-020, using established `vault4s` for all Vault communications.
- **Resilience**: Improved health monitoring and circuit breaking for secret management.
  **Actions**
- Refactored `VaultAdapter` to use `com.banno.vault4s`.
- Implemented `VaultHealthSentinel` for background health monitoring.
- Updated `docs/backlog/iteration-3.json` (T3.32).

## 2026-01-15 — Vault Integration Hardening & AppRole Support

**Summary**

- Refactored `VaultAdapter` to support secure AppRole authentication (role_id/secret_id).
- Integrated `vault4s` `VaultClient.loginAndKeep` logic for automated token lifecycle management, optimized to share a single login for both Transit and managed client operations.
- Fixed security regression where empty tokens were sent to Vault when unconfigured.
- Simplified adapter architecture by removing the health sentinel in favor of standard library patterns and consolidated login logic.
- Ensured fail-fast behavior with `VaultNotAuthenticated` errors.

**Impacts**

- **Security**: Eliminated static token requirement; implemented secure service-to-service authentication via AppRole.
- **Resilience**: Automated token renewal prevents outages due to expired credentials.

**Actions**

- Modified `modules/shared-kernel/src/main/scala/com/expatledger/kernel/infrastructure/secrets/VaultAdapter.scala`.
- Updated `modules/shared-kernel/src/test/scala/com/expatledger/kernel/infrastructure/secrets/VaultAdapterSpec.scala`.
- Removed `modules/shared-kernel/src/main/scala/com/expatledger/kernel/infrastructure/secrets/VaultHealthSentinel.scala`.
- Updated `docs/backlog/iteration-3.json`.
- Re-rendered `BACKLOG.md`.

## 2026-01-15 — Infrastructure: Vault Coverage Recovery

**Summary**

- Recovered test coverage for `shared-kernel` module from 81.74% to 92.69%, exceeding the 90.00% requirement.
- Expanded `VaultAdapterSpec.scala` to cover multiple authentication methods (GitHub, Kubernetes, UserPass).
- Hardened token renewal logic tests, including background renewal fibers and non-renewable token scenarios.
- Covered `VaultAdapterError` and `VaultConfig` edge cases (e.g., URI validation).
- Refactored `VaultAdapter` to make `tokenLeaseExtension` configurable.

**Impacts**

- **Quality**: Ensures that the critical secret management infrastructure is fully verified across all branches.
- **Reliability**: Verified authentication and renewal flows reduce the risk of runtime secret-access failures.

**Actions**

- Modified `modules/shared-kernel/src/main/scala/com/expatledger/kernel/infrastructure/secrets/VaultAdapter.scala`.
- Modified `modules/shared-kernel/src/main/scala/com/expatledger/kernel/infrastructure/secrets/config/VaultConfig.scala`.
- Modified `modules/shared-kernel/src/test/scala/com/expatledger/kernel/infrastructure/secrets/VaultAdapterSpec.scala`.
- Hardened token renewal loop in `VaultAdapter` by using floating-point arithmetic and extracting `RenewalFactor` constant.
- Updated `docs/backlog/iteration-3.json`.
- Re-rendered `BACKLOG.md`.

## 2026-01-15 — Infrastructure: Configurable Vault Consistency

**Summary**

- Made `ConsistencyConfig` parameters (retry delay and max retries) configurable in `VaultConfig`.
- Updated `VaultAdapter` to use these environment-specific settings for eventual consistency handling.

**Impacts**

- **Resilience**: Allows tuning Vault retry behavior for different environments (e.g., faster retries for local dev, more conservative for production).

**Actions**

- Modified `modules/shared-kernel/src/main/scala/com/expatledger/kernel/infrastructure/secrets/config/VaultConfig.scala`.
- Modified `modules/shared-kernel/src/main/scala/com/expatledger/kernel/infrastructure/secrets/VaultAdapter.scala`.
- Updated `modules/shared-kernel/src/test/scala/com/expatledger/kernel/infrastructure/secrets/VaultAdapterSpec.scala`.
- Updated `docs/backlog/iteration-3.json`.
- Re-rendered `BACKLOG.md`.

## 2026-01-15 — Infrastructure: Automated AppRole Bootstrapping & Documentation

**Summary**

- Enhanced local development infrastructure with automated secure AppRole bootstrapping.
- Updated project documentation to reflect the new centralized secret management architecture.

**Impacts**

- **Security**: Ensures local development parity with production security patterns (AppRole vs static tokens).
- **Onboarding**: Simplified setup for new developers by automating credential generation and providing clear documentation.

**Actions**

- Updated `infra/vault/init-vault.sh` to generate and export AppRole credentials to `.vault.env`.
- Modified `docker-compose.security.yml` and `docker-compose.yml` to support credential sharing and injection.
- Updated `application.conf` for backend services to load Vault settings from environment variables.
- Overhauled `README.md` with current security stack initialization and local environment setup instructions.
- Updated `docs/backlog/iteration-3.json` (T3.33, T3.34).
- Re-rendered `BACKLOG.md`.

## 2026-01-15 — Infrastructure: Automated AppRole Bootstrapping

**Summary**

- Enhanced Vault initialization scripts to support automated AppRole credential generation for local development.
- Implemented automatic export of `role_id` and `secret_id` to a `.vault.env` file in the project root.
- Configured `docker-compose.yml` and `application.conf` across services to consume these credentials automatically.

**Impacts**

- **Developer Experience**: Eliminates the need for manual Vault configuration or static token management during local development.
- **Security**: Ensures that local development mirrors production-like AppRole authentication patterns.
- **Resilience**: Automates the linkage between Vault infrastructure and backend services.

**Actions**

- Modified `infra/vault/init-vault.sh` to generate and export AppRole credentials.
- Updated `docker-compose.security.yml` to mount the project root for credential persistence.
- Updated `docker-compose.yml` to use `env_file` and configured Vault environment variables for `tenant-service` and `account-service`.
- Updated `application.conf` in `tenant-service` and `account-service` to map Vault environment variables.
- Updated `docs/backlog/iteration-3.json` (T3.33).
- Re-rendered `BACKLOG.md`.

## 2026-01-15 — Operational Rule: Fail-Fast for Assistance

**Summary**

- Established a new operational rule for AI agents to ask for assistance immediately if stuck on library usage or complex technical blockers.
  **Impacts**
- **Efficiency**: Reduces time wasted on trial-and-error when library documentation or API surface is unclear.
- **Collaboration**: Ensures human-in-the-loop intervention for complex technical decisions.
  **Actions**
- Updated `.junie/guidelines.md` with the "Fail-Fast for Assistance" rule.

## 2026-01-15 — Documentation: Data Encryption Beginner's Guide

**Summary**

- Created a comprehensive guide for beginners on data encryption concepts (Rotation, Rewrapping, and Transit Operations) in the context of HashiCorp Vault.
- Linked the new guide in the main `README.md` to improve discoverability for new developers.
- Postponed the full implementation of the `RewrapWorker` and ALE key rotation to a future task to ensure project stability.

**Impacts**

- **Knowledge Management**: Centralizes critical cryptographic knowledge and provides clear definitions for core security operations.
- **Onboarding**: Facilitates faster onboarding for new team members by providing high-level conceptual explanations of the ALE infrastructure.
- **Maintenance**: Stabilized the codebase by removing partially implemented features causing compilation errors.

**Actions**

- Created `docs/architecture/security-encryption-guide.md`.
- Modified `README.md`.
- Updated `docs/backlog/iteration-4.json` (T4.8).
- Reverted `RewrapWorker` and postponed T4.4.
- Re-rendered `BACKLOG.md`.

## 2026-02-12 — Refactor: Consolidated SecretManager and CryptoService Traits

**Summary**

- Consolidated `SecretManager` and `CryptoService[IO]` to reduce code duplication and simplify the security architecture.
- Made `SecretManager` extend `CryptoService[IO]`, aligning parameter names across both traits (`plaintext`, `ciphertext`).
- Removed the redundant `VaultCryptoService` adapter.

**Impacts**

- **Maintainability**: Reduced architectural complexity by eliminating a redundant adapter class.
- **Consistency**: Standardized parameter naming for cryptographic operations across the codebase.
- **Code Quality**: Improved type safety by explicitly linking the ALE port (`SecretManager`) to the generic cryptographic service interface.

**Actions**

- Modified `modules/shared-kernel/src/main/scala/com/expatledger/kernel/domain/secrets/SecretManager.scala`.
- Modified `modules/shared-kernel/src/main/scala/com/expatledger/kernel/infrastructure/secrets/VaultAdapter.scala`.
- Removed `modules/shared-kernel/src/main/scala/com/expatledger/kernel/infrastructure/secrets/VaultCryptoService.scala`.
- Updated `BACKLOG.md` (via `scripts/backlog_render.py`).

## 2026-01-15 — Infrastructure: Maintenance Worker Dependency Isolation

**Summary**

- Decoupled `maintenance-worker` dependencies from the `shared-kernel` module.
- Defined a dedicated `maintenanceWorkerDependencies` set in `project/Dependencies.scala`.
- Optimized the dependency footprint for the maintenance tool, focusing on `decline`, `http4s-client`, and `logging`.
- Replaced the high-privilege administrative token placeholder with a dedicated, automatically generated "maintenance" token for local development.

**Impacts**

- **Maintainability**: Clearer separation of concerns between runtime services and administrative tooling.
- **Security**: Reduced attack surface for the high-privilege maintenance module by limiting its dependencies.

**Actions**

- Modified `project/Dependencies.scala`.
- Modified `build.sbt`.

## 2026-01-15 — Infrastructure: High-Privilege Maintenance Token Generation

**Summary**

- Enhanced the Vault bootstrapping process to generate a dedicated high-privilege "maintenance" token for development.
- Configured `infra/vault/init-vault.sh` to create a `maintenance` policy and export the resulting token to `.vault.env`.
- Implemented a standard `Main` entry point for the `maintenance-worker` module to consume the `VAULT_MAINTENANCE_TOKEN` environment variable.
- Updated documentation with instructions on running maintenance tasks locally.

**Impacts**

- **Developer Experience**: Provides a seamless way to test and execute maintenance tasks (like key rotation) in local development.
- **Security**: Demonstrates the use of restricted, task-specific policies (`maintenance` policy) even for administrative tools.
- **Traceability**: Aligns with the strategic goal of isolating high-privilege operations within the `maintenance-worker` module.

**Actions**

- Modified `infra/vault/init-vault.sh` to automate maintenance token generation and export.
- Created `modules/maintenance-worker/src/main/scala/com/expatledger/maintenance/Main.scala`.
- Updated `README.md` with usage instructions for the maintenance worker.
- Updated `docs/backlog/iteration-4.json`.
- Re-rendered `BACKLOG.md`.

## 2026-01-15 — Operational Rule: Request Clarification Over Scanning

**Summary**

- Added a rule to prioritize asking the user for clarification when information is missing or instructions are imprecise, rather than performing extensive repository scans.

- **Impacts**

- **Efficiency**: Reduces token usage and time spent on manual context gathering when the user can provide direct answers.

- **Actions**

- Updated `.junie/guidelines.md` with the "Request Clarification Over Scanning" rule.
