# Requirement NFR-003: Reliability (DR/BKP)

## Status

- **Type**: Non-Functional Requirement
- **Status**: Active

## Description

Define the strategies for Disaster Recovery (DR) and Backup (BKP) to ensure business continuity and data integrity.

## Targets

- **RTO (Recovery Time Objective)**: < 4 hours. The maximum acceptable length of time that the ledger can be down after a regional failure.
- **RPO (Recovery Point Objective)**: < 15 minutes. The maximum acceptable amount of data loss measured in time.

## Functional Requirements

1. **Automated Backups**: Daily full backups of the PostgreSQL database and WAL (Write-Ahead Logging) archiving for Point-in-Time Recovery (PITR).
2. **Cross-Region Replication**: (Optional for Phase 2) Replicate backups to a different geographical region to protect against total regional outages.
3. **Recovery Drills**: Conduct quarterly recovery drills to verify the RTO and RPO targets.

## Constraints

- **Compliance**: Backup retention policies must comply with GDPR/CCPA and local financial regulations (e.g., 5-7 years retention).
- **Encryption**: All backups must be encrypted at rest.
