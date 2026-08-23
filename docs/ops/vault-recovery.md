# Vault Disaster Recovery Runbook

> **⚠ NOT IN FORCE — HISTORICAL RECORD ONLY**
>
> **Status: not in force as of 2026-08-08. Superseded by [ADR-026](/reference/backend/decisions/ADR-026-secret-management-proportionality.md) (Accepted 2026-08-06). Do not treat any step below as executable.**
>
> **The component this runbook recovers no longer exists.** HashiCorp Vault has been removed from every path in this repository — code, configuration, infrastructure, compose services, and dependencies. There is no Vault server to seal, unseal, restore, or contain. The delivered posture is Google Tink AEAD (AES-256-GCM) and DAEAD (AES-256-SIV) behind the `SecretManager` port, with keysets wrapped by two AWS KMS customer managed keys, and static per-environment database credentials read from AWS Secrets Manager. See [`docs/architecture/security-encryption-guide.md`](../architecture/security-encryption-guide.md).
>
> **This runbook was never executable by the current team, independently of the removal.** It requires a 3-of-5 Shamir unseal quorum with at least two distinct custodians, plus distinct Incident Commander, Operator, and Recorder roles, and instructs that quorum controls must not be bypassed. A single maintainer cannot form a two-custodian quorum, so under the present team a sealed Vault would have been an **unrecoverable outage** rather than a recoverable incident. That is the failure mode this document demonstrates, and the reason ADR-026 treats an unoperable secret provider as the availability and data-loss risk rather than the mitigation.
>
> **A KMS-oriented recovery runbook is a named follow-up obligation, and it is not yet written.** ADR-026's [follow-up obligations](/reference/backend/decisions/ADR-026-secret-management-proportionality.md#follow-up-obligations) table records it as due with the cutover, "since the existing runbook becomes actively misleading" — hence this banner. Its custodianship model must be executable by one person, and it must be written around the real failure mode: loss, disablement, or scheduled deletion of a KMS master key, with multi-Region keys, deletion protection, a long deletion waiting period, alarms on destructive key operations, and a rehearsed restore. Until that document exists there is **no in-force secret-recovery runbook** for this repository.
>
> This file is retained, not deleted, because the body below records a real tabletop exercise. Read it as history, not as instructions.

## Scope

This runbook defines operational steps to recover HashiCorp Vault after a security incident, including suspected or confirmed data breach, credential compromise, seal/unseal disruption, and persistent volume loss.

The objective is containment-first recovery with deterministic gates before dependent services resume.

## Incident Classifications

- `SEV-1 Breach`: Suspected or confirmed unauthorized access to Vault, tokens, AppRole credentials, or host infrastructure.
- `SEV-1 Availability`: Vault unavailable, sealed unexpectedly, or failed startup with no active breach indicators.
- `SEV-0 Data Loss`: Corruption or loss of Vault persistent storage requiring restore from backup.

If classification is ambiguous, use the `SEV-1 Breach` path by default.

## Prerequisites

- Authorized responders are available for assigned roles.
- Access to Vault host/runtime and backup storage is available.
- Offline access to Shamir recovery shares is available to custodians.
- Latest known-good Vault data backup exists and is retrievable.
- Incident ticket is opened and timeline logging has started.

## Roles and Responsibilities

- `Incident Commander (IC)`: Owns prioritization and decision points; authorizes progression between phases.
- `Key Custodian(s)`: Provide Shamir shares under quorum policy and confirm custody controls.
- `Operator`: Executes Vault and infrastructure commands.
- `Recorder`: Captures evidence and command log with UTC timestamps.
- `Service Owner Approver`: Authorizes dependent service re-entry after recovery gates pass.

Dual control is mandatory: the same individual must not act as both sole executor and sole approver for unseal/re-entry.

## Breach-Response Phases

### 1) Detection

- Confirm symptoms and scope:
  - Unauthorized token issuance or policy change
  - Unknown AppRole usage
  - Unexpected seal/unseal events
  - Integrity alerts on Vault data host
- Declare incident severity and assign roles.
- Start evidence log (`who`, `when`, `action`, `outcome`, `evidence link`).

### 2) Containment (Mandatory Before Rotation)

