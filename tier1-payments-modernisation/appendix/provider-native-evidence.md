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
| S17 | [Aurora Global Database overview](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html) | Storage-level replication to secondaries with typical lag documented as under one second; "typical" is not a bound, so it informs but does not set the RPO |
| S18 | [Route 53 Application Recovery Controller](https://docs.aws.amazon.com/r53recovery/latest/dg/what-is-route53-recovery.html) | Readiness checks and highly available routing controls give an operator-controlled traffic switch independent of the failed Region's control plane; it switches traffic, it does not fence writers |
| S19 | [ARC zonal shift](https://docs.aws.amazon.com/r53recovery/latest/dg/arc-zonal-shift.html) | Moves supported load balancer and EKS traffic away from an impaired AZ; requires pre-provisioned capacity in remaining AZs |
| S20 | [AWS Fault Injection Service](https://docs.aws.amazon.com/fis/latest/userguide/what-is.html) | Managed, stop-condition-guarded fault experiments (AZ, EKS, network, database actions) for repeatable recovery evidence |
| S21 | [Amazon RDS Proxy](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/rds-proxy.html) | Connection pooling and faster client reconnection on Aurora failover; adds a component whose capacity and connection-pinning behavior need testing |
| S22 | [AWS Backup logically air-gapped vault](https://docs.aws.amazon.com/aws-backup/latest/devguide/logicallyairgappedvault.html) | Locked, service-isolated vault shareable to a recovery account; supported resource types are limited. AWS documents it as not currently available in Asia Pacific (Malaysia), so P cannot use it; use a Vault Lock vault in the recovery account [S11] and re-check before approval |
| S23 | [Amazon Aurora DSQL](https://docs.aws.amazon.com/aurora-dsql/latest/userguide/what-is-aurora-dsql.html) | Multi-Region clusters with strongly consistent synchronous commit; PostgreSQL-compatible with feature differences. Singapore is a documented Region; Malaysia does not appear in the documented Region list (checked 4 Nov 2026), so it cannot pair P with R |
| S24 | [DynamoDB global tables](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/GlobalTables.html) | Multi-Region eventual or strong consistency modes; strong consistency (MRSC) needs exactly three Regions (or two plus a witness) chosen from a documented set that includes Singapore but not Malaysia, and it changes the data model |
| S25 | [AWS Private CA](https://docs.aws.amazon.com/privateca/latest/userguide/PcaWelcome.html) | Managed private certificate hierarchy for mTLS issuance and rotation; CA hierarchy and key custody remain bank decisions |
| S26 | [AWS Payment Cryptography](https://docs.aws.amazon.com/payment-cryptography/latest/userguide/what-is.html) | Managed payment HSM functions (PIN, MAC, key exchange); Region availability must be confirmed |
| S27 | [AWS CloudHSM](https://docs.aws.amazon.com/cloudhsm/latest/userguide/introduction.html) | Single-tenant HSM clusters across AZs under customer key control; the bank owns cluster availability, backup and crypto-user management |
| S28 | [Amazon S3 Object Lock](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock.html) | WORM retention for audit logs and evidence; compliance mode cannot be shortened by any user |
| S29 | [Aurora Database Activity Streams](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/DBActivityStreams.html) | Near-real-time, KMS-encrypted database activity feed outside DBA control for privileged-access monitoring |
| S30 | [Split cost allocation data](https://docs.aws.amazon.com/cur/latest/userguide/split-cost-allocation-data.html) | Allocates EKS node cost to pods and namespaces in cost and usage reports for shared-cluster chargeback |
| S31 | [AWS Database Migration Service](https://docs.aws.amazon.com/dms/latest/userguide/Welcome.html) | Full-load and CDC replication with data validation for migration and comparison; not a substitute for single-writer authority |
| S32 | [EKS on AWS Fargate](https://docs.aws.amazon.com/eks/latest/userguide/fargate.html) | Per-pod serverless capacity for EKS with DaemonSet, privileged-pod and storage restrictions |
| S33 | [AWS regional services list](https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/) | Authoritative per-Region availability; Malaysia `ap-southeast-5` is a newer Region, so each named service must be confirmed there |
| S34 | [Amazon MQ](https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/welcome.html) | Managed ActiveMQ/RabbitMQ brokers for protocol-compatible bridging; does not provide IBM MQ |
| S35 | [AWS Transfer Family](https://docs.aws.amazon.com/transfer/latest/userguide/what-is-aws-transfer-family.html) | Managed SFTP/FTPS/AS2 into S3 for file-based clearing and settlement exchange |

**Regional availability rule.** S1-S16 are core to the baseline. S17-S35 are proposed enhancements or comparison options; every one is conditional on confirmation in S33 for both `ap-southeast-5` and `ap-southeast-1`. Where a service is absent in Malaysia, the documented fallback is used (for example, Kubernetes-native pod drain instead of ARC zonal shift; a self-managed CA on CloudHSM instead of Private CA) and the gap is recorded in the region bill of materials.

## Evidence still required from the bank

| Evidence | Required owner/action |
|---|---|
| Cross-border permission | Security/compliance attaches already-granted Malaysia/Singapore approval reference, covered entities/data categories and conditions |
| Recovery objectives | Payments business/data owners define commitment, numerical near-zero RPO and allowable exposure |
| Region/feature bill of materials | Platform/data/network owners confirm pinned versions, AZ/instance capacity, quotas, endpoints and backup-copy support in both regions; check S17-S35 against S33 and record fallbacks |
| Kong feature matrix | Platform confirms edition/support, authentication plugins, DB-less/KIC/Gateway API compatibility, config recovery and counter semantics |
| End-to-end recovery | Operations attaches measured timings, fencing proof, lost-tail assessment and reconciliation results |
| Threat-control operation | Security attaches configured coverage and evidence, not just service-name lists |

S9/S10 describe a **proposed** self-hosted topology. They do not select Kong Enterprise, promise licensed plugin availability or introduce Konnect. P/R approval is bank-provided context, not a fact inferred from public AWS documentation.

See [AI assistance disclosure](ai-assistance-disclosure.md) for provenance and [validation limitations](../architecture-paper/09-validation-and-limitations.md) for acceptance gates.
