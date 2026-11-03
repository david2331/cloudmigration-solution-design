# Provider-native evidence and source register

**Selected cloud: AWS. Documentation consulted during drafting on 3 November 2026.** Sources support described service behavior; they do not prove this bank's deployment, regulatory compliance or measured recovery. Reconfirm current service versions, regional features, quotas and licensing at implementation.

| ID | Official source | Behavior and design consequence |
|---|---|---|
| S1 | [AWS Control Tower accounts](https://docs.aws.amazon.com/controltower/latest/userguide/accounts.html) | Account creation/enrolment deploys governance resources; use for landing-zone provisioning, not as a blanket compliance certificate |
| S2 | [EKS networking and endpoint access](https://docs.aws.amazon.com/eks/latest/best-practices/subnets.html) | AWS-managed control plane is separate from the customer node VPC; private API access requires connected tooling |
| S3 | [EKS Pod Identity](https://docs.aws.amazon.com/eks/latest/userguide/pod-identities.html) | Maps service accounts to IAM roles; restrict IMDS because pod identity alone does not block node credentials |
| S4 | [Aurora high availability](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Concepts.AuroraHighAvailability.html) | Regional storage replicated synchronously across AZs; readers and failover compute are separate concerns |
| S5 | [Aurora Global Database disaster recovery](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database-disaster-recovery.html) | Unplanned global failover can lose async tail; healthy planned switchover synchronises first; RPO controls can affect write processing |
| S6 | [Aurora Global Database region/engine matrix](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Concepts.Aurora_Fea_Regions_DB-eng.Feature.GlobalDatabase.html) | Lists Aurora PostgreSQL Global Database in Malaysia and Singapore; choose supported common versions, not any arbitrary version |
| S7 | [GitHub Actions OIDC with AWS](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws) | Short-lived AWS federation; validate audience and actual subject format, including repository/environment protection and applicable immutable subject IDs |
| S8 | [Terraform S3 backend](https://developer.hashicorp.com/terraform/language/backend/s3) | Enable versioning and explicit `use_lockfile` with compatible Terraform; DynamoDB-based locking is deprecated; state access is sensitive |
| S9 | [Kong Gateway DB-less mode](https://developer.konghq.com/gateway/db-less-mode/) | No Kong configuration DB; configuration must reach every node; with KIC, Kubernetes API resources are the source; decK sync/dump workflows require DB-backed mode |
| S10 | [Kong Ingress Controller](https://developer.konghq.com/kubernetes-ingress-controller/) | Translates Kubernetes resources to Kong config; support, failure behavior and licensing vary by deployment model/version |
| S11 | [AWS Backup Vault Lock](https://docs.aws.amazon.com/aws-backup/latest/devguide/vault-lock.html) | Compliance lock is immutable after grace period while recovery points remain; governance lock removable by sufficiently privileged users |
| S12 | [SQS at-least-once delivery](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/standard-queues-at-least-once-delivery.html) | Standard queue messages may be delivered again; consumers must be idempotent |
| S13 | [Direct Connect with Site-to-Site VPN](https://docs.aws.amazon.com/whitepapers/latest/aws-vpc-connectivity-options/aws-direct-connect-site-to-site-vpn.html) | Documents combining private connectivity and IPsec; cited example is not an automatically applicable TGW/private-VIF topology |
| S14 | [Transit Gateway routing and attachments](https://docs.aws.amazon.com/vpc/latest/tgw/transit-gateway-appliance-scenario.html) | Regional routing and attachment/AZ behavior require deliberate segmentation; explicitly engineer inspection paths and route propagation |
| S15 | [Amazon ECS execution model](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/launch_types.html) | Task definitions, services and scheduler behavior provide a credible non-Kubernetes container alternative |
| S16 | [AWS Lambda quotas and constraints](https://docs.aws.amazon.com/lambda/latest/dg/gettingstarted-limits.html) | Concurrency, duration and resource limits vary by execution mode; assess the selected mode and workload |

## Evidence still required from the bank

| Evidence | Required owner/action |
|---|---|
| Cross-border permission | Security/compliance attaches already-granted Malaysia/Singapore approval reference, covered entities/data categories and conditions |
| Recovery objectives | Payments business/data owners define commitment, numerical near-zero RPO and allowable exposure |
| Region/feature bill of materials | Platform/data/network owners confirm pinned versions, AZ/instance capacity, quotas, endpoints and backup-copy support in both regions |
| Kong feature matrix | Platform confirms edition/support, authentication plugins, DB-less/KIC/Gateway API compatibility, config recovery and counter semantics |
| End-to-end recovery | Operations attaches measured timings, fencing proof, lost-tail assessment and reconciliation results |
| Threat-control operation | Security attaches configured coverage and evidence, not just service-name lists |

S9/S10 describe a **proposed** self-hosted topology. They do not select Kong Enterprise, promise licensed plugin availability or introduce Konnect. P/R approval is user-provided context, not a fact inferred from public AWS documentation.

See [AI assistance disclosure](ai-assistance-disclosure.md) for provenance and [validation limitations](../architecture-paper/10-validation-and-limitations.md) for acceptance gates.
