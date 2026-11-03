# Threat-control model

**Selected cloud: AWS. Task 5 (15%). Scope: payment data plane, Kong control/configuration plane, hybrid integration and three-layer delivery.**

Protect ledger integrity, payment credentials, entity data, deployment authority, gateway policy, audit evidence and recovery assets. Account, VPC, namespace, region, external rail and GitHub boundaries are distinct; no single boundary replaces the others.

| Material threat | Preventive controls | Detective controls | Responsive controls | Owner |
|---|---|---|---|---|
| Cross-entity access | Separate accounts/clusters, least-privilege IAM/resource policies, no default TGW cross-routing, distinct keys | IAM Access Analyzer, CloudTrail, network and data-access logs | Revoke grants, isolate resources, preserve evidence | Security/platform |
| Privileged misuse | Federation, short-lived roles, EKS access entries/RBAC, independent approvals | CloudTrail, EKS audit and privileged-operation alerts | Disable grants/sessions as applicable, rotate exposed credentials, review financial impact | Security |
| Application bypasses Kong | Platform-only public ingress, restrictive SGs, NetworkPolicy and admission | Inventory drift, unexpected listeners/routes, direct-access probes | Block bypass and quarantine release | Platform |
| Unauthorized Kong configuration | Private Admin API, KIC-only normal writes, namespace-scoped routes, plugin allowlist, platform-owned Gateway and baseline policy | KIC reconciliation errors, route/policy diffs, Kubernetes audit | Restore approved configuration, withdraw affected routes, rotate exposed secrets | Platform |
| Gateway compromise or insecure plugin | Patched pinned images, restricted pod privileges, approved plugins, TLS/mTLS | Runtime findings, gateway anomalies, unexpected egress | Isolate gateway/node, replace trusted images, revoke credentials | Platform/security |
| Authentication or authorization bypass | Approved token validation with issuer/audience/expiry checks; application business/entity authorization | Denial/anomaly metrics and security tests | Revoke credentials, block affected clients, investigate transactions | Platform + application |
| CI workflow compromise | Protected branches/environments, pinned action SHAs, exact OIDC trust, least-privilege GITHUB_TOKEN and AWS roles | Workflow audit, unusual STS role sessions, release provenance | Disable deploy trust, quarantine artifacts and releases | Delivery platform/security |
| Malicious dependency/image/chart | Dependency controls, SBOM, scans, signatures/provenance, immutable digests and admission enforcement | Registry findings and policy violations | Block promotion, rebuild trusted artifact, compatible rollback | Application/security |
| Deployment runner compromise | Ephemeral isolated runners, no untrusted PR execution, restricted network and credentials | Host/runner and egress telemetry | Destroy compromised runner, revoke authority, recreate trusted runner | Delivery platform |
| Pod escape and lateral movement | Nonroot/restricted pod security, seccomp, least privilege, IMDS restrictions, NetworkPolicy | Runtime monitoring and Kubernetes audit | Isolate nodes/workloads, rotate exposed identities | Platform |
| Exfiltration or wrong-location copy | Approved-region restrictions, endpoint/egress policies, key/resource policies, payload minimisation | CloudTrail/data events where configured, GuardDuty, approved S3 discovery | Block transfer, revoke access, incident and notification process | Security/data owner |
| Duplicate or manipulated payments | Idempotency, ACID invariants, authenticated rail integration, separation of duties | Ledger balance checks, rail reconciliation and anomaly alerts | Quarantine uncertainty; authorized compensating entries | Payments |
| Split-brain submission | Single authority and enforceable writer/rail fencing before recovery | Authority alarms and duplicate/sequence checks | Halt affected submission, establish authority, reconcile | Payments/operations |
| DDoS or resource exhaustion | WAF, applicable Shield protection, request limits, backpressure and capacity reserves | Traffic, latency, queue-age and saturation alarms | Filter/limit, prioritise critical traffic, scale safely | Network/platform/application |
| Backup deletion or ransomware | Recovery accounts, locked retention, independently protected keys and restore roles | Backup failures, deletion attempts and restore integrity exercises | Clean-room recovery and financial reconciliation | Security/data/operations |
| Audit tampering or gaps | Restricted archive access, immutable retention where supported, segregated log administration | Missing-log, delivery-error and configuration-drift alarms | Preserve copies, restore collection, investigate evidence gaps | Security |

AWS service capability must be enabled and configured; naming GuardDuty, Config or CloudTrail does not mean every workload or data event is covered. See [provider evidence](../appendix/provider-native-evidence.md), especially S1-S3, S7, S9-S14.

## Privileged and emergency access

Normal users authenticate through corporate federation with MFA and scoped, short-lived roles. Separate change author and approver for material production changes. Platform operators do not receive unrestricted ledger access merely because they manage EKS.

Break-glass identities are independently protected, monitored, periodically exercised and reviewed after use. Their reachability must cover the identity-provider outage scenario; do not depend exclusively on the failed IdP. Record authorization, actions, duration and credential rotation. Restrict Kong administration and emergency KIC changes so later reconciliation cannot silently overwrite an emergency fix.

## Trust and residual risk

Kong is self-hosted and bank-operated: plugin vulnerabilities, misconfiguration, license expiry where applicable and node capacity are the bank's responsibilities. Approved cross-border replication does not authorize arbitrary data in GitHub, third-party support systems or unapproved telemetry locations.

Rate limiting protects capacity, not ledger correctness. Per-node counters are not exact global enforcement. ALB TLS termination, Kong token validation and application authorization need separate threat analysis. GitHub availability must not determine ongoing payment service availability.

The [risk register](09-risk-register.md) records unresolved fencing, RPO and plugin decisions; the [ownership RACI](../governance/ownership-model.md) assigns accountability.
