# Architecture framing

**Selected cloud: AWS. Task 1 (10%). Status: review draft.**

## Principles

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

## Quality attributes

Targets marked *proposed* are architecture starting points for the payments business owner to confirm; they are not measured results.

| Attribute | Measurable target | Primary AWS mechanism | How it is verified |
|---|---|---|---|
| Availability | 99.99% per critical journey (acceptance, status, posting), measured per calendar month on eligible requests | Three-AZ EKS, Kong and Aurora; ARC zonal shift [S19] | SLO burn-rate alerts; monthly SLO report |
| Recoverability | Regional RTO ≤ 30 min from disruption to safe journeys; RPO near zero, bounded by quantified replication lag | Aurora Global Database [S5, S17]; ARC routing controls [S18] | Quarterly regional exercise with FIS [S20]; measured lost-tail count |
| Integrity | Zero duplicate or lost financial effects for acknowledged commits within a region; 100% daily ledger-to-rail reconciliation | ACID ledger + outbox on Aurora; idempotency keys | Daily reconciliation breaks = 0 unresolved after T+1 |
| Latency (*proposed*) | Payment acceptance p99 ≤ 500 ms at peak, excluding external rail time | In-region writer access; RDS Proxy [S21] | Load test at 2x peak with one AZ removed |
| Throughput (*proposed*) | Sustain 2x forecast peak TPS per entity with one AZ lost | EKS node headroom; Aurora instance sizing | Capacity test before each migration wave |
| Security | No standing human production access; all deploy identity short-lived; 100% signed images at admission | IAM Identity Center, GitHub OIDC [S7], admission policy | Access review; admission deny logs; CloudTrail |
| Auditability | Every production change and financial correction traceable to identity, approval and artifact digest; logs immutable for the retention period | CloudTrail, S3 Object Lock [S28], Database Activity Streams [S29] | Quarterly audit sample; Object Lock compliance check |
| Residency | 100% of regulated data copies in approved locations | SCP region allow-list, endpoint and key policies | Copy inventory against approval scope (C05) |
| Operability | Platform upgrades within EKS standard support; runbook-only recovery without GitHub | EKS managed upgrades; prepositioned artifacts | Upgrade calendar; GitHub-outage DR exercise |
| Cost transparency | 100% of spend allocated to entity and product; unit cost per completed payment published monthly | Account-per-entity, tags, split cost allocation data [S30] | Monthly allocation coverage report |
| Portability | Known, bounded switching cost to another conformant Kubernetes runtime | OCI images, Gateway API, PostgreSQL schema, adapters | Annual portability exercise ([Task 3](04-application-platform-decision.md)) |

## Availability composition

A journey's availability is the product of the components it needs in series. AWS components are made redundant across three AZs, so the binding constraints are usually the single-path dependencies outside AWS.

| Component on the payment-acceptance path | Assumed availability | Basis |
|---|---|---|
| Route 53 + ALB + WAF (multi-AZ) | 99.99% | Regional AWS edge path with ARC zonal shift |
| Kong (3+ replicas, 3 AZs) | 99.995% | Bank-operated; needs proven AZ-loss capacity |
| EKS payment services (3 AZs) | 99.995% | Bank-operated workload resilience |
| Aurora writer with in-region failover | 99.99% | Failover typically completes within a minute or two; connections recovered via RDS Proxy |
| Hybrid path to on-premises (diverse DX + VPN) | 99.99% | Two diverse DX locations plus independent VPN |
| On-premises core banking / screening | **assumption A03 — to be supplied** | Bank-owned dependency |

Treated as independent serial components, the four AWS components alone compose to about **99.97%** (0.9999 × 0.99995 × 0.99995 × 0.9999), and adding the hybrid path gives about **99.96%** — both below 99.99% before the on-premises systems are counted. Serial multiplication of the components' availability figures is pessimistic for failures that redundancy absorbs (an AZ loss is not downtime if the surviving AZs carry the load), but optimistic for correlated failures such as a bad release or a regional control-plane event. The conclusion holds either way: 99.99% is not achieved by selecting highly available services; it is achieved only by error-budget management of the journey. The design therefore:

- Makes **payment acceptance** depend only on in-region AWS components plus a durable ledger write. Screening and core-banking posting run asynchronously behind the outbox, so their outages delay processing rather than reject acceptance. Mandatory sanctions and fraud screening still completes before any external submission.
- Counts against the 4.32-minute monthly budget only **unabsorbed** failure. AZ impairment is evacuated with ARC zonal shift [S19] onto pre-provisioned spare capacity; Aurora writer failover reconnects through RDS Proxy [S21]; releases use canaries with automatic stop. Each of these must be exercised to show it completes inside the budget.
- Treats **status queries** as read-only journeys served from Aurora readers, with their own SLO.
- Requires each synchronous external dependency to publish an availability objective (A03). Any synchronous dependency below 99.99% makes the journey target unattainable and must be renegotiated or decoupled.

These figures are design assumptions for allocation, not provider SLA commitments or measured values.

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

Sources: [provider evidence](../appendix/provider-native-evidence.md). Assumptions: [scope and exclusions](10-assumptions-and-exclusions.md).
