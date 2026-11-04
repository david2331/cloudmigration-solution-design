# Executive architecture summary

**Selected cloud: AWS.**

Modernise the Tier 1 payments platform progressively using independently isolated legal-entity deployments. **Malaysia (`ap-southeast-5`) is primary; Singapore (`ap-southeast-1`) is recovery.** Cross-border permission is granted per bank confirmation (assumption C05); security/compliance must attach the approval record and applicable scope to the implementation evidence.

The target combines Amazon EKS and Helm for applications, Terraform for infrastructure, GitHub Actions for delivery, and **platform-owned self-hosted Kong** for API gateway capabilities. Application teams consume Kong through approved route configuration; they do not operate shared gateway infrastructure.

## Business outcomes and proposed design

| Outcome | Design response | Important qualification |
|---|---|---|
| 99.99% critical-journey availability | Active application and Kong replicas across three AZs, resilient connectivity and database failover | Provider SLAs and replica counts do not prove the end-to-end SLO |
| 30-minute RTO | Pre-provisioned Singapore compute, Kong, connectivity, keys, secrets, artifacts and database secondary | Measured from disruption to safe service restoration; target is not yet demonstrated |
| Near-zero RPO | Aurora PostgreSQL regional durability and asynchronous Aurora Global Database replication | Regional loss can lose committed replication tail; numeric tolerance remains unresolved |
| Entity separation | Independent production accounts, regional clusters, databases, IAM boundaries and keys | Shared governance does not imply shared data or unrestricted administration |
| Progressive migration | Bounded payment cohorts, a single authoritative writer, coexistence adapters and reconciliation | Reversing traffic after new writes is not a safe rollback by itself |
| Portability | OCI images, Kubernetes/Helm, explicit API and event contracts, data and identity adapters | AWS databases, messaging and recovery still create migration work |
| Cost accountability | Entity/product allocation, shared-platform rules and cost per completed payment | Per-entity clusters and ready DR capacity have material fixed cost |

## Operating model

Exactly three delivery layers separate responsibilities. Platform teams own foundation infrastructure and the Kubernetes/Kong lifecycle subpipeline. Product teams own application infrastructure and application releases, using centrally governed modules and service interfaces. Product teams own their end-to-end SLOs; platform teams own published platform service objectives.

Kong runs separately per entity and region, not as one cross-entity gateway. The proposed topology is DB-less Kong managed by Kong Ingress Controller (KIC). AWS load balancers provide ingress transport and WAF integration; Kong provides API routing and approved gateway policies. Backend applications still enforce business authorization and idempotency.

## Decisions needed before production approval

The bank must define payment commitment semantics, numerical RPO tolerance, critical journeys, peak capacity and latency. Aurora Global Database is a defensible near-zero regional RPO proposal only if its residual loss exposure is acceptable. If no acknowledged commit may be lost during regional failure, redesign the commitment durability mechanism rather than describe asynchronous replication as zero-loss.

Cross-border approval is not an open choice in this draft; its evidence and data-category scope still need recording. Kong edition/plugin compatibility, reliable fencing, external-rail recovery, capacity and complete recovery timings remain implementation gates.

See [framing](02-architecture-framing.md), [target architecture](03-target-architecture.md), [data and DR](05-data-and-dr.md), and [provider evidence](../appendix/provider-native-evidence.md).
