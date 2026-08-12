# USP-009: Personal Finance API

## Status

- **Type**: Unique Selling Point
- **Priority**: Could Have
- **Status**: Draft

## Description

Give tech-savvy expats (developers/quants) an API key to read their own ledger data into their own scripts or Excel sheets via gRPC or REST. This is a secure and modern alternative to the "Custom SQL" requirement.

## Functional Alignment

- **FR-007**: Leverages the existing RBAC and identity propagation logic.
- **ADR-018**: Ensures API access respects application-level encryption.

## Key Features

1. **Scoped API Keys**: Generate keys that only have read access to a specific tenant's data.
2. **Standard Protocols**: Support for REST (via Tapir) and gRPC (via Protobuf) for programmatic access.
3. **Quant-Friendly Exports**: Direct JSON/CSV streaming for easy ingestion into Python/Pandas or Excel.

## Business Value

Attracts high-value power users who want to build their own custom dashboards or automated financial workflows on top of a secure, multi-currency ledger.
