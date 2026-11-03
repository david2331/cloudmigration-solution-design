# Architecture framing

**Selected cloud: AWS. Task 1 (10%). Status: review draft.**

## Principles and quality attributes

| Principle | Consequence |
|---|---|
| Financial correctness before uncontrolled availability | Halt uncertain submissions rather than create duplicate settlement or split-brain writes |
| Entity isolation by default | Separate production accounts, clusters, data and keys; explicit approved interfaces for exceptions |
| Residency covers every copy | Govern replicas, backup, telemetry, Terraform state, CI artifacts and operational exports |
| Provider-native where justified | Use managed AWS capabilities with documented behaviors, not unsupported end-to-end guarantees |
| Platform as a product | Central team operates EKS/Kong and guardrails; applications consume stable supported interfaces |
| Portability through boundaries | Keep business logic independent of ingress plugins, IAM credential retrieval and messaging adapters |
| Single resource and transaction authority | One IaC/controller owner per resource and one authoritative writer per migrated payment cohort |
| Recovery by evidence | Exercise AZ loss, regional loss, partitions and clean-room restoration independently |

## Hard constraints

| Constraint | Interpretation |
|---|---|
| Cloud | AWS; no Azure or cross-cloud target |
| Geography | P: Malaysia `ap-southeast-5`; R: Singapore `ap-southeast-1`; approved cross-border scope must be evidenced |
| Availability | 99.99% for defined critical journeys, approximately 52.6 minutes/year or 4.32 minutes per 30 days |
| RTO | At most 30 minutes from disruption to safe operation for the agreed regional-failure scenarios |
| RPO | Near zero for committed transactions; numerical tolerance and meaning of commitment require business decision |
| Runtime and deployment | EKS, Helm, Terraform and GitHub Actions |
| Gateway | Self-hosted Kong; platform owner, application consumers |
| Responsibility | Central landing zones/guardrails; product-owned applications and SLOs |
| Auditability and migration | Traceable configuration and financial events; staged migration with explicit reversal limits |

An annual and a monthly SLO window are not interchangeable. Select the contractual window, eligible requests, latency thresholds and exclusions before sign-off. A 30-minute outage can meet the disaster RTO while breaching a monthly 99.99% SLO. Define acceptance, posting, status and external-submission indicators separately, with dependency budgets and burn-rate alerts.

## Decision owners and governance

| Decision | Accountable role | Required concurrence |
|---|---|---|
| Landing-zone/EKS/Kong lifecycle | Platform owner | Security, network, application representatives |
| Residency rules and evidence custody | Security/compliance | Legal and entity business owner |
| Commitment semantics and loss tolerance | Payments business/risk owner | Data engineering, payments engineering, operations |
| Application infrastructure and design | Application owner | Platform, security, data engineering |
| Database topology and recovery readiness | Data owner | Application, operations, security |
| Production execution | Operations/release owner | Product service approval and required independent change gates |
| Regional recovery authorization | Business/service owner under delegated incident procedure | Incident commander, data, platform and network |

Use the [consolidated RACI](../governance/ownership-model.md) for execution details. No accountable owner can bypass mandatory security or financial-integrity gates.

Architecture reviews occur at design baseline, production readiness, migration-wave exit and material change. Each exception has an owner, expiry, compensating control and review trigger. ADRs capture rationale and rejected alternatives; policy-as-code enforces repeatable rules but does not replace risk acceptance.

AWS Organizations/Control Tower support account provisioning and guardrails [S1]. SCPs set permission ceilings, do not grant permissions, and do not establish residency alone. EKS manages its control plane, not workload correctness or all cluster operations [S2]. Kong's DB-less behavior changes configuration ownership and plugin compatibility [S9].

Sources: [provider evidence](../appendix/provider-native-evidence.md). Assumptions: [scope and exclusions](11-assumptions-and-exclusions.md).
