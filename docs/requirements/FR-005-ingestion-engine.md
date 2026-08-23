# Requirement FR-005: Ingestion Engine

## Status

- **Type**: Functional Requirement
- **Priority**: Should Have
- **Iteration**: 3
- **Status**: Implemented

## Description

A configuration-driven engine to parse bank statements in Excel (.xlsx, .xls) and CSV formats. It maps bank-specific columns to the internal ledger format. Users should be able to import large volumes of transactions via Excel files.

## User Story

As an Expat, I want to upload my bank's monthly Excel statement so that I don't have to manually enter every transaction.

## Acceptance Criteria

- Valid Excel files (.xlsx, .csv) are parsed and ingested correctly.
- Error report generated for invalid rows.
- Success Metric: < 1% import failures.

## Functional Requirements

1. **Configurable Mapping**: Define which columns in a file correspond to Date, Amount, Description, and Currency.
2. **Multi-format Support**: Handle `.csv`, `.xls`, and `.xlsx`.
3. **Tenant-Specific Templates**: Allow different tenants to have different mappings for the same bank or custom files.
4. **Validation**: Detect and report parsing errors (e.g., invalid date format, non-numeric amount).
5. **Batch Processing**: Support high volumes of transactions in a single upload.
6. **Error Reporting**: Provide a report detailing which rows failed and why.

## PDF Statement Import (In Scope for R1)

- **PDF Import is in scope for R1**, delivered by the R1.2 "ABN Happy Path" slice. Direct PDF statement ingestion is the fastest route to getting real statement data into the platform, and the investigation into how to parse ABN AMRO statement PDFs is complete, so the original "high implementation complexity and low immediate ROI" basis for deferring it no longer holds. Approved by the product owner on 2026-08-04 (issue [#79](https://github.com/alexandervivas/expat-ledger-backend/issues/79)); recorded in `docs/governance/scope-CHANGELOG.md`.
- The authoritative public contract for PDF statement import — upload, import-draft retrieval and lifecycle, reconciliation outcome, confirmation, and discard — is defined in `docs/contracts/openapi/v1/openapi.yaml` under `/v1/statement-imports` (issue #79). The architectural decisions behind it are recorded in [ADR-024](/reference/backend/decisions/ADR-024-statement-import-draft-lifecycle.md).
- Constraints that apply specifically to PDF statement import, and that differ from Excel/CSV ingestion:
  - The uploaded PDF is **transient**: it is streamed, parsed, and discarded, and never reaches durable storage, backups, or logs. No operation retrieves, downloads, streams, or echoes it.
  - Persisted provenance is limited to safe metadata only: an algorithm-labelled `sha256:` file hash, parser version, bank identifier and bank code, a fixed-width masked account reference, the inclusive statement period, and the durable import result. The original filename, extracted statement text, the file's byte length, and unmasked account references are never accepted, persisted, or returned.
  - Import is a **review** workflow, not a fire-and-forget import: a draft is reconciled (`RECONCILED` / `NEEDS_REVIEW`), and only a reconciled draft may be confirmed.
- R1.2 covers the ABN AMRO PDF layout only. Bancolombia and ING PDF formats remain out of scope for R1.2.

## Deferred / Out of Scope

- **Row-level draft preview and correction**: reviewing and correcting individual parsed statement rows before confirmation is deferred beyond R1.2.
- **Automatic account matching**: the target account is supplied by the client on upload; inferring it from the statement is deferred beyond R1.2.
- **Overlapping-period detection**: R1.2 refuses a duplicate upload by file hash only; detecting the same period delivered as a differently generated file is deferred beyond R1.2.

## Data Points

- `bank_id`: Associated bank for the template.
- `column_mapping`: Map of domain fields to indices or headers.
- `date_format`: Pattern for parsing dates (e.g., `dd/MM/yyyy`).

## Constraints

- **Resource Management**: Large files must be processed using streaming to avoid memory issues (FS2 integration).
- **Idempotency**: Prevent duplicate transaction ingestion via `source_id` or hash checks.
