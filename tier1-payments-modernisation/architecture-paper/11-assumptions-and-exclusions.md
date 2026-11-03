# Assumptions and exclusions

**Selected cloud: AWS. Distinguish user-confirmed direction from proposed design and unresolved requirements.**

| ID | Status | Statement |
|---|---|---|
| C01 | Confirmed | AWS is the selected target cloud |
| C02 | Confirmed | Terraform is IaC; GitHub Actions is CI/CD; applications use EKS and Helm |
| C03 | Confirmed | Self-hosted Kong is platform-owned; application teams are gateway service consumers |
| C04 | Confirmed | P is Malaysia `ap-southeast-5`; R is Singapore `ap-southeast-1` |
| C05 | User-confirmed approval | Malaysia/Singapore cross-border approval is already granted; evidence reference and scope remain to be attached |
| C06 | Confirmed | Production accounts and clusters are isolated by legal entity |
| C07 | Scenario requirement | 99.99% critical-journey availability, 30-minute RTO, near-zero committed-payment RPO |
| P01 | Proposed | DB-less Kong/KIC per entity/region; exact edition, plugins and Gateway API support need acceptance |
| P02 | Proposed | Aurora PostgreSQL regional ledger and asynchronous Global Database secondary |
| P03 | Proposed | Live regional DR in entity production account; isolated entity recovery account for backups/clean room |
| P04 | Proposed | Central security, log, network and tooling accounts with residency-scoped data |
| P05 | Proposed | SQS with outbox and idempotent processing; no implicit cross-region queue replication |
| A01 | Assumption | Three suitable AZs and sufficient required service/instance capacity can be allocated in each region |
| A02 | Assumption | Bank can fund and staff Kubernetes, Kong and 24x7 payment operations |
| A03 | Assumption | Hybrid core banking, screening and rails remain available under documented dependency objectives |
| O01 | Open | Actual legal entities, transaction volumes, peaks, payloads, latency and retention periods |
| O02 | Open | Commitment definition, numerical RPO, permitted lost transaction exposure and SLO measurement window |
| O03 | Open | Enforceable writer/submission fencing and external-rail unknown-outcome handling |
| O04 | Open | Production versions, licensing, account IDs, CIDRs, domain names, approval references and named operators |

## Exclusions

No executable implementation or cloud deployment is included in this documentation update. Account names, AZ slots and service names are consistent design identifiers, not live account IDs or created resources. No secrets, customer data or production payloads belong in the repository or GitHub job logs.

No Azure services, cross-cloud recovery or Kong-hosted control plane are introduced. On-premises systems remain explicitly justified hybrid dependencies.

No claim is made of final regulatory certification, zero-loss regional recovery with asynchronous replication, a universal 30-minute cyber-recovery capability, exact global Kong rate limiting, or cloud portability without adapter and operational work.

Country mapping is not legal-entity mapping: each approved entity is deployed in both countries. Separate accounts do not automatically establish segregation of duties if administrator roles remain overly broad.
