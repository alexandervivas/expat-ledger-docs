# Requirement FR-015: Automated Export (PDF/CSV)

## Status

- **Type**: Functional Requirement
- **Priority**: Must Have
- **Iteration**: 4
- **Status**: Draft

## Description

Generate reports for offline analysis based on current dashboard views.

## User Story

As a user, I want to export my filtered transaction list to a PDF or CSV file so that I can share it with my accountant or perform further analysis in Excel.

## Acceptance Criteria

- PDFs must maintain high-fidelity chart renders.
- CSV exports must include all raw data currently filtered.

## Functional Requirements

1. **CSV Export**: Generate a standard CSV file containing all fields of the currently filtered transaction list.
2. **PDF Export**: Generate a formatted PDF report including summary charts and a transaction table.
3. **Tax-Ready Templates**: Provide one-click report templates for specific tax filings based on the user's tax residency (e.g., FBAR/FATCA for USA, Model 720 for Spain, or Income Summaries for the UK).
4. **Privileged Compliance Worker**: Tax-filing exports that require decrypted sensitive fields must be generated through the `maintenance-worker` privileged workflow, not through the normal user-facing runtime path.
5. **Artifact Provenance**: Compliance export artifacts must include generation metadata and integrity or signing information so operators can verify export provenance and trace outputs back to the execution context.
6. **Async Generation**: Large exports should be handled asynchronously with a notification when ready.

## Constraints

- **Privacy**: Exported files must be handled securely and only accessible by the authorized user.
- **Security Boundary**: Decrypted compliance export generation must remain tenant-scoped, Vault-mediated, and auditable.
