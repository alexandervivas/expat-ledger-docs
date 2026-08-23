# Requirement AI-004: Premium Advisor (Technical & Security Boundaries)

## Status

- **Type**: Functional Requirement / Security Policy
- **Priority**: High (for Premium Tier)
- **Iteration**: 6
- **Status**: Draft

## Description

Defines the security and privacy boundaries for the 24/7 AI Financial Advisor (USP-010). It ensures that ledger data can be used to ground the LLM without compromising the system's "Zero-Knowledge" pillar (ADR-017).

## Functional Requirements

1. **Context Grounding**: The system must summarize ledger data (balances, recent spending, currency exposures) to provide context to the LLM.
2. **PII Scrubbing**: Before sending data to any external LLM provider, the system MUST scrub all Personal Identifiable Information (PII) such as account numbers, specific merchant names (unless relevant to categorization), and exact street addresses.
3. **Differential Privacy**: Use techniques like rounding or noise addition to prevent the exact identification of high-net-worth individuals from transaction patterns.
4. **Tenant Isolation**: The LLM session must be strictly isolated. Data from one tenant MUST NEVER be used to train or prompt responses for another tenant.
5. **On-Demand Context**: Context should be fetched on-demand and NOT persisted in the LLM's long-term memory.

## Technical Constraints

- **Zero-Knowledge Compatibility**: The backend (which holds the ALE keys) performs the summarization. The raw, encrypted descriptions (ALE-protected) are decrypted in memory, summarized, and then the summary is sent to the LLM.
- **Audit Logging**: All queries to the AI Advisor must be logged for security audits, but responses containing sensitive financial advice must be encrypted at rest.

## Acceptance Criteria

- No PII is sent to external LLM providers.
- LLM responses are relevant to the user's specific financial situation.
- Zero cross-tenant data leakage via the LLM context.
