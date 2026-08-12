# Requirement FR-007: RBAC & Identity Propagation

## Status

- **Type**: Functional Requirement
- **Priority**: High
- **Iteration**: 2
- **Status**: Implemented

## Description

A security framework ensuring that users only access data belonging to their authorized tenants. It uses Role-Based Access Control (RBAC) and propagates user identity across microservice boundaries.

## User Story

As a user, I want my data to be private and inaccessible to other users, and I want to be able to grant specific permissions to other people if I choose to share my tenant.

## Functional Requirements

1. **Identity Resolution**: Map external Auth0 `sub` claims to internal `UserId`.
2. **Tenant Mapping**: Maintain a mapping of Users to Tenants with specific Roles (OWNER, ADMIN, VIEWER).
3. **Permission Enforcement**: Check permissions (e.g., `ViewTenant`, `ManageAccounts`) before executing service logic.
4. **Context Propagation**: Pass the authenticated `UserId` through gRPC metadata across all service calls.

## Data Points

- `user_id`: Unique UUID.
- `tenant_id`: Reference to the tenant.
- `role`: Role enum.
- `permissions`: List of granular permission enums.

## Constraints

- **Performance**: Authorization checks must be cached (Scaffeine) to meet P95 < 200ms.
- **Security**: Deny-by-default for all endpoints.
