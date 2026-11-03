# Deployment governance

**Status: design draft; not implemented.** Gates below are proposed requirements, not deployed controls or successful test results. Accountability is consolidated in the [ownership model](ownership-model.md); the paper's [threat-control matrix](../architecture-paper/06-threat-control-model.md) is authoritative. Source IDs reference the currently empty [provider-native evidence register](../appendix/provider-native-evidence.md), without claiming independent verification.

## Delivery and promotion contract

Use AWS, Terraform, GitHub Actions and EKS/Helm across exactly three delivery layers:

1. **Foundation:** accounts, VPC/network, EKS nodes/controllers and the **platform Kubernetes/Kong release subpipeline**, including lifecycle, Gateway policy and baseline plugins.
2. **Application infrastructure:** Terraform-managed Aurora, SQS, S3, IAM, secret metadata and alarms.
3. **Application code:** immutable images, Helm workloads/services, approved namespace-scoped HTTPRoutes and database migration logic.

The foundation platform-release subpipeline is not a fourth layer. See [deployment pipelines](../diagrams/deployment-pipelines.md) and [deployment architecture](../diagrams/deployment-architecture.md). Each layer publishes versioned contracts to its consumers; downstream changes must pin compatible versions rather than silently adopting upstream outputs.

P is Malaysia `ap-southeast-5`; R is Singapore `ap-southeast-1`. `entity-a-prod` and `entity-b-prod` remain separate workload accounts, each with separate EKS clusters in P and R. Live Aurora recovery remains in the workload-account topology; separate entity recovery accounts are for immutable backups/cleanrooms only. Shared security/log/network/tooling accounts retain explicit residency boundaries. Cross-border approval is user-confirmed granted, with evidence reference pending and no regulator verification.

| Promotion | Required immutable record | Gate and execution |
|---|---|---|
| Foundation AWS infrastructure | Commit, pinned Terraform/provider versions, dependency lock file, reviewed plan digest and target state/account/region | Platform approves foundation delivery; Network/Security clear applicable controls. Apply that exact plan through the scoped foundation role after drift/revalidation checks. |
| Foundation platform-release subpipeline | Controller/Kong chart digests, versioned values/policies and compatibility evidence | Platform approves controller, CRD, Gateway and Kong lifecycle changes; stage/test before production. Helm owns these workloads. |
| Application infrastructure | Reviewed Terraform plan digest, target state, resource/identity contract version and data-impact review | Application approves delivery with Data/Security clearance as applicable; use the scoped infrastructure role and exact approved plan after revalidation. |
| Application code | ECR image digest, chart digest, signature/provenance, scan results, configuration digest, migration version and compatibility evidence | Application provides readiness evidence; OPS approves the production window and executes canary/rollback gates, with BUS clearance for material service/data risk. |

For every promotion, a manifest binds the artifacts to layer, entity, environment, account, region, commit, configuration, dependency contracts, approvals, evidence and rollback target. Record execution identity, timestamps, observed result and exceptions. Build images/charts **once** and promote the same digest through environments and into approved regional registries; verify destination digests and signatures, never rebuild or trust mutable tags. Target-specific configuration is separately versioned and approved. Do not promote raw secrets.

## Identity and execution isolation

- GitHub Actions assumes AWS STS roles using OIDC, with exact `aud` and `sub` matching. The standard AWS audience is `sts.amazonaws.com`. Trust the actual subject emitted by the configured GitHub organization/repository, including customization and escaping rules ([S7](../appendix/provider-native-evidence.md)).
- With a GitHub environment, the subject pattern is `repo:ORG/REPO:environment:ENV`; without an environment, a branch subject is `repo:ORG/REPO:ref:refs/heads/BRANCH`. These are templates, not deployable wildcard policies: substitute exact approved values and check the resulting token claims.
- An environment subject **does not bind the branch**. Enforce protected-environment deployment branches/tags and reviewers, branch protection, and reviewed workflow changes. Separate authors from production approvers; pin third-party actions to reviewed commit SHAs and give jobs minimum token permissions.
- Use separate layer + entity + environment roles with explicit account/region scope; controller and workload roles are separate from deployment roles. Constrain EKS RBAC so application deployers cannot administer Kong, global plugins, GatewayClass/Gateway or other namespaces.
- Use isolated, ephemeral, connected deployment runners for privileged access. Do not run untrusted pull-request code on them. Separate build/test runners from privileged deployment execution; restrict network egress, credentials and artifact access, and destroy runner instances after use.
- Log STS assumptions, approvals and deployment actions to controlled security/log-account destinations with residency policy. Independently audit emergency identities; OIDC is not the only emergency access mechanism.

