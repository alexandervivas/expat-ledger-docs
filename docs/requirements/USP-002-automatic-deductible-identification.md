# USP-002: Automatic Deductible Identification

## Status

- **Type**: Unique Selling Point
- **Priority**: Could Have
- **Status**: Draft

## Description

Uses the AI engine to proactively flag transactions that may be tax-deductible based on the user's current tax residency and the transaction metadata (e.g., category, merchant description).

## Functional Alignment

- **AI-001/AI-003**: Extends AI capabilities to include tax-specific logic.
- **FR-014**: Leverages the filtering engine to isolate potential deductibles.

## Key Features

1. **Category-Residency Mapping**: "This moving expense in Berlin is deductible under German tax law."
2. **Flagging Workflow**: Automatically marks potential deductibles in the UI with a "Possible Tax Deduction" badge.
3. **Confirmation Loop**: Users confirm if the flag is correct, refining the local AI model for that tenant.

## Business Value

Provides immediate financial ROI to the user by ensuring they don't miss tax-saving opportunities inherent to their expat status.