- Restrict ingress and administrative access to approved responders.
- Revoke active high-risk tokens first, then broad token families as required.
- Disable or tightly scope exposed authentication paths until recovery is stable.
- Suspend dependent service restarts until post-restore validation gates pass.

### 3) Recovery

- If sealed, execute manual unseal procedure (below) using Shamir quorum.
- If storage is compromised/unavailable, restore Vault data volume from known-good backup.
- Bring Vault to healthy state before any key or credential rotation.

### 4) Validation

- Run mandatory recovery gates (see Recovery Validation Gates).
- Do not restart dependent services until all gates pass and IC + Service Owner approval is recorded.

### 5) Post-Incident Hygiene

- Rotate compromised credentials and keys in controlled sequence.
- Document blast radius and remediation follow-ups.
- Schedule postmortem and backlog hardening actions.

## Manual Unseal Procedure (Shamir Quorum)

### Quorum and Control Rules

- Minimum quorum for recovery shares is `3-of-5` unless an environment-specific policy supersedes this value.
- At least two distinct custodians must participate.
- Recorder must capture each submitted share event with UTC timestamp.

### Execution Sequence

1. IC confirms incident state, role assignment, and scope of unseal.
2. Operator verifies Vault is sealed and in recovery scope.
3. Custodians provide shares one at a time; operator submits each share.
4. After quorum completion, operator verifies `sealed=false`.
5. Recorder logs final unseal status and command evidence.

If quorum cannot be achieved, escalate to security leadership and continue containment posture; do not bypass quorum controls.

## Shamir Share Emergency Handling Policy

- Shares must remain split across independent custodians and storage domains.
- Shares must never be copied into source control, chat, ticket bodies, or plaintext shared storage.
- Access requests require IC authorization and second-party verification.
- After suspected share exposure, declare breach path and rotate/re-key per security policy.

## Backup Procedure (Vault Data Volume)

1. Confirm backup window and source volume identity.
2. Capture pre-backup metadata (host, vault version, storage path, UTC time).
3. Create encrypted backup artifact in approved backup location.
4. Record checksum and retention metadata in evidence log.
5. Verify backup readability and checksum integrity.

## Restore Procedure (Vault Data Volume)

1. Keep containment controls active and prevent service restarts.
2. Select latest known-good backup based on integrity evidence.
3. Restore data volume to target environment.
4. Validate filesystem ownership/permissions required by Vault runtime.
5. Start Vault and verify process-level health before unseal/validation.

## Recovery Validation Gates (All Required)

- `Gate 1`: Vault reports healthy status and API responsiveness.
- `Gate 2`: Vault seal status is `unsealed`.
- `Gate 3`: Transit smoke test succeeds (`encrypt` then `decrypt` round trip).
- `Gate 4`: Dynamic credential issuance smoke test succeeds for a dependent service role.
- `Gate 5`: IC and Service Owner Approver sign off on service re-entry.

Failure of any gate returns the process to containment + recovery troubleshooting; no partial re-entry.

## Credential and Key Hygiene Sequence (Post-Containment)

1. Revoke suspect tokens and disable compromised auth artifacts.
2. Rotate AppRole/operational secrets for affected services.
3. Evaluate Transit key rotation requirement; rotate where risk assessment demands it.
4. Assess and execute rewrap workflow for impacted encrypted data if key version changed.
5. Re-run validation gates after each high-risk rotation step.

## Service Re-entry Criteria

Dependent services may resume only when all conditions hold:

- Recovery validation gates are complete and recorded.
- No active containment blocker remains open.
- Credential and key hygiene steps required for the incident class are complete.
- IC and Service Owner Approver provide explicit approval in incident record.

## Audit Evidence Checklist

For each critical step, record:

- `who`: responder identity and role
- `when`: UTC timestamp
- `what`: command/procedure step executed
- `result`: pass/fail plus key output summary
- `proof`: log/screenshot/artifact reference

## Tabletop Walkthrough Notes (2026-02-18)

Walkthrough scenario: suspected AppRole credential leak plus Vault restart requiring manual unseal.

Clarity fixes captured during walkthrough and applied in this runbook:

- Added explicit containment-before-rotation ordering to avoid attacker persistence windows.
- Added fixed validation gate list before dependent service restart.
- Added required dual-control statement for unseal and service re-entry approvals.
- Added audit evidence schema (`who/when/what/result/proof`) for post-incident traceability.