## Terraform and controller controls

Use S3 remote state with versioning, KMS encryption and **native S3 locking** (`use_lockfile = true` with a compatible Terraform version). Split backend keys and permissions by entity, environment and lifecycle; scope lock access with state access. Do not share a broad state-writer identity across layers ([S8](../appendix/provider-native-evidence.md)).

For foundation and application-infrastructure changes:

1. Validate the configuration using the repository's approved checks; pin tool/provider versions, inspect IAM/network/data impact and generate a saved plan against the intended backend.
2. Review the plan, policy results, target identity and manifest digest. Encrypt and restrict plans because they can contain sensitive information. Require explicit Data review for schema/storage effects and protected approval for replacement or destruction.
3. Immediately before apply, verify artifact integrity, target identity, backend state and drift. Hold the state lock during apply and serialize deployments to the target. If drift, state changes, expiry or revalidation invalidates the approved plan, generate a new plan and obtain new approval; never substitute an unreviewed fresh plan at apply time.
4. Apply the exact approved saved plan, record outputs without secrets, inspect post-apply drift/health, and publish only the approved contract. No routine console mutation, unlocked apply or automatic production destroy. Emergency deviations require scoped authorization, audit and subsequent reconciliation into IaC.

Terraform provisions AWS resources; Helm manages Kubernetes workloads. AWS Load Balancer Controller owns the ALB fronting Kong and its managed resources; KIC reconciles application routes into Kong. No duplicate AWS declarations, Terraform management of Helm-owned workloads, or competing routing controllers. Ownership handoffs must identify the previous/new reconciler, relinquish the old binding without deletion, and validate reconciliation before delivery resumes ([S2](../appendix/provider-native-evidence.md), [S10](../appendix/provider-native-evidence.md)).

Manage secret **metadata**, access policy and references in Terraform, not raw values in configuration, plans or state. Populate/rotate values through a separately controlled secret process in each region; do not assume primary-region secret values or keys are accessible during recovery.

## Application and gateway release gates

Before production, verify signatures/provenance, vulnerability scan policy, workload identity, dependency compatibility and test evidence. Applications expose ClusterIP services behind ALB + WAF → Kong; private hybrid access uses an internal ALB. Security-group, network-policy and admission checks must reject public NodePort/LoadBalancer bypass. Verify service TLS/mTLS, application authorization and payment idempotency.

Platform owns GatewayClass/Gateway, `allowedRoutes`, baseline plugin/auth controls and private Admin API access. Applications deploy only approved namespaced HTTPRoutes under that contract, with no global plugin/admin rights. The proposed gateway is self-hosted DB-less Kong with KIC, per entity/region, at least three replicas across AZs; no Amazon API Gateway, Konnect or external control plane.

Recover DB-less configuration from versioned Git/Kubernetes desired state, not a configuration database or `decK sync`. Gate platform releases on plugin/version compatibility, licensing, authentication and rate-limit assessment; these remain pending. A local counter is not a globally enforced rate limit ([S9](../appendix/provider-native-evidence.md), [S10](../appendix/provider-native-evidence.md)).

Use a staged canary with preapproved numerical SLO thresholds and observation windows for availability, latency, error rate, payment correctness and duplicate/uncertain submissions. Thresholds and automatic stop/rollback criteria must be defined before release, not inferred during an incident. OPS records the go/no-go outcome.

Keep database changes backward compatible using expand/contract: expand first, run a controlled migration/backfill with Data review, deploy compatible code, and contract only after the rollback window and old-version retirement. Application rollback selects the prior approved image/chart/configuration digests; it does not reverse committed payments or assume a destructive schema migration can be rolled back. Use a reviewed forward fix or data-recovery procedure where rollback compatibility is lost.

