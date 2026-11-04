# Ownership model

This is the proposed accountability model. Product sources are in the [evidence register](../appendix/provider-native-evidence.md).

## Scope and boundaries

- **AWS only:** Malaysia `ap-southeast-5` is primary (P); Singapore `ap-southeast-1` is recovery (R).
- `entity-a-prod` and `entity-b-prod` are separate workload accounts, each with a separate EKS cluster in each region. Separate entity recovery accounts hold immutable backups and clean-room recovery, **not** the live Aurora Global Database topology.
- Security tooling, log archive, network and platform tooling accounts are separate, with explicit residency controls for logs, backups, state, artifacts and administrative access. Foundation owns account guardrails; Security owns policy and evidence requirements ([S1](../appendix/provider-native-evidence.md)).
- The [context](../diagrams/context-diagram.md), [logical architecture](../diagrams/logical-architecture.md) and [deployment architecture](../diagrams/deployment-architecture.md) describe these boundaries. The paper's [threat-control matrix](../architecture-paper/06-threat-control-model.md) remains authoritative; this document does not duplicate it.

## Exactly three delivery layers

| Layer | Scope and accountable owner | Published artifacts and handoff |
|---|---|---|
| 1. Foundation | Platform: accounts, VPC/network integration, EKS nodes/controllers, and platform Kubernetes/Kong releases, lifecycle and policies. Network engineers own network implementation within this layer; Security owns guardrail policy. | Approved Terraform plans/state outputs and versioned platform Helm/configuration releases; publish cluster, network, Gateway and policy contracts to layers 2 and 3. |
| 2. Application infrastructure | Application: Terraform for Aurora, SQS, S3, IAM, secret metadata and alarms. Data engineers implement database topology, backup and recovery configuration; Security reviews access. | Approved Terraform plans and versioned non-secret endpoint, identity and resource contracts consumed by layer 3. |
| 3. Application code | Application: immutable images, Helm workloads/services, approved namespaced HTTPRoutes and database migration logic. Data reviews migration safety; Operations controls production release execution. | Image and chart digests, signatures, scans, provenance, migration compatibility evidence and an approved promotion manifest. |

The **platform Kubernetes/Kong release pipeline is a subpipeline of foundation**, never a fourth layer. Team responsibilities within a layer do not create extra delivery layers. Promotions follow [deployment governance](deployment-governance.md) and the [pipeline diagram](../diagrams/deployment-pipelines.md).

Product/application teams own end-to-end application SLOs, including the impact of their dependencies. Platform owns published EKS/Kong service objectives and platform incident response; delegating release execution to Operations does not transfer product SLO accountability.

### Single resource owner

Terraform provisions AWS infrastructure; Helm owns Kubernetes workloads. Keep Terraform state split by entity, environment and lifecycle, with one state/resource owner and no duplicate AWS declarations. Terraform must not separately manage Helm-owned workloads. Before any ownership transfer, record resource IDs, relinquish the previous reconciler/state binding without destroying the resource, establish the new owner, and prove a clean plan/reconciliation.

The AWS Load Balancer Controller owns the ALB fronting Kong and its controller-managed AWS resources; Terraform owns surrounding network/security foundations, not duplicate ALBs or controller-created rules. Foundation installs/configures that controller. KIC owns the application-routing reconciliation into Kong; no two controllers may own the same routing object. Explicitly record any IaC-to-controller handoff and rollback procedure ([S2](../appendix/provider-native-evidence.md), [S10](../appendix/provider-native-evidence.md)).

Platform provides workload identity integration; Application defines least-privilege workload IAM in layer 2. Security reviews trust boundaries; credentials are not embedded in images or charts ([S3](../appendix/provider-native-evidence.md)).

## Platform product and application contract

