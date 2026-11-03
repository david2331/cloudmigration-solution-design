# Validation and known limitations

**Selected cloud: AWS. This is an acceptance plan, not a report of executed deployment tests.**

| Area | Required validation | Evidence and pass condition |
|---|---|---|
| Account/entity boundary | Attempt cross-entity access to routes, pods, data, keys and Terraform state | Unauthorized operations denied and audited; exceptions explicitly approved |
| Residency | Inventory copies in P Malaysia/R Singapore and external systems | Every copy covered by approved scope; approval record attached |
| Terraform | Format/validate/plan, policy review, locking and restore exercise using selected pinned toolchain | No unauthorized or unexplained destructive plan; one resource/state owner; recoverable state |
| GitHub Actions | Reject wrong repository/environment subject, unauthorized promotion and untrusted runner use | Short-lived scoped roles; protected approvals; auditable immutable artifact promotion |
| Kong | Route isolation, bypass prevention, token/authorization failures, policy compatibility and config convergence | Only approved routes/policies accepted; no public Admin API; unconfigured pods not ready |
| Gateway resilience | Kill replicas/AZ capacity; expire certificates in rehearsal; block KIC API/config delivery | Existing valid routes remain safe; recovery behavior measured; restart does not silently accept empty config |
| Payment integrity | Duplicate and conflicting keys, concurrent writes, partial failures, external timeout | Balanced ledger and unique intended effects; uncertain payments quarantined |
| SLO/capacity | Peak traffic plus AZ loss and dependency slowdown | Approved latency/error budget met with safe database/queue pressure |
| Regional DR | Disable primary paths; include old-region-to-rail partition case | Exclusive authority established; safe critical journeys restored within 30 minutes; actual lost tail quantified |
| Cyber-recovery | Restore clean point in isolated account using recovery keys/identities | Trusted infrastructure, decryptable data and approved reconciliation; separate recovery objectives met |
| Failback | Rebuild/resynchronise Malaysia and controlled authority transfer | No dual writers/submitters, compatible versions and reconciled state |
| Portability | Move representative image/chart and replace relevant adapters | Record changes and switching cost; preserve API and financial behavior |
| Cost | Baseline/peak/DR simulation and entity allocation | Funded unit-cost model with visible shared and recovery costs |

Execute only after implementation in controlled environments. Retain dates, versions, account/region identifiers, outcomes, timings and remediation owners. Use the [DR scenario catalogue](../appendix/dr-testing-scenarios.md) for detailed recovery cases.

## Known limitations and approval gates

This repository currently contains design documents, not runnable Terraform, Helm releases, Kong configurations or GitHub Actions workflows. No production resources, feature availability inventory, measured SLOs or recovery results are asserted.

Critical journey definitions, throughput/latency, named legal entities, retention periods, precise payment commitment semantics and quantified near-zero RPO remain open. Aurora Global Database support is listed for both regions, but that does not validate every chosen version, feature, quota or capacity class.

Cross-border approval is user-confirmed granted; its document/reference, scope and conditions are not supplied. This draft is not legal or regulatory certification.

Kong DB-less/KIC, Gateway API resource compatibility, authentication plugins, license/support model, certificate validation and shared-rate-limit semantics need implementation selection. Do not assume every enterprise plugin is available or DB-less compatible.

The fencing algorithm is unresolved and must cover continued old-region rail access. Regional asynchronous replication may lose acknowledged data. If zero loss is required, the current data proposal is insufficient. Cyber-recovery is not yet demonstrated within the normal regional RTO/RPO.

The ADR is a two-page-equivalent Markdown narrative; actual pagination/readability depends on the final export format. Mermaid diagrams are source diagrams and should be rendered and reviewed in the submission's target viewer before final export.
