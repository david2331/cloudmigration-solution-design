# Target architecture

**Selected cloud: AWS. Task 2 (20%). Terraform, GitHub Actions, EKS/Helm and platform-owned self-hosted Kong are confirmed directions.**

## Multi-account and geographical boundaries

```text
AWS Organization
  Management account (no payment workloads)
  Security OU
    Security tooling account
    Residency-controlled log archive account(s)
  Infrastructure OU
    Network account(s)
    Platform tooling account
  Production OU
    Entity A OU
      entity-a-prod       (Malaysia primary + Singapore regional DR)
      entity-a-recovery   (isolated backups + clean-room recovery)
    Entity B OU
      entity-b-prod
      entity-b-recovery
  Nonproduction OU
    entity-a-nonprod
    entity-b-nonprod
  Sandbox OU              (no regulated production data)
```

`entity-a`/`entity-b` are placeholders for legal entities, not countries. Each production account hosts its own EKS cluster and application data in **P: Malaysia `ap-southeast-5`** and a separate regional recovery deployment in **R: Singapore `ap-southeast-1`**. Regional DR shares the entity production account; cyber-recovery custody is separately isolated. Cross-border approval is user-confirmed; its record and covered data types must be attached.

Provision via AWS Control Tower/Organizations and approved Terraform modules. Restrict regions and dangerous actions with SCPs, retaining narrow documented global-service exceptions. Separate IAM, resource policies, keys and routing enforce entity boundaries. Central security may aggregate permitted findings, not automatically every sensitive payload.

See the [context](../diagrams/context-diagram.md), [logical](../diagrams/logical-architecture.md), and [mandatory deployment diagrams](../diagrams/deployment-architecture.md).

## Three delivery layers

| Layer | Managed resources | Owner and release |
|---|---|---|
| Foundation infrastructure | Accounts, networks, inspection, EKS, managed nodes, cluster add-ons, Kong/KIC, baseline policies, audit | Platform; Terraform foundation pipeline plus platform Helm subpipeline |
| Application infrastructure | Aurora, SQS, S3, application IAM, secrets metadata, backup configuration, dashboards/alarms | Application teams using approved Terraform modules; data/security review |
| Application code | Business services, tests, images, Helm charts, approved HTTPRoutes, migration logic | Application teams; GitHub Actions build and promotion |

Terraform states are split by entity, environment, region where appropriate, and lifecycle. Organization-global and cross-region resources have a single explicit state owner rather than duplicate regional definitions. Use encrypted, versioned S3 backends with native lockfiles supported by the pinned Terraform version [S8]. Bootstrap backends through a restricted one-time process, then bring them under a dedicated foundation lifecycle.

Treat state and saved plans as sensitive. Product pipelines consume approved non-secret outputs, not unrestricted foundation state. Restore replicated state only under a fenced recovery procedure; never permit simultaneous writers against independently restored backends.

Helm owns Kubernetes resources. Controller-created AWS resources are an explicit exception to direct Terraform provisioning: the AWS Load Balancer Controller owns its ALBs and associated generated resources. Do not declare those again in Terraform.

## Kong as a platform product

The proposed gateway implementation is **self-hosted DB-less Kong with KIC**, independently deployed per entity and region. This avoids a Kong configuration database but requires DB-less-compatible plugins and tested configuration recovery [S9, S10]. No Konnect or external Kong control plane is proposed.

| Capability | Platform responsibility | Application responsibility |
|---|---|---|
| Gateway lifecycle | Helm release, supported versions, KIC, capacity, certificates, availability and incident response | Respect supported API contracts |
| Routing | Gateway/GatewayClass and namespace admission policy; approved domains and `allowedRoutes` | Namespace-scoped HTTPRoutes to authorized services |
| Security policies | Approved authentication integration, plugin allowlist, default limits, log redaction | Business authorization, tenant/entity checks, idempotency |
| Administration | Private Admin API, scoped privileged access and audit | No Admin API or unrestricted global-plugin access |
| Change control | Guardrail validation and platform-wide policy approval | Versioned API contracts and route requests through GitHub Actions |

Application teams being "consumers" describes an operating model; it does not automatically mean creating Kong Consumer credential objects for each team.

North-south path: **Route 53 -> ALB with WAF -> Kong -> ClusterIP application service**. Hybrid callers use a private internal ALB, also forwarding through Kong. AWS Load Balancer Controller manages the dedicated Kong-fronting ingress; KIC handles application routing. They must not reconcile the same routing object.

