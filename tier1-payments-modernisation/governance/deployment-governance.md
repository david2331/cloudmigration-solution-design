# Deployment governance

Gates below are proposed requirements. Accountability is in the [ownership model](ownership-model.md); the paper's [threat-control matrix](../architecture-paper/06-threat-control-model.md) is authoritative. Product sources are in the [evidence register](../appendix/provider-native-evidence.md).

## Delivery and promotion contract

Use AWS, Terraform, GitHub Actions and EKS/Helm across exactly three delivery layers:

1. **Foundation:** accounts, VPC/network, EKS nodes/controllers and the **platform Kubernetes/Kong release subpipeline**, including lifecycle, Gateway policy and baseline plugins.
2. **Application infrastructure:** Terraform-managed Aurora, SQS, S3, IAM, secret metadata and alarms.
3. **Application code:** immutable images, Helm workloads/services, approved namespace-scoped HTTPRoutes and database migration logic.

The foundation platform-release subpipeline is not a fourth layer. See [deployment pipelines](../diagrams/deployment-pipelines.md) and [deployment architecture](../diagrams/deployment-architecture.md). Each layer publishes versioned contracts to its consumers; downstream changes must pin compatible versions rather than silently adopting upstream outputs.

P is Malaysia `ap-southeast-5`; R is Singapore `ap-southeast-1`. `entity-a-prod` and `entity-b-prod` remain separate workload accounts, each with separate EKS clusters in P and R. Live Aurora recovery remains in the workload-account topology; separate entity recovery accounts are for immutable backups/clean-room environments only. Shared security tooling, log archive, network and platform tooling accounts retain explicit residency boundaries.

| Promotion | Required immutable record | Gate and execution |
|---|---|---|
| Foundation AWS infrastructure | Commit, pinned Terraform/provider versions, dependency lock file, reviewed plan digest and target state/account/region | Platform approves foundation delivery; Network/Security clear applicable controls. Apply that exact plan through the scoped foundation role after drift/revalidation checks. |
| Foundation platform-release subpipeline | Controller/Kong chart digests, versioned values/policies and compatibility evidence | Platform approves controller, CRD, Gateway and Kong lifecycle changes; stage/test before production. Helm owns these workloads. |
| Application infrastructure | Reviewed Terraform plan digest, target state, resource/identity contract version and data-impact review | Application approves delivery with Data/Security clearance as applicable; use the scoped infrastructure role and exact approved plan after revalidation. |
| Application code | ECR image digest, chart digest, signature/provenance, scan results, configuration digest, migration version and compatibility evidence | Application provides readiness evidence; OPS approves the production window and executes canary/rollback gates, with BUS clearance for material service/data risk. |

For every promotion, a manifest binds the artifacts to layer, entity, environment, account, region, commit, configuration, dependency contracts, approvals, evidence and rollback target. Record execution identity, timestamps, observed result and exceptions. Build images/charts **once** and promote the same digest through environments and into approved regional registries; verify destination digests and signatures, never rebuild or trust mutable tags. Target-specific configuration is separately versioned and approved. Do not promote raw secrets.

## Identity and execution isolation

- GitHub Actions assumes AWS STS roles using OIDC, with exact `aud` and `sub` matching. The standard AWS audience is `sts.amazonaws.com`. Trust the actual subject emitted by the configured GitHub organization/repository, including customization and escaping rules ([S7](../appendix/provider-native-evidence.md)).
- Legacy GitHub subject examples are `repo:ORG/REPO:environment:ENV` for an environment or `repo:ORG/REPO:ref:refs/heads/BRANCH` for a branch. Repositories using immutable subject IDs include owner/repository IDs in those segments. These are explanatory examples, not deployable wildcard policies: use the actual configured subject format and validate token claims before creating trust.
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

Before production, verify signatures/provenance, vulnerability scan policy, workload identity, dependency compatibility and test evidence. Applications expose ClusterIP services behind ALB + WAF -> Kong; private hybrid access uses an internal ALB. Security-group, network-policy and admission checks must reject public NodePort/LoadBalancer bypass. Verify service TLS/mTLS, application authorization and payment idempotency.

Platform owns GatewayClass/Gateway, `allowedRoutes`, baseline plugin/auth controls and private Admin API access. Applications deploy only approved namespaced HTTPRoutes under that contract, with no global plugin/admin rights. The proposed gateway is self-hosted DB-less Kong with KIC, per entity/region, at least three replicas across AZs; no Amazon API Gateway, Konnect or external control plane.

Recover DB-less configuration from versioned Git/Kubernetes desired state, not a configuration database or `decK sync`. Gate platform releases on plugin/version compatibility, licensing, authentication and rate-limit assessment; these remain pending. A local counter is not a globally enforced rate limit ([S9](../appendix/provider-native-evidence.md), [S10](../appendix/provider-native-evidence.md)).

Use a staged canary with preapproved numerical SLO thresholds and observation windows for availability, latency, error rate, payment correctness and duplicate/uncertain submissions. Thresholds and automatic stop/rollback criteria must be defined before release, not inferred during an incident. OPS records the go/no-go outcome.

Keep database changes backward compatible using expand/contract: expand first, run a controlled migration/backfill with Data review, deploy compatible code, and contract only after the rollback window and old-version retirement. Application rollback selects the prior approved image/chart/configuration digests; it does not reverse committed payments or assume a destructive schema migration can be rolled back. Use a reviewed forward fix or data-recovery procedure where rollback compatibility is lost.

## Recovery and GitHub-independent execution

Regional recovery follows the ordered sequence in [DR architecture](../diagrams/dr-architecture.md) and the fencing rules in [data and DR](../architecture-paper/05-data-and-dr.md). The delivery-side gates are:

- Preprovision and exercise EKS, Kong/controllers/routes, network paths, keys, regional secrets, images/charts and Aurora in R for each entity.
- Promote the recovery database only after the fencing gate; enable submitters only under BUS authorization. Failback follows a separate approved plan, not a DNS reversal.
- Cyber recovery uses entity recovery-account backups, with security integrity clearance and separate BUS resumption approval.

A GitHub outage must not prevent predeployed emergency recovery. Before readiness sign-off, maintain independently approved connected emergency runner access, signed/digested artifacts, promotion manifests and versioned runbooks available **without GitHub**, including required scripts/tools and regional registry access. Use short-lived, permission-controlled emergency identities independent of GitHub OIDC, segregated approvals and tamper-resistant audit logs. Exercise recovery with GitHub inaccessible; do not rely on downloading workflows, actions or runbooks from GitHub during the event. Reconcile emergency changes and evidence when normal delivery returns.

## Evidence required before implementation sign-off

Record named role holders, approved cross-border evidence reference and residency rules; validated provider/engine support; actual OIDC claims and environment restrictions; resource/controller ownership inventory; approved promotion/rollback evidence; Kong compatibility/licensing/rate-limit decisions; and measured AZ, regional, cyber and GitHub-outage exercises. Attach bank-specific evidence through its owner. Until these gates are evidenced, this document remains a design proposal rather than an operational assurance claim.
