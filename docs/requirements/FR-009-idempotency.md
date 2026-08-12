# Requirement FR-009: Idempotency

## Status

- **Type**: Functional Requirement
- **Priority**: High
- **Iteration**: 2
- **Status**: Implemented

## Description

To ensure system reliability in the face of network failures or retries, all mutating operations (POST, PUT, DELETE) must be idempotent.

## User Story

As a user, if my internet connection drops while I'm creating a transaction and I retry the request, I want to be sure that the transaction is only created once and not duplicated.

## Functional Requirements

1. **Idempotency-Key**: Every mutating endpoint must require an `Idempotency-Key` header.
2. **Response Caching**: The system must persist the result of an operation associated with the `(route, idempotency-key, tenant_id)`.
3. **Replay Logic**: If a request with the same key is received within a 24-hour window, the system must return the cached response instead of re-executing the logic.
4. **Consistency**: The system must ensure that the request body for a repeated key matches the original request; otherwise, it should return a 409 Conflict.

## Data Points

- `idempotency_key`: Unique string provided by the client.
- `cached_response`: The full HTTP/gRPC response previously returned.

## Constraints

- **Storage**: Idempotency records should be cleaned up periodically (e.g., after 24-48 hours).
- **Tenant Isolation**: Idempotency keys must be scoped to a `tenant_id` to prevent cross-tenant key collisions.