## Recovery and GitHub-independent execution

Preprovision and exercise EKS, Kong/controllers/routes, network paths, keys, regional secrets, images/charts and Aurora in R for each entity. Validate diverse Direct Connect paths and VPN fallback to both countries, TLS/mTLS or engineered IPsec (Direct Connect alone is not encryption), TGW entity segmentation and symmetric Network Firewall routing with per-AZ endpoints. Only routed traffic is inspected; TLS decryption is not automatic ([S13](../appendix/provider-native-evidence.md), [S14](../appendix/provider-native-evidence.md)); see [hybrid connectivity](../diagrams/hybrid-connectivity.md).

Aurora uses multi-AZ storage and a single writer with readers in the active region; R is a read-only global secondary until promotion. There is one active global write region. Global Database P → R replication is asynchronous: near-zero is not guaranteed zero regional RPO. The supplied matrix lists Aurora PostgreSQL Global Database availability in both regions, but engine/version, features and capacity still need validation ([S4](../appendix/provider-native-evidence.md), [S5](../appendix/provider-native-evidence.md), [S6](../appendix/provider-native-evidence.md)).

Regional recovery sequence:

1. OPS declares the incident, captures disruption time, assesses dependencies and obtains BUS recovery authorization with Data/Security input.
2. Fence **old payment submitters and the old database writer before any promotion or traffic switch**. Require positive evidence from the preapproved fencing mechanism; DNS redirection is not fencing. If fencing is unprovable, halt promotion and escalate rather than accept split brain.
3. DATA assesses replication position and potential loss; APP/DATA identify uncertain commits and external submissions. BUS approves the reconciliation/hold strategy before safe critical journeys resume. Do not claim zero regional loss.
4. Promote the recovery database only after the fencing gate. Verify writer uniqueness, regional identities/secrets and service readiness while external submitters remain fenced.
5. Reconcile surviving ledger/outbox records and query external processors for uncertain outcomes before retrying with idempotency keys. SQS is region-local and is **not replicated**; replay only from surviving durable records, explicitly recording gaps ([S12](../appendix/provider-native-evidence.md)). After reconciliation/hold gates and critical-journey validation, switch approved traffic and enable only safe submitters under BUS authorization.
6. Record restored critical-journey evidence, actual RTO/RPO and reconciliation exceptions. Failback requires a separate approved resynchronization/fencing plan; it is not automatic DNS reversal.

The draft RTO is **≤30 minutes from disruption to safe critical journeys**, not merely database promotion; it is unmeasured. Zero loss is expected for an AZ failure under regional HA, not guaranteed across regional failure. Cyber recovery uses entity recovery-account immutable backups/cleanrooms, with security integrity clearance and separate BUS resumption approval. Validate retention, Vault Lock behavior, restore keys and cleanroom isolation; its RTO is separate and unmeasured ([S11](../appendix/provider-native-evidence.md)). See [DR architecture](../diagrams/dr-architecture.md).

A GitHub outage must not prevent predeployed emergency recovery. Before readiness sign-off, maintain independently approved connected emergency runner access, signed/digested artifacts, promotion manifests and versioned runbooks available **without GitHub**, including required scripts/tools and regional registry access. Use short-lived, permission-controlled emergency identities independent of GitHub OIDC, segregated approvals and tamper-resistant audit logs. Exercise recovery with GitHub inaccessible; do not rely on downloading workflows, actions or runbooks from GitHub during the event. Reconcile emergency changes and evidence when normal delivery returns.

## Evidence required before implementation sign-off

Record named role holders, approved cross-border evidence reference and residency rules; validated provider/engine support; actual OIDC claims and environment restrictions; resource/controller ownership inventory; approved promotion/rollback evidence; Kong compatibility/licensing/rate-limit decisions; and measured AZ, regional, cyber and GitHub-outage exercises. Populate the evidence register through its owner. Until these gates are evidenced, this document remains a design proposal rather than an operational assurance claim.
