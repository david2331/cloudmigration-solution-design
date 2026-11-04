# Data integrity and disaster recovery

**Selected cloud: AWS. Task 4 (20%). P = Malaysia `ap-southeast-5`; R = Singapore `ap-southeast-1`. Cross-border approval is granted per bank confirmation (assumption C05).**

## Transaction semantics

Separate received, durably accepted, ledger committed, submitted externally, externally confirmed and settled states. A successful receipt is not final settlement. The business/data owner must define which state is promised by each API response and exactly what counts as a committed payment for RPO.

Use entity-scoped payment IDs and idempotency keys. An ACID transaction records payment state, balanced ledger postings and the transactional outbox as appropriate to the transition. Database constraints and tested concurrency control enforce invariants; requests reusing a key with different content are rejected. Retries return the recorded result.

The ledger is append-oriented: corrections create authorized compensating entries, not destructive edits. Gateway authentication/rate limiting does not replace service-level authorization or financial invariants.

## Outbox, delivery and reconciliation

Publish durable outbox events to region-local SQS. A crash between publish and marking the outbox record can duplicate delivery; consumers record processed identifiers atomically with effects where possible. SQS standard queues are at-least-once [S12]. FIFO may help ordering within message groups but does not create exactly-once external settlement.

External timeouts are unknown outcomes. Re-query with the original rail reference before resubmission. If the rail cannot offer idempotency/status lookup, quarantine uncertain payments and use operational reconciliation.

Reconcile bank ledger, external submissions/acknowledgements, settlement statements and balances. Track missing/duplicate/mismatched items in a controlled exception queue with owner and ageing. Pending payments remain visible to customer-service operations.

## Primary and secondary databases

Use one Aurora PostgreSQL ledger cluster per entity. Malaysia hosts the writer and failover readers across AZs; storage is synchronously replicated across AZs [S4]. Reader replication behavior is distinct from storage durability. Financial read-after-write paths use the writer or an explicitly validated consistency approach.

Singapore hosts the Aurora Global Database secondary in the same entity production account. Replication is asynchronous [S5]. The provider's region/engine matrix lists PostgreSQL Global Database in both Malaysia and Singapore [S6]; choose a currently supported common engine/version and validate failover compatibility, instance classes, quotas and capacity before deployment.

Use separate backups in the entity recovery account to address account compromise. The live secondary is not an independently protected cyber-recovery copy.

## RPO credibility

| Failure | Intended recovery point | Limitation |
|---|---|---|
| Pod/node failure | No loss of successfully committed ledger data | No authoritative state only in container memory/disk |
| Ordinary AZ or DB instance failure | Zero committed loss within Aurora regional durability design | Application retries and ambiguous responses still require reconciliation |
| Healthy planned global switchover | Zero database data loss supported by synchronized switchover | Compatible versions and coordinated application/rail transition required |
| Sudden Malaysia regional loss | Near-zero may be achievable; not guaranteed zero | Depends on replication tail and failure conditions |
| SQS consumer/queue disruption | Replay surviving outbox and processing records | SQS is regional; replay cannot recreate a lost database tail |
| Corruption or ransomware | Last clean recoverable point plus reconciliation | Replication may propagate corruption; normal DR RPO is not automatically met |

**Open approval gate:** quantify near-zero (time and transaction exposure) and whether loss of any acknowledged payment is allowed. If the requirement is zero lost acknowledged commits during regional failure, this asynchronous topology is insufficient. Evaluate a synchronously durable commitment design against supported regions, latency, SQL semantics, availability under partition and cost. Do not claim compliance by simply accepting an unspecified risk.

Aurora PostgreSQL `rds.global_db_rpo` can constrain processing as replication falls behind, trading write availability for tighter exposure; it does not make asynchronous replication an unconditional zero-loss protocol [S5].

## Regional recovery and fencing

Singapore has pre-provisioned EKS, platform-owned Kong/KIC, routes, WAF/ALB, connectivity, database capacity, regional SQS, ECR artifacts, certificates, secrets and keys. Dormant payment submitters must remain disabled until authorized. DB-less Kong restores approved Kubernetes configuration; it has no configuration database to promote. Readiness rejects empty/unconfigured gateways.

| Elapsed target | Activity |
|---|---|
| 0-3 minutes | Detect disruption and affected critical journeys |
| 3-8 minutes | Assess failure and authorize regional recovery under delegated incident procedure |
| 8-15 minutes | Establish exclusive authority, fence old writers/submitters, promote database and dependencies |
| 15-23 minutes | Enable Singapore applications/Kong, replay surviving outbox, quarantine uncertain payments |
| 23-30 minutes | Switch ingress, establish safe critical journeys and monitor |

These are proposed allocations, not measured outcomes. Full historical reconciliation may continue, but affected uncertain payments cannot be blindly resubmitted.

**DNS is not fencing.** Route 53 changes do not stop old workers, open connections or an isolated primary. Detailed fencing must cover database writes and external rail submissions, including a partition where Malaysia remains able to reach the rail. Candidate controls include enforceable exclusive rail sessions/credentials and writer authority with fail-closed expiry, but their implementation and failure guarantees are unresolved. Do not promote a competing writer/submitter if exclusive authority cannot be established.

Under such uncertainty, safety may exceed the 30-minute RTO. This conflict must be resolved before production approval, not concealed in the runbook. Regional failover requires coordinated database, application, Kong, on-premises routing and rail action; database promotion time alone is not end-to-end RTO.

If GitHub is unavailable, execute an independently authorized runbook using prepositioned artifacts and recovery identities. Do not require a fresh Terraform build of the entire recovery estate. Failback is a separate planned event: rebuild/resynchronise Malaysia, reconcile, confirm compatibility, fence the Singapore authority and perform controlled switchover. No uncontrolled reverse dual writes.

## Backup and cyber-recovery

Enable point-in-time recovery and approved snapshot schedules. Use supported encrypted cross-account/cross-region backup-copy workflows, verifying restore and retention capability per resource. Keep backups in the isolated entity recovery account with independently governed keys and principals.

Use AWS Backup Vault Lock compliance mode after retention review and its grace period [S11]. Governance mode can be removed by privileged users; it is not equivalent immutability. Protect KMS key lifecycle and recovery credentials: undeletable backups are useless without decryptability.

Recover compromise in a clean-room environment from a verified clean point, trusted Terraform/Helm/image versions and rotated credentials. Investigate restored financial state and reconcile before service resumption. Cyber-recovery has a separately approved, currently unmeasured RTO/RPO; this draft does not claim it fits 30 minutes.

See [DR diagram](../diagrams/dr-architecture.md), [exercise catalogue](../appendix/dr-testing-scenarios.md), [risk register](08-risk-register.md) and [sources S4-S6, S9-S12](../appendix/provider-native-evidence.md).
