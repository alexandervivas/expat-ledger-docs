# USP-007: Zero-Knowledge Ledger

## Status

- **Type**: Unique Selling Point
- **Priority**: Must Have (Integrated into FR-008)
- **Status**: Draft

## Description

The system uses application-level encryption (ALE) so that sensitive data (e.g., transaction descriptions, account numbers) is never stored in plaintext. This ensures that even database administrators or hosting providers cannot read the transaction details.

**Terminology.** "Zero-knowledge" here means **application-layer encryption with host-blind storage** — the database and hosting provider hold only ciphertext. It does **not** mean a zero-knowledge proof system, and no such construction is claimed or used.

## Functional Alignment

- **[ADR-027](/reference/backend/decisions/ADR-027-secret-management-proportionality.md)**: The current decision. Google Tink AEAD (AES-256-GCM) for PII fields and DAEAD (AES-256-SIV) for `account_number`, with `tenant_id` bound as associated data, and the keyset wrapped by an AWS KMS customer managed key. Declared assurance target is OWASP ASVS 5.0.0 Level 2 with named additions and deferrals.
- **[ADR-018](/reference/backend/decisions/ADR-018-application-level-encryption.md)**: Originated the ALE architecture; its Tink AEAD/DAEAD mechanism is reinstated by ADR-027, while its key-management sections are superseded.
- **[FR-008](FR-008-data-encryption.md)**: The requirement this USP is integrated into. Note that FR-008 is forward-looking — the posture is decided but the runtime is not yet migrated.

## Key Features

1. **Host-Blind Privacy**: Market the "Zero-Knowledge" aspect—only the tenant's authenticated session can decrypt descriptions.
2. **ALE-First Design**: Encryption happens at the application boundary, not just at the database level (TDE).
3. **Regional Privacy Compliance**: Specifically targets high-net-worth expats in regions with unstable privacy laws or high surveillance.

## Business Value

Establishes the platform as an "Enterprise Grade" vault for personal wealth, building deep trust with privacy-conscious users.
