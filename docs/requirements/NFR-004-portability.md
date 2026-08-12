# Requirement NFR-004: Portability

## Status

- **Type**: Non-Functional Requirement
- **Status**: Active

## Description

Ensure the backend remains cloud-agnostic and easily portable between different infrastructure providers.

## Functional Requirements

1. **Containerization**: All services must be fully containerizable using Docker.
2. **Infrastructure-as-Code (IaC)**: Use standardized IaC tools (e.g., Terraform, Crossplane) for provisioning resources.
3. **Twelve-Factor App Compliance**: Follow Twelve-Factor App principles, especially regarding configuration (environment variables) and backing services.
4. **Standard Protocols**: Favor standard protocols (gRPC, AMQP 0.9.1, JDBC) over provider-specific APIs to avoid vendor lock-in.

## Constraints

- **JVM Runtime**: Services must run on standard OpenJDK 21+ environments. This is a runtime-portability floor, not a toolchain statement: the supported and CI-verified toolchain is **JDK 25** (`.tool-versions` pins `corretto-25.0.1.8.1`, and both CI jobs build on Temurin 25), which satisfies the 21+ floor.
- **Statelessness**: Application containers must be stateless to allow easy horizontal scaling and migration.