Self-hosted Kong is a Platform-owned product; application teams are its consumers (not automatically Kong Consumer objects). Platform owns GatewayClass, Gateway, `allowedRoutes`, baseline authentication/plugins, Kong upgrades, the private Admin API and admission policy. Applications submit approved namespace-scoped HTTPRoutes only and remain responsible for TLS/mTLS integration, business authorization and idempotency. Full contract: [Kong as a platform product](../architecture-paper/03-target-architecture.md) and [logical architecture](../diagrams/logical-architecture.md) ([S9](../appendix/provider-native-evidence.md), [S10](../appendix/provider-native-evidence.md)).

## Consolidated RACI

Roles: **SEC** Security/compliance; **NET** Network; **PLT** Platform/foundation; **APP** Application/product engineering; **DATA** Database/data engineering; **OPS** Operations/incident and release management; **BUS** Business/service risk owner. Each role must have named primary/deputy contacts per entity before implementation. OPS and BUS are separate responsibilities, not interchangeable approvals.

**A** = sole accountable role; **R** = executes; **C** = consulted; **I** = informed; **A/R** = accountable and executing. Each row has exactly one A, including A/R. Consulted control owners can withhold mandatory gate clearance; accountability does not override policy.

| Decision or activity | SEC | NET | PLT | APP | DATA | OPS | BUS |
|---|---|---|---|---|---|---|---|
| Account guardrails, residency policy and evidence custody | A/R | C | R | I | C | C | C |
| Cross-border evidence acceptance and residual business risk | R | C | C | I | C | C | A |
| Foundation delivery and account/EKS lifecycle | C | R | A/R | C | I | R | I |
| Hybrid connectivity, segmentation and firewall paths | C | A/R | R | C | I | R | I |
| Foundation Kubernetes/Kong subpipeline and route guardrails | C | C | A/R | C | I | R | I |
| Application-infrastructure delivery and resource contracts | C | C | R | A/R | R | C | I |
| Database topology, backups and data recovery readiness | C | I | C | R | A/R | R | C |
| Code, HTTPRoutes, authorization and idempotency | C | I | C | A/R | C | R | I |
| Migration logic and expand/contract compatibility | I | I | C | A/R | R | C | I |
| CI identity, artifact trust and privileged-access policy | A/R | I | R | R | C | R | I |
| Production promotion, canary and operational rollback | C | C | R | R | C | A/R | C |
| Regional recovery authorization and uncertain-payment gate | C | C | R | R | R | R | A |
| Fence, promote, reconcile and switch recovery traffic | C | R | R | R | R | A/R | C |
| Cyber clean-room integrity clearance | A/R | C | R | R | R | R | C |
| Cyber business-service resumption authorization | R | C | R | R | R | R | A |
| Exercises, measured recovery evidence and runbook currency | C | R | R | R | R | A/R | C |

## Data, network and recovery duties

- **DATA** owns Aurora topology, backups and recovery readiness; the active region has one writer and R is a read-only global secondary until promoted ([S4](../appendix/provider-native-evidence.md), [S5](../appendix/provider-native-evidence.md), [S6](../appendix/provider-native-evidence.md)). See [data and DR](../architecture-paper/05-data-and-dr.md).
- **APP** owns region-local SQS handling, replay from the surviving ledger/outbox and idempotent external submissions ([S12](../appendix/provider-native-evidence.md)).
- **NET** owns diverse Direct Connect with VPN fallback to both countries, TGW segmentation and symmetric Network Firewall paths ([S13](../appendix/provider-native-evidence.md), [S14](../appendix/provider-native-evidence.md)). See [hybrid connectivity](../diagrams/hybrid-connectivity.md).
- **OPS** maintains recovery readiness and executes fencing, promotion and traffic switching; **BUS** owns the uncertain-commit decision gate. Neither may bypass fencing. See [DR architecture](../diagrams/dr-architecture.md), the recovery gates in [deployment governance](deployment-governance.md) and, for cyber recovery, [S11](../appendix/provider-native-evidence.md).
