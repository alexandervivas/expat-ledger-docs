# USP-001: "Tax-Residency Ready" Exports

## Status

- **Type**: Unique Selling Point
- **Priority**: Must Have (Integrated into FR-015)
- **Status**: Draft

## Description

Leverages the system's awareness of the user's `TaxResidency` to provide one-click report templates for specific international tax filings. This transforms a standard ledger into a compliance-first tool for global citizens.

## Target Audience

Expats living in countries with strict reporting requirements (e.g., US citizens abroad, residents of Spain with foreign assets).

## Functional Alignment

- **FR-001**: Uses the `taxResidencies` defined during onboarding.
- **FR-015**: Extends the "Automated Export" capability with specific templates.

## Key Features

1. **FBAR/FATCA Ready**: CSV/PDF templates that follow the structure required for US FinCEN Form 114.
2. **Model 720 (Spain)**: Groups assets and maximum balances as required by Spanish tax law.
3. **UK Income Summary**: Summarizes foreign income for Self Assessment tax returns.
4. **Secure Provenance**: Compliance exports include execution metadata and integrity/signing information so generated artifacts remain auditable and tamper-evident.
5. **Privileged Generation Path**: Sensitive compliance exports are generated through the `maintenance-worker` using Vault-mediated decryption rather than a normal user-facing request path.

## Business Value

Reduces the "Audit Anxiety" for expats by ensuring their financial data is organized according to the rules of their specific tax residencies.
