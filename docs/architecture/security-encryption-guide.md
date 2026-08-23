# Data Encryption Guide: Tink Keysets, KMS Master Keys, and Rotation

> **Status: in force as of 2026-08-08.** This guide describes the encryption posture that is wired and running, decided in [ADR-026](/reference/backend/decisions/ADR-026-secret-management-proportionality.md) (Accepted 2026-08-06) and delivered by [issue #88](https://github.com/alexandervivas/expat-ledger-backend/issues/88). It replaces the previous HashiCorp Vault Transit guide in full: **Vault no longer exists anywhere in this repository** — no code, configuration, infrastructure, compose service, or dependency.

Application-Level Encryption (ALE) in **The Expat Ledger** protects sensitive fields before they reach PostgreSQL. It uses **Google Tink** primitives in-process, with the Tink keysets themselves encrypted ("wrapped") by **AWS KMS customer managed keys**. There is no encryption-as-a-service round trip per field.

---

## 1. The two layers, and why the distinction matters

Every rotation, recovery, and failure question in this document reduces to which of these two layers you are talking about. Conflating them is the single most expensive mistake available here.

| Layer                               | What it is                                                   | Where the key material lives                                                       | Who uses it                                      |
| :---------------------------------- | :----------------------------------------------------------- | :--------------------------------------------------------------------------------- | :----------------------------------------------- |
| **KMS master key** (key-encryption) | An AWS KMS customer managed key, addressed by **alias ARN**  | Inside AWS KMS, HSM-backed, never leaves it                                        | Tink, once per process start, to unwrap a keyset |
| **Tink keyset** (data-encryption)   | A JSON keyset holding the AES keys that encrypt field values | At rest: encrypted, in `infra/keysets/` locally. At runtime: **in process memory** | The services, on every field encrypt/decrypt     |

The keyset at rest contains only `encryptedKeyset` and `keysetInfo` — no cleartext key material — whenever a master key URI is configured. That keysets are decrypted into process memory is the deliberate **ASVS 13.3.3 deferral** recorded in ADR-026 §1, not an oversight: satisfying 13.3.3 would mean a provider round trip per encrypted field per row, against the NFR-001 P95 < 200 ms budget. The revisit condition is a _measurement_ with real users, not a re-argument.

---

## 2. Primitives and encrypted fields

Two keysets, two primitives, one associated-data rule.

| Primitive                 | Algorithm   | Keyset                             | Used for                                                                 |
| :------------------------ | :---------- | :--------------------------------- | :----------------------------------------------------------------------- |
| **AEAD** (randomized)     | AES-256-GCM | `CRYPTO_KEYSET_PATH`               | `accounts.routing_details`, `accounts.owner_full_name`, `tenants.tax_id` |
| **DAEAD** (deterministic) | AES-256-SIV | `CRYPTO_DETERMINISTIC_KEYSET_PATH` | `accounts.account_number`                                                |

**`tenant_id` is bound as associated data on every operation**, deterministic and randomized alike. Ciphertext written for one tenant therefore cannot be decrypted under another tenant's context, and the same account number under two tenants does not produce colliding deterministic ciphertext.

`transaction-service` performs no application-level encryption and loads no keyset. Its startup path is the same ordering minus the keyset step, deliberately rather than by loading a keyset it does not need.

---

## 3. ⚠ Rotation: the trap you must not walk into

**Rotating the KMS master key is harmless. Rotating the Tink DAEAD primary key is not.** These are different operations with different consequences, and ADR-026 §3 records the distinction as a genuine tension in the design.

### Rotating the **KMS master key** — safe, and expected

A master key rotation (automatic or manual) produces a new key version behind the same alias. The keyset is re-wrapped; **the field ciphertext in the database is untouched**, because the master key never encrypted a field value — it only encrypted the keyset. Nothing needs to be rewritten, no index breaks, and no downtime is implied. KMS retains previous versions so an existing wrapped keyset stays readable.

### Rotating the **Tink AEAD primary key** — safe

Adding a new primary key to the AEAD (AES-256-GCM) keyset changes what _new_ writes produce. Existing ciphertext stays decryptable because the retired key remains in the keyset. Nothing depends on GCM ciphertext being stable — it is randomized by construction, so two encryptions of the same plaintext already differ.

### Rotating the **Tink DAEAD primary key** — ⚠ **breaks deterministic equality**

AES-256-SIV is deterministic: identical plaintext under identical associated data yields identical ciphertext. That is the property that makes an index, a unique constraint, or an equality lookup on `account_number` possible at all. **Rotating the DAEAD primary key changes the ciphertext produced for the same plaintext**, so from the rotation boundary onward:

- a new write of an account number already stored produces a _different_ ciphertext than the stored row;
- equality comparison, a unique constraint, or an index lookup on the column silently stops matching across the boundary;
- decryption of old rows still works (the retired key stays in the keyset) — so the failure is a **silent correctness failure, not an error**.

The only correct fix is a **column-wide rewrap**: decrypt every stored value under the old primary and re-encrypt it under the new one. **No such rewrap path exists today.** This is exactly the trap the previous posture fell into — Vault Transit's convergent encryption had the same property and shipped a `rewrap` endpoint, and the maintenance CLI's `rewrap` was a no-op print statement that never implemented it.

### Therefore: the deterministic key is **not rotated today**

This is a deliberate, recorded position, not an omission. It is safe right now for one reason only: there is no persisted production ciphertext and no index or unique constraint on `accounts.account_number`, so there is no row whose equality could fail.

**ADR-026's trigger for building the rewrap path** ([follow-up obligations](/reference/backend/decisions/ADR-026-secret-management-proportionality.md#follow-up-obligations)): **before the first real user data is persisted, or before any index or unique constraint is added to `account_number`, whichever comes first.** At that point a working column-wide rewrap becomes a genuine prerequisite for the adopted ASVS 13.3.4 rotation commitment and the determinism capability to coexist, and the deterministic key's rotation schedule must be defined in terms of it.

### What the maintenance worker does and does not do

`maintenance-worker` has **no rotation command and no rewrap command**. Its Vault `rotate-vault`/`rotate-transit` branches and its `rewrap` stub were deleted with Vault. What it does own is `local-bootstrap` (see §5). Key rotation is a Tink keyset concern plus a KMS console/API concern; it is not automated in this repository, and pretending otherwise in tooling would be worse than the honest gap.

---

## 4. Runtime behavior: startup, fail-closed, and what "picked up" means

The wired `SecretManager` is `TinkSecretManager` (`modules/shared-kernel/.../infrastructure/secrets/TinkSecretManager.scala`), a thin adapter over `TinkCryptoService`. It writes no cryptography of its own.

**Startup ordering is a requirement, encoded once in `ServiceStartup`:**

1. acquire the **application** and **migration** database credentials;
2. load the secret manager — unwrap both keysets;
3. run Flyway migrations under the **migration** credential (the only one holding `CREATE`);
4. bind the port and serve under the DML-only **application** credential.

**Fail-closed, with no fallback.** If a master key cannot be resolved, or a keyset cannot be unwrapped, or a credential cannot be read, startup raises a typed error and neither migrations nor a bound port are reached. There is no runtime fallback from the KMS-wrapped path to a plaintext keyset, and none from the `aws` credential provider to `static`. An insecure fallback is prohibited, not merely undesirable.

**Selection is by presence, not by a switch.** The presence of `CRYPTO_MASTER_KEY_URI` is the _only_ discriminator between a KMS-wrapped keyset and a plaintext local-only one, so configuration cannot express a contradiction. `CRYPTO_DETERMINISTIC_MASTER_KEY_URI` names the second master key; when absent it falls back to `CRYPTO_MASTER_KEY_URI`, resolved in one place.

**Master keys are addressed by alias ARN**, e.g. `aws-kms://arn:aws:kms:us-east-1:<account>:alias/expat-ledger-aead`, never by key id. An emulator mints a fresh key id per container, so only an alias is stable enough to live in static configuration. The bootstrap _parses the alias out of the configured URI_ rather than composing it from a prefix declared in code, so a key name has exactly one spelling anywhere in the system.

**A rotated secret is picked up on restart, not in flight.** Database credentials are static per-environment secrets read once at startup; the lease/refresh loop that Vault required is gone, along with the credential-refresh failure race. Secrets Manager's native rotation with `AWSCURRENT`/`AWSPREVIOUS` and an alternating-user strategy makes restart-based pickup workable. A rotation poller is a recorded follow-up whose trigger is _before the first deployed environment runs unattended_.

---

## 5. Keyset material and provisioning

`infra/keysets/` holds **generated, git-ignored material only**. A plaintext Tink keyset is base64 AES-256 key material; committing one would violate the standing prohibition on committing key material and would be permanent in the history ADR-025's secret-scanning gate covers. Nothing under `infra/keysets/` is ever committed.

Provisioning is `maintenance-worker local-bootstrap` — non-interactive and idempotent. It ensures the two aliased KMS master keys exist, generates and writes both wrapped keysets, and seeds the database secrets, deriving every provisioned name from the same configuration classes the services read. Re-running it creates no duplicate key, alias, or secret and leaves existing keyset material untouched; it deliberately **refuses to overwrite a keyset it cannot read** rather than destroying decryptable data.

`--offline` writes plaintext local-only keysets alongside a `LOCAL-ONLY.txt` marker, makes no AWS calls, and seeds no secrets. That path exists because the LocalStack image requires a developer-supplied auth token; it is the documented route for a clean checkout without one. See the [README](https://github.com/alexandervivas/expat-ledger-backend#readme) for the two startup commands.

**LocalStack KMS ciphertext is not portable to AWS** — LocalStack uses an encrypted data format distinct from AWS's. Never attempt to move a locally wrapped keyset into a deployed environment.

---

## 6. Assurance target

The declared target is **OWASP ASVS 5.0.0 Level 2** (ADR-026 §1), amending the previously inherited and unjustified L3 claim.

- **Adopted above L2:** 13.3.4 and 13.1.4 (documented secret expiry and rotation schedule), and the **hardware-backed elevation of 13.3.1** — the KMS master key is HSM-resident and never leaves KMS. The derived Tink data-encryption keys are not HSM-resident.
- **Deferred with reason:** 13.3.3 (all cryptographic operations inside an isolated security module), on the NFR-001 P95 budget. Revisit by measurement with real users, or on a change in regulatory scope.
- **Recorded deviation:** 13.2.1 (L2) — static per-environment database credentials rather than short-lived per-service ones, accepted with a rotation schedule. RDS IAM database authentication is the named upgrade path.
- **Least privilege (13.3.2)** is applied at the database boundary today: migrations run as `expat_migrator` (holding `CREATE`), services connect as `expat_app` (DML only, denied `CREATE` on schema `public`). Per-service IAM roles with key-usage-only grants, key policies denying administrative actions to runtime roles, and CloudTrail retention for KMS `Decrypt` are a **named follow-up**, due _before the first real user data is persisted_.

---

## 7. Determinism: a capability preserved, not a behavior protected

Deterministic encryption of `account_number` is preserved, and nothing uses it. `accounts.account_number` is plain `TEXT NOT NULL` with **no index and no unique constraint**, and no code filters, joins, or deduplicates on it. The reconciliation and duplicate-detection use cases that originally justified determinism do not exist.

Two constraints bear on what a searchable capability would eventually need, both recorded in ADR-026 §3:

- Deterministic encryption permits frequency analysis. The mitigation is unchanged from ADR-017: high-entropy fields only, tenant-scoped associated data. An AWS KMS HMAC blind index (`GenerateMac`/`VerifyMac`, emulated by LocalStack on the free tier) is the recorded upgrade path.
- The delivered `statement-import-reconciliation-contracts` capability mandates that import provenance carry only a **masked** account reference — `****` plus the last four characters — and forbids persisting an unmasked one. Equality on full-value deterministic ciphertext cannot serve a suffix match. **So if reconciliation is the driver, a keyed blind index over a normalized suffix is the likelier mechanism than deterministic encryption of the whole value.** Deciding whether the deterministic capability is exercised at all is itself an ADR-026 follow-up, due _before building any index on `account_number`_.

---

## 8. Recovery

**Losing a KMS master key makes all ciphertext under it unrecoverable.** This is structurally the sharpest risk in the design and is no smaller than Vault's was. It is currently **accepted rather than mitigated**, because nothing is deployed and all local and test data is synthetic and disposable.

The mitigations — multi-Region keys, `ScheduleKeyDeletion`/`DisableKey` alarms, and a recorded restore rehearsal — are staged behind an explicit trigger: _before the first real user data is persisted_. Deletion protection and a long deletion waiting period are free and should be set at provisioning time.

**There is no in-force secret-recovery runbook.** `docs/ops/vault-recovery.md` is retained as a historical tabletop record and carries a not-in-force banner; the KMS-oriented replacement is a named ADR-026 follow-up and is **not yet written**.