Only approved platform ingress may expose workloads. Security groups, network policies and admission restrictions prevent bypass through public Services, NodePorts or alternate ingresses. Kong-to-application traffic uses authenticated TLS/mTLS as required; TLS termination and certificate validation on every hop are explicit design items, not assumed from "HTTPS".

Platform-owned gateway replicas are spread across three AZs with tested spare capacity. DB-less configuration is not automatically shared between nodes: KIC must converge each instance, and readiness must exclude unconfigured pods. Git stores approved desired state; Kubernetes is KIC's runtime source. Restore pinned manifests/configuration independently in Singapore. No `decK sync` is used for DB-less configuration.

Authentication plugin edition/licensing, compatibility and failure behavior are review gates. Per-node rate-limit counters are not a global quota. A globally enforced counter would introduce a separately designed state dependency. Payment authorization and financial limits must not rely exclusively on gateway counters.

## Hybrid networking and security inspection

Use diverse Direct Connect circuits/locations, independently routed Site-to-Site VPN fallback, and tested on-premises reachability to both countries. DX is not encrypted by default; use application TLS/mTLS and an engineered IPsec option when needed [S13].

Transit Gateway route tables isolate entities, on-premises destinations and shared services. Network Firewall endpoints span AZs; stateful inspection needs symmetric paths, applicable appliance-mode configuration and no unapproved bypass routes [S14]. It inspects routed flows only; encrypted traffic is not automatically decrypted. Local VPC traffic needs its own controls.

Use private subnets, planned address capacity, Route 53 Resolver integration and appropriate VPC endpoints. Restrict egress and endpoint policies. Size VPN fallback for prioritized payment journeys rather than assume it matches DX bandwidth. See [hybrid connectivity](../diagrams/hybrid-connectivity.md).

## Identity, data and integration

Corporate federation through IAM Identity Center provides short-lived human roles; EKS access entries/RBAC restrict cluster access. Separate tightly audited emergency access covers identity-provider outages. EKS Pod Identity maps application service accounts to least-privilege IAM roles; constrain IMDS to prevent node-role credential access [S3].

Use per-entity Aurora PostgreSQL with writer/readers across AZs, SQS for asynchronous work and S3 for approved objects. Secrets Manager and KMS are regionally provisioned with deliberate replication/copy policies. Never store credentials in Helm values or GitHub logs. Aurora's ledger transaction plus outbox is authoritative; queues are not the ledger.

Use versioned API/event contracts, timeouts, backpressure and bounded retries. Circuit breakers may protect failing screening/core dependencies, but must not silently skip mandatory fraud or sanctions checks. See [data and DR](05-data-and-dr.md).

## Observability and capacity

CloudWatch plus OpenTelemetry provides redacted logs, metrics and traces. Optional managed Prometheus/Grafana requires regional and cost review; it is not a hidden prerequisite. Enable CloudTrail, EKS audit logs, Config, GuardDuty and Security Hub capabilities as available and approved.

Monitor payment outcomes and correctness, gateway errors/latency, route convergence, certificate expiry, queue age/DLQs, Aurora failover/replication lag, saturation and reconciliation gaps. Platform owns gateway/cluster indicators; products own end-to-end journey indicators.

Use topology spread, disruption budgets, readiness, graceful drain and enough surviving compute/database capacity for AZ loss. Protect critical baseline capacity from Spot interruption; scale auxiliary work separately. Connection budgets and backpressure protect the database during pod scaling.

## Delivery and recovery independence

GitHub Actions uses OIDC to scoped AWS STS roles, with audience/subject conditions matching the actual repository subject format and protected environments [S7]. Separate roles by layer, entity and environment; EKS authorization further narrows access. Connected ephemeral deployment runners do not execute untrusted PR code.

Build once, scan, produce SBOM/provenance, sign, and promote the same image/chart digests. Use staged rollout, synthetic checks and error-budget gates. Database changes follow expand-and-contract; Helm rollback cannot undo committed payments.

Singapore artifacts, routes, certificates, secrets and network paths are prepositioned. GitHub availability is not a payment-path or emergency-failover dependency. See [deployment governance](../governance/deployment-governance.md), [pipeline diagram](../diagrams/deployment-pipelines.md), and [cost model](../appendix/cost-considerations.md).

Provider behavior and qualifications: [S1-S14](../appendix/provider-native-evidence.md).
