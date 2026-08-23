# Requirement FR-008: Data Encryption (ADR-026)

## Status

- **Type**: Functional Requirement (Security)
- **Priority**: High
- **Iteration**: 3
- **Status**: Implemented (posture decided in ADR-026, runtime delivered by [issue #88](https://github.com/alexandervivas/expat-ledger-backend/issues/88) on 2026-08-08)

> **Mechanism of record.** The encryption posture below is wired and running. `TinkSecretManager` is the only production `SecretManager`; HashiCorp Vault has been removed from every path in the repository — code, configuration, infrastructure, compose services, and dependencies. Where an obligation is deliberately deferred it is stated as deferred with its trigger, never as delivered. Operational detail lives in [`docs/architecture/security-encryption-guide.md`](../architecture/security-encryption-guide.md).

## Description

Sensitive financial data, specifically account numbers and Personally Identifiable Information (PII), must be protected using Application-Level Encryption (ALE). The runtime encryption model is Google Tink AEAD/DAEAD in-process, with keysets that are never plaintext at rest in a deployed environment — each is wrapped by an AWS KMS customer managed key, addressed by alias ARN, through Tink's KMS envelope integration, so raw master key material is never handled by application services.

## User Story

As an Expat, I want my bank account numbers and private details to be encrypted so that my financial privacy is protected against data breaches.

## Functional Requirements

1. **Application-Level Encryption** _(implemented)_: Services MUST encrypt and decrypt sensitive fields before persistence using Google Tink AEAD (AES-256-GCM), through the `SecretManager` port, with the keyset wrapped by an AWS KMS master key. Keysets MUST NOT exist as plaintext at rest in a deployed environment, and master key material MUST NOT be supplied in plaintext environment variables (ADR-017, still in force). Delivered by `TinkSecretManager` over `TinkCryptoService`; the presence of `CRYPTO_MASTER_KEY_URI` is the only discriminator between a KMS-wrapped keyset and the local-only plaintext one, and generated keysets live in git-ignored `infra/keysets/`.
2. **Deterministic Encryption** _(implemented; justification is forward-looking)_: Services MUST use deterministic encryption — Tink DAEAD (AES-256-SIV) — for `account_number`, so that an index, unique constraint, or exact-match lookup on the column remains possible.
   - **This is a capability preserved, not a behaviour protected.** No index, no unique constraint, and no query depends on it. `accounts.account_number` is declared plain `TEXT NOT NULL` in `V3__Add_Sensitive_Account_Fields.sql` with no index and no unique constraint, and no code in the repository filters, joins, or deduplicates on the column — account reads key on `id` and `tenant_id` only. **The "indexed exact-match lookups" and "reconciliation and duplicate detection" that this requirement previously cited as its justification do not exist.** If they are genuinely wanted they require their own index or constraint and query path, recorded as a documented traceability gap in [`TRACEABILITY.md`](TRACEABILITY.md).
   - **Masked-reference constraint (ADR-026 §3)**: the delivered `statement-import-reconciliation-contracts` capability mandates that import provenance carry only a masked account reference — `****` plus the last four characters — and forbids accepting or persisting an unmasked one. Equality on full-value deterministic ciphertext cannot serve a suffix match, so if reconciliation is the driver, **a keyed blind index over a normalized suffix is the likelier eventual mechanism** than deterministic encryption of the whole value. Deciding whether the deterministic capability is exercised at all is an ADR-026 follow-up, triggered before any index is built on `account_number`.
   - **Trade-off, unchanged from ADR-017**: deterministic encryption permits frequency analysis, so it is restricted to high-entropy fields and tenant-scoped associated data. An AWS KMS HMAC blind index is the recorded upgrade path if frequency analysis on that column later matters.
3. **Tenant-Bound Context** _(implemented)_: Encryption/decryption operations MUST bind tenant context as associated data to prevent cross-tenant decryption, including for the deterministic path, so the same account number under two tenants does not produce colliding ciphertext. `tenant_id` is bound as associated data on every AEAD and DAEAD operation.
4. **Key Management** _(partially implemented; rotation of the deterministic key deferred with a recorded trigger)_: Key lifecycle MUST be managed through Tink keyset rotation under the AWS KMS master key, on a documented rotation schedule, with deletion protection and alarms on destructive key operations.
   - **Delivered**: two customer managed keys, one per keyset, addressed by alias ARN and unwrapped once at startup rather than per field. Rotating the **KMS master key** is harmless — it only re-wraps the keyset, leaving field ciphertext untouched.
   - **Deferred, with trigger**: rotating the **Tink DAEAD primary key** changes the ciphertext produced for identical plaintext and therefore breaks deterministic equality on `account_number` until a column-wide rewrap exists. **No rewrap path exists, so the deterministic key is not rotated today.** ADR-026's trigger for building it: before the first real user data is persisted, or before any index or unique constraint is added to `account_number`, whichever comes first. Multi-Region keys, `ScheduleKeyDeletion`/`DisableKey` alarms, and a recorded restore rehearsal carry the same first trigger.
5. **Transparent Decryption** _(implemented)_: Authorized services automatically decrypt the data when retrieving it from the database, concurrently per row via `parMapN`.
6. **Fail-closed startup** _(implemented)_: Startup MUST fail before migrations run and before any port is bound if a master key cannot be resolved, a keyset cannot be unwrapped, or a database credential cannot be read. There MUST be no runtime fallback to a plaintext keyset and no fallback between credential providers. The ordering — credentials, keyset, migrate, bind — is encoded once in `ServiceStartup`.

## Data Points

- `accounts.account_number`: Encrypted (deterministic, AES-256-SIV).
- `accounts.routing_details`, `accounts.owner_full_name`, `tenants.tax_id`: Encrypted (non-deterministic, AES-256-GCM).
- `transaction-service` performs no application-level encryption and loads no keyset.

## Constraints

- **Performance**: Encryption/Decryption should not significantly impact the P95 latency (< 200ms target). This budget is the recorded reason ADR-026 defers ASVS 13.3.3 (all cryptographic operations inside an isolated security module) rather than performing per-field cryptography in a remote module.
- **Compliance**: OWASP ASVS 5.0.0 **Level 2** is the declared assurance target — **not L3**, which was an inherited and unjustified claim amended by ADR-026 §1. Adopted above L2: 13.3.4, 13.1.4, and the hardware-backed elevation of 13.3.1 (the KMS master key is HSM-resident; the derived Tink data-encryption keys are not). Deferred with reason: 13.3.3, on the P95 budget above. Recorded deviation: 13.2.1, static per-environment database credentials, with RDS IAM database authentication as the named upgrade. See [ADR-026](/reference/backend/decisions/ADR-026-secret-management-proportionality.md).
- **Least privilege (ASVS 13.3.2)**: migrations run under a migration credential holding `CREATE` (`expat_migrator`); services connect under a DML-only application credential (`expat_app`) that is denied `CREATE` on schema `public`. Per-service IAM roles with key-usage-only grants, key policies denying administrative actions to runtime roles, and CloudTrail retention for KMS `Decrypt` are an ADR-026 follow-up, triggered before the first real user data is persisted.
- **Credential rotation**: database credentials are static per-environment secrets read once at startup. **A rotated secret is picked up on restart, not in flight**; the lease/refresh loop the Vault posture required no longer exists.
