# Logical architecture

**Status: design draft; not implemented.** This pattern is instantiated independently for entity A and entity B, in Malaysia P and Singapore R. R is preprovisioned but payment processing remains fenced until approved recovery activation.

```mermaid
flowchart TB
  internet["Internet channels"]
  onprem["On-premises consumers via DX / VPN / TGW"]
  partners["Payment partners"]

  subgraph workload["One entity workload account  -  one regional instance"]
    subgraph ingress["VPC ingress boundary  -  public and private entry points"]
      waf["AWS WAF web ACL"]
      alb["Internet-facing Application Load Balancer<br/>AWS Load Balancer Controller owned"]
      ialb["Private internal ALB<br/>AWS Load Balancer Controller owned"]
    end
    subgraph eks["Private EKS data plane  -  AZ-a / AZ-b / AZ-c"]
      subgraph platform["Platform namespace / privileged trust boundary"]
        kong["Self-hosted DB-less Kong<br/>At least 3 replicas spread across AZs"]
        kic["Kong Ingress Controller (KIC)"]
        policy["GatewayClass / Gateway / allowedRoutes<br/>Baseline authentication and plugin policy"]
        lbc["AWS Load Balancer Controller"]
      end
      subgraph app["Application namespaces  -  scoped RBAC"]
        route["Approved namespaced HTTPRoutes"]
        svc["ClusterIP services -> payment pods<br/>Authorization + idempotency"]
        workers["Outbox publisher / queue workers<br/>Fenced external submitters"]
      end
    end
    subgraph data["Private data / AWS service boundary"]
      aurora["Aurora PostgreSQL<br/>Single regional writer + readers<br/>Regional storage replicated across AZs"]
      sqs["Regional Amazon SQS + DLQ"]
      s3["Private Amazon S3 + SSE-KMS"]
      secrets["AWS Secrets Manager / KMS"]
      identity["EKS Pod Identity -> scoped IAM"]
    end
    egress["Controlled egress<br/>Routed AWS Network Firewall paths"]
    observability["CloudWatch metrics / alarms / redacted logs"]
  end

  internet -->|"HTTPS; WAF attached to public ALB"| waf
  waf --> alb
  onprem -->|"Private HTTPS / approved identity"| ialb
  alb -->|"Restricted target SG; TLS"| kong
  ialb -->|"Restricted target SG; TLS"| kong
  kong -->|"TLS / mTLS; no direct public service"| svc
  lbc -.->|"Reconciles dedicated Kong-fronting ALBs"| alb
  lbc -.->|"Reconciles dedicated Kong-fronting ALBs"| ialb
  policy -.-> kic
  route -.->|"Namespace and route admission checks"| kic
  kic -.->|"Private Admin API; controlled credentials"| kong
  svc -->|"Atomic ledger + outbox transaction"| aurora
  workers -->|"Read / mark durable outbox"| aurora
  workers -->|"Publish / retry"| sqs
  sqs -->|"At-least-once delivery; deduplicate"| workers
  workers -->|"Idempotency key; reconcile uncertain outcome"| egress
  egress -->|"TLS / mTLS"| partners
  svc --> s3
  identity -.->|"Service-account-specific permissions"| svc
  identity -.-> workers
  svc -->|"Runtime access, not embedded values"| secrets
  kong --> observability
  workers --> observability
```

## Controller and security contracts

| Boundary | Contract |
| --- | --- |
| Entry | AWS Load Balancer Controller reconciles the ALBs fronting Kong through dedicated platform-owned resources. KIC reconciles application HTTPRoutes to Kong. The controllers must not both own the same routing resource; classes, RBAC and admission enforce separation. |
| Kong administration | Platform alone has privileged access. KIC reaches a private Admin API; no public admin endpoint or application-team admin credentials. Kubernetes desired state and reviewed Git manifests are the versioned configuration source. DB-less means **no Kong configuration database and no decK sync**. |
| Route delegation | Platform owns GatewayClass, Gateway, `allowedRoutes`, approved cross-namespace references and baseline authentication/plugin controls. Apps receive namespace-scoped HTTPRoute permissions only; admission prevents host/path hijacking and unauthorized policy overrides. |
| Bypass prevention | Only approved ingress can reach Kong; only Kong and approved internal callers can reach payment services. Restricted security groups, Kubernetes NetworkPolicy and admission prohibit arbitrary public LoadBalancer/NodePort services and direct application ingress. ClusterIP alone is not a security boundary. |
| Identity | Evaluate Pod Identity support and least-privilege associations per service account. Kong authentication does not replace application authorization, tenant/entity checks or payment idempotency. TLS/mTLS protects hops to services; certificate rotation is platform-integrated. |
| Kong acceptance | DB-less/KIC versions, Gateway API support, plugin compatibility, licensing, authentication dependencies and rate-limit semantics require assessment. Local per-replica counters are **not** a global limit; any distributed counter dependency requires explicit design, availability and residency approval. No external Kong control plane. |

## Payment and data semantics

- Commit ledger changes and an outbox record atomically in Aurora. SQS is region-local and not transactionally coupled to that commit; publishers retry and consumers deduplicate. DLQ redrive is controlled and observable.
- Across regions, Aurora Global Database replicates P -> R asynchronously. Recovery reconstitutes work from the **surviving** ledger/outbox; neither SQS queues nor unreplicated commits magically recover. Partner submissions use stable idempotency keys and query/reconcile uncertain outcomes before replay.
- Each region has one writer when primary and readers distributed for failover; R is a read-only global secondary before promotion. AWS-managed EKS control planes are outside the customer VPC; see the [physical deployment](deployment-architecture.md).
- EKS/Helm is the selected workload approach. ECS and Lambda are not additional delivery targets in this baseline.

[Pipeline ownership](deployment-pipelines.md) | [Recovery controls](dr-architecture.md) | [Consolidated RACI](../governance/ownership-model.md).

[Provider-native evidence](../appendix/provider-native-evidence.md): **S2** EKS networking; **S3** Pod Identity; **S4-S6** Aurora HA, global recovery and region support; **S9-S10** Kong DB-less and KIC; **S12** SQS. **S15** ECS and **S16** Lambda are comparison sources, not selected components.
