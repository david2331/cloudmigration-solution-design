# Selected cloud: AWS

# Tier 1 payments modernisation

**Status: architecture review draft, not an implemented or approved production solution.**

| Confirmed direction | Selection |
|---|---|
| Primary (P) | Malaysia, `ap-southeast-5` |
| Recovery (R) | Singapore, `ap-southeast-1` |
| Cross-border permission | User confirms approval already granted; approval record/reference still to be attached |
| Infrastructure as code | Terraform |
| CI/CD | GitHub Actions |
| Applications | Amazon EKS, OCI images and Helm charts |
| API gateway | Self-hosted Kong, owned by the platform team; application teams consume governed routing/policy capabilities |
| Entity isolation | Separate production accounts and EKS clusters per legal entity |
| Delivery model | Foundation infrastructure, application infrastructure, application code |

P/R denote operational locations, not legal entities or separate environments. Each entity has a primary and recovery deployment. Self-hosted Kong is the API gateway; **Amazon API Gateway is not part of the design**.

Start with the [executive summary](architecture-paper/01-executive-summary.md), [target architecture](architecture-paper/03-target-architecture.md), and [mandatory deployment diagram](diagrams/deployment-architecture.md).

## Assessment coverage

| Task | Weight | Authoritative document |
|---|---|---|
| 1. Architecture framing | 10% | [Principles, constraints and governance](architecture-paper/02-architecture-framing.md) |
| 2. Target architecture | 20% | [Accounts, services and boundaries](architecture-paper/03-target-architecture.md) |
| 3. Application platform decision | 15% | [EKS, ECS, Lambda and EC2](architecture-paper/04-application-platform-decision.md) |
| 4. Data and DR | 20% | [Integrity, replication and recovery](architecture-paper/05-data-and-dr.md) |
| 5. Threat and control model | 15% | [Threat-control matrix](architecture-paper/06-threat-control-model.md) |
| 6. Migration roadmap | 10% | [Waves and rollback](architecture-paper/07-migration-roadmap.md) |
| 7. Challenge response | 10% | [ADR-001: EKS platform decision](adr/ADR-001-EKS-Platform-Decision.md) |

## Required and supporting deliverables

| Deliverable | Location |
|---|---|
| Context, logical and deployment diagrams | [Context](diagrams/context-diagram.md), [logical](diagrams/logical-architecture.md), [deployment](diagrams/deployment-architecture.md) |
| DR and hybrid diagrams | [DR](diagrams/dr-architecture.md), [hybrid connectivity](diagrams/hybrid-connectivity.md) |
| Three-layer delivery diagram | [Deployment pipelines](diagrams/deployment-pipelines.md) |
| Decision records and ADR explanation | [Decision register and two-page-equivalent ADR](adr/ADR-001-EKS-Platform-Decision.md) |
| Ownership and consolidated RACI | [Ownership model](governance/ownership-model.md) |
| Release and Terraform governance | [Deployment governance](governance/deployment-governance.md) |
| Risk register | [Risks](architecture-paper/09-risk-register.md) |
| Validation and known limitations | [Acceptance evidence](architecture-paper/10-validation-and-limitations.md) |
| Assumptions and exclusions | [Scope](architecture-paper/11-assumptions-and-exclusions.md) |
| Cost transparency | [Cost considerations](appendix/cost-considerations.md) |
| DR exercise catalogue | [DR scenarios](appendix/dr-testing-scenarios.md) |
| Sources and AI disclosure | [Provider evidence](appendix/provider-native-evidence.md), [AI assistance](appendix/ai-assistance-disclosure.md) |

## Important review gates

Near-zero RPO must be quantified. Aurora cross-region replication is asynchronous and cannot guarantee no loss of acknowledged regional commits. Exclusive writer and external-submission fencing must be designed and demonstrated before claiming the 30-minute RTO. Kong DB-less/KIC is a proposed implementation topology, not an already selected edition or proven plugin set.

The numbered paper intentionally skips 08: its duplicate placeholder was consolidated into the authoritative ADR. Separate empty RACI placeholders were consolidated into the ownership model; redundant threat-diagram and service-rationale placeholders were replaced by the matrix and evidence register. No executable infrastructure, Helm charts or Actions workflows are supplied yet.
