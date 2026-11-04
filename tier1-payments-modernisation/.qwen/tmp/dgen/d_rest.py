import sys
sys.path.insert(0, "/Users/david/Documents/work/cloudmigration-solution-design/tier1-payments-modernisation/.qwen/tmp/dgen")
from lib import Diagram, build

OUT = "/Users/david/Documents/work/cloudmigration-solution-design/tier1-payments-modernisation/diagrams"
WORK = "/Users/david/Documents/work/cloudmigration-solution-design/tier1-payments-modernisation/.qwen/tmp/dgen"


def dr():
    d = Diagram("dr-architecture", "Disaster recovery — each entity recovers independently from Malaysia (P) to Singapore (R)", 1700, 1120)

    d.group("ops", "plain", "Recovery authority (independent of GitHub and of the failed region)", 20, 60, 1180, 130)
    d.res("incident", "users", "Incident command + entity<br>payment owner (authorise)", 90, 90, parent="ops")
    d.res("operator", "server", "Independent recovery runner<br>+ runbooks, prepositioned artifacts", 480, 90, parent="ops")
    d.svc("arc", "arc", "Route 53 ARC routing controls<br>(traffic switch, not fencing)", 900, 90, parent="ops")

    d.group("acct", "account", "Entity workload account — repeat for entity A and entity B", 20, 210, 1180, 560)
    d.group("p", "region", "P: Malaysia ap-southeast-5 — three AZs", 40, 250, 520, 500, parent="acct")
    d.svc("pk", "eks", "EKS / Kong /<br>payment submitters", 110, 310, parent="p")
    d.svc("pd", "aurora", "Aurora primary:<br>ledger + outbox", 110, 470, parent="p")
    d.svc("pq", "sqs", "Local SQS / DLQ", 360, 470, parent="p")
    d.badge("s2", "2", 175, 300, parent="p", color="#B85450")

    d.group("r", "region", "R: Singapore ap-southeast-1 — three AZs, pre-provisioned", 600, 250, 580, 500, parent="acct")
    d.svc("rd", "aurora", "Aurora global secondary<br>(read-only until promoted)", 660, 470, parent="r")
    d.svc("rq", "sqs", "Local SQS / DLQ (rebuilt<br>work, not replicated)", 920, 470, parent="r")
    d.svc("rk", "eks", "EKS / Kong / routes / network,<br>keys, secrets, certs, images", 920, 310, parent="r")
    d.diamond("gate", "Safety gate:<br>writer AND submitters<br>fenced; loss assessed", 620, 290, 220, 110, color="red", parent="r")
    d.badge("s4", "4", 640, 470, parent="r")
    d.badge("s5", "5", 985, 460, parent="r")
    d.badge("s6", "6", 985, 300, parent="r")

    d.group("vault", "account", "Entity recovery account — cyber-recovery boundary", 20, 790, 760, 310)
    d.svc("imm", "backup", "AWS Backup Vault Lock<br>(compliance mode)", 110, 860, parent="vault")
    d.res("clean", "vault", "Isolated clean-room restore:<br>new credentials, integrity checks", 420, 860, parent="vault")
    d.add_text("vnote", "Cyber recovery has its own approved RTO/RPO; the 30-minute regional target does not apply.", 60, 1010, 680, 40, parent="vault", size=11)

    d.group("ext", "external", "External payment partners", 800, 790, 400, 310)
    d.res("partner", "bank", "Rails / settlement<br>(idempotency + status query)", 976, 860, parent="ext")
    d.add_text("pnote", "Unknown outcomes are queried with the original reference before any resubmission.", 820, 1000, 360, 50, parent="ext", size=11)

    d.legend(1220, 60, [
        ("flow", "Normal / restored flow"),
        ("async", "Async replication (loss possible)"),
        ("fenced", "Gated recovery action"),
        ("backup", "Backup copy policy"),
        ("control", "Operator control action"),
    ], width=460)

    d.group("steps", "plain", "Ordered regional recovery", 1220, 230, 460, 520)
    steps = [
        "<b>1 Detect and declare</b> — record disruption time, scope, replication health; owner authorises runbook.",
        "<b>2 Fence before promotion</b> — revoke old writer and submitter authority with an enforceable lease; DNS is not fencing.",
        "<b>3 Assess loss</b> — replicated ledger/outbox position, ambiguous acknowledgements, partner-side submissions.",
        "<b>4 Promote</b> — approved Aurora global failover; verify single writer and regional secrets.",
        "<b>5 Rebuild work</b> — replay only surviving outbox into R-local SQS with de-duplication.",
        "<b>6 Validate then switch</b> — probes and canaries; flip ARC routing control; enable safe journeys only.",
        "<b>7 Fail back separately</b> — rebuild P as secondary; planned switchover later.",
    ]
    y = 262
    for i, n in enumerate(steps):
        d.add_text(f"st{i}", n, 1230, y, 440, 64, parent="steps", size=11)
        y += 68

    d.group("obj", "plain", "Draft objectives (unmeasured)", 1220, 770, 460, 330)
    objs = [
        "<b>AZ failure:</b> expected zero committed loss; stay within 99.99% error budget.",
        "<b>Regional disaster:</b> RTO <= 30 min from disruption to safe critical journeys.",
        "<b>Regional data:</b> near-zero RPO aspiration, not guaranteed zero (async tail).",
        "<b>Cyber:</b> separate clean-room RTO/RPO to be agreed and measured.",
    ]
    y = 805
    for i, n in enumerate(objs):
        d.add_text(f"ob{i}", n, 1230, y, 440, 62, parent="obj", size=12)
        y += 70

    d.edge("incident", "operator", "control", "authorise")
    d.edge("operator", "pk", "fenced", "stop writes + side effects", exit=(0.5, 1), entry=(0.5, 0), points=[(504, 230), (134, 230)])
    d.edge("operator", "gate", "control", "", exit=(0.8, 1), entry=(0.5, 0), points=[(518, 240), (730, 240)])
    d.edge("operator", "arc", "control", "")
    d.edge("pk", "pd", "flow", "")
    d.edge("pk", "pq", "flow", "", exit=(1, 0.5), entry=(0.5, 0), points=[(384, 334)])
    d.edge("pd", "rd", "async", "asynchronous replication; non-zero loss possible", exit=(0.5, 1), entry=(0.5, 1), points=[(134, 600), (684, 600)])
    d.edge("gate", "rd", "fenced", "promote after fencing evidence", exit=(0.3, 1), entry=(0.3, 0))
    d.edge("gate", "rk", "fenced", "enable safe journeys", exit=(1, 0.5), entry=(0, 0.5), points=[(880, 345), (880, 334)])
    d.edge("rd", "rq", "fenced", "replay surviving outbox")
    d.edge("rq", "rk", "flow", "")
    d.edge("arc", "rk", "flow", "switch after validation", exit=(0.5, 1), entry=(0.8, 0), points=[(924, 220), (958, 220)])
    d.edge("rk", "partner", "fenced", "after gate", exit=(1, 0.5), entry=(1, 0.5), points=[(1160, 334), (1160, 884)])
    d.edge("pd", "imm", "backup", "approved backup copy policy", exit=(0, 0.5), entry=(0.5, 0), points=[(70, 494), (70, 780), (134, 780)])
    d.edge("imm", "clean", "backup", "")
    d.edge("clean", "rk", "control", "separate cyber release approval", exit=(1, 0.3), entry=(1, 0.8), points=[(790, 874), (790, 770), (1190, 770), (1190, 348)])
    return d


def hybrid():
    d = Diagram("hybrid-connectivity", "Hybrid connectivity — on-premises to both Malaysia (P) and Singapore (R)", 1700, 1160)

    d.group("prem", "dc", "On-premises trust boundary", 20, 60, 1180, 160)
    d.res("apps", "server", "Approved channels / operations /<br>payment systems", 540, 90, parent="prem")
    d.res("ra", "cgw", "Customer router A /<br>carrier A", 220, 100, parent="prem", size=40)
    d.res("rb", "cgw", "Customer router B /<br>carrier B", 920, 100, parent="prem", size=40)

    d.group("net", "account", "Network account — segmented regional routing", 20, 240, 1180, 560)
    d.svc("dx1", "dx", "DX path A — diverse<br>location / circuit", 220, 290, parent="net")
    d.svc("dx2", "dx", "DX path B — independent<br>failure domain", 920, 290, parent="net")
    d.res("dxgw", "tgw_att", "Direct Connect gateway<br>(transit VIFs, controlled prefixes)", 570, 390, parent="net")

    for i, (rid, name, short) in enumerate((("my", "P: Malaysia ap-southeast-5", "p"), ("sg", "R: Singapore ap-southeast-1", "r"))):
        x = 40 + i * 580
        d.group(rid, "region", name, x, 490, 560, 290, parent="net")
        d.svc(f"vpn{short}", "vpn", "Site-to-Site VPN<br>fallback (internet)", x + 60, 540, parent=rid)
        d.svc(f"tgw{short}", "tgw", "Transit Gateway<br>entity route tables", x + 250, 540, parent=rid)
        d.group(f"insp{short}", "plain", "Inspection VPC — AZ-local endpoints", x + 20, 650, 520, 110, parent=rid)
        for j, az in enumerate("abc"):
            d.svc(f"nf{short}{az}", "nfw", f"AZ-{az} firewall", x + 70 + j * 170, 680, parent=f"insp{short}", size=36)

    for i, ent in enumerate("ab"):
        x = 20 + i * 600
        other = "B" if ent == "a" else "A"
        d.group(f"acct{ent}", "account", f"entity-{ent}-prod — no default entity {other} routes", x, 820, 580, 320)
        for j, (reg, lab) in enumerate((("p", "P"), ("r", "R"))):
            gx = x + 20 + j * 280
            d.group(f"v{ent}{reg}", "vpc", f"{lab} workload VPC", gx, 860, 260, 260, parent=f"acct{ent}")
            d.res(f"alb{ent}{reg}", "alb", "Private ALB", gx + 30, 910, parent=f"v{ent}{reg}")
            d.k8s(f"kong{ent}{reg}", "pod", "Kong", gx + 170, 910, parent=f"v{ent}{reg}")
            d.svc(f"eks{ent}{reg}", "eks", "ClusterIP apps<br>(EKS, 3 AZs)", gx + 100, 1020, parent=f"v{ent}{reg}")

    d.legend(1220, 60, [
        ("hybrid", "Direct Connect (private, not encrypted)"),
        ("fenced", "IPsec VPN fallback"),
        ("flow", "Inspected, entity-scoped route"),
        ("control", "Routed inspection, symmetric return"),
    ], width=460)

    d.group("contracts", "plain", "Routing and security contracts", 1220, 230, 460, 910)
    notes = [
        "<b>Diversity:</b> two DX routes with evidenced carrier, location, router and last-mile diversity; both regional TGWs reachable independently.",
        "<b>VPN fallback:</b> tunnels to each country's TGW; validate BGP preference, MTU/MSS and degraded capacity for critical journeys.",
        "<b>Encryption:</b> DX is not encrypted. Require TLS/mTLS end-to-end or an engineered IPsec overlay.",
        "<b>Segmentation:</b> separate TGW route domains per entity; no default cross-entity propagation or automatic P<->R peering.",
        "<b>Inspection:</b> per-AZ Network Firewall endpoints with appliance mode and symmetric routes. Only routed traffic is inspected; TLS is not decrypted automatically.",
        "<b>Private ingress:</b> internal ALB -> Kong -> ClusterIP. SGs, NetworkPolicy and admission prevent direct exposure.",
        "<b>DNS:</b> Route 53 Resolver inbound/outbound endpoints in both regions; private naming is not authorisation.",
        "<b>Readiness:</b> prove reachability to both regions. Route availability must never enable dual writers.",
    ]
    y = 265
    for i, n in enumerate(notes):
        d.add_text(f"n{i}", n, 1230, y, 440, 100, parent="contracts", size=12)
        y += 108

    d.edge("apps", "ra", "line", "", ortho=False)
    d.edge("apps", "rb", "line", "", ortho=False)
    d.edge("ra", "dx1", "hybrid", "")
    d.edge("rb", "dx2", "hybrid", "")
    d.edge("dx1", "dxgw", "hybrid", "", exit=(0.5, 1), entry=(0, 0.5), points=[(244, 414)])
    d.edge("dx2", "dxgw", "hybrid", "", exit=(0.5, 1), entry=(1, 0.5), points=[(944, 414)])
    d.edge("dxgw", "tgwp", "hybrid", "approved P prefixes", exit=(0.3, 1), entry=(0.5, 0), points=[(584, 470), (314, 470)])
    d.edge("dxgw", "tgwr", "hybrid", "approved R prefixes", exit=(0.7, 1), entry=(0.5, 0), points=[(604, 470), (894, 470)])
    d.edge("ra", "vpnp", "fenced", "IPsec", exit=(0, 0.5), entry=(0, 0.5), points=[(30, 120), (30, 564)])
    d.edge("rb", "vpnr", "fenced", "IPsec", exit=(1, 0.5), entry=(0.5, 0), points=[(1190, 120), (1190, 520), (684, 520)])
    d.edge("vpnp", "tgwp", "fenced", "")
    d.edge("vpnr", "tgwr", "fenced", "")
    d.edge("tgwp", "nfpb", "control", "symmetric", exit=(0.5, 1), entry=(0.5, 0), points=[(314, 640), (298, 640)])
    d.edge("tgwr", "nfrb", "control", "symmetric", exit=(0.5, 1), entry=(0.5, 0), points=[(894, 640), (878, 640)])
    d.edge("nfpa", "albap", "flow", "entity A", exit=(0.5, 1), entry=(0.5, 0), points=[(128, 800), (94, 800)])
    d.edge("nfpc", "albbp", "flow", "entity B", exit=(0.5, 1), entry=(0.5, 0), points=[(468, 805), (694, 805)])
    d.edge("nfra", "albar", "flow", "entity A", exit=(0.5, 1), entry=(0.5, 0), points=[(708, 795), (374, 795)])
    d.edge("nfrc", "albbr", "flow", "entity B", exit=(0.5, 1), entry=(0.5, 0), points=[(1048, 810), (974, 810)])
    for ent in "ab":
        for reg in "pr":
            d.edge(f"alb{ent}{reg}", f"kong{ent}{reg}", "flow", "")
            d.edge(f"kong{ent}{reg}", f"eks{ent}{reg}", "flow", "", exit=(0.5, 1), entry=(1, 0.5))
    return d


def pipelines():
    d = Diagram("deployment-pipelines", "Deployment pipelines — three delivery layers; platform Kong release is a foundation subpipeline", 1700, 1140)

    d.group("gh", "github", "GitHub trust boundary", 20, 60, 1180, 170)
    d.github("ghlogo", "GitHub", 50, 100, parent="gh", size=40)
    d.box("pr", "Untrusted pull requests<br>checks only, no deploy creds", 150, 110, 210, 60, "red", parent="gh")
    d.box("reviewed", "Protected reviewed<br>commit / workflow", 410, 110, 200, 60, "blue", parent="gh")
    d.box("build", "Isolated build + scan<br>image, chart, SBOM, provenance", 660, 110, 230, 60, "blue", parent="gh")
    d.box("approval", "Protected environment<br>approval (branches, reviewers)", 940, 110, 230, 60, "yellow", parent="gh")

    d.group("tool", "account", "Platform tooling account — connected deployment trust boundary", 20, 250, 1180, 180)
    d.svc("ecr", "ecr", "ECR immutable image + OCI chart<br>digests; signed manifest; R copies", 130, 300, parent="tool")
    d.res("runner", "server", "Ephemeral deployment runners<br>(no PR code, per trust tier)", 560, 300, parent="tool")
    d.res("sts", "sts", "AWS STS: OIDC exact aud/sub<br>layer + entity + env roles", 960, 300, parent="tool")

    d.group("tgt", "account", "Selected entity account + environment (P or R)", 20, 450, 1180, 670)
    d.group("l1", "plain", "Layer 1 — Foundation (platform team)", 40, 490, 360, 400, parent="tgt")
    d.box("f", "Terraform: accounts, VPC,<br>EKS, IAM boundaries", 70, 540, 300, 60, "blue", parent="l1")
    d.box("platform", "Foundation subpipeline (Helm):<br>controllers, Kong, platform policy", 70, 660, 300, 60, "purple", parent="l1")
    d.res("state", "bucket", "S3 Terraform state — versioning,<br>SSE-KMS, native lockfile", 196, 780, parent="l1")

    d.group("l2", "plain", "Layer 2 — Application infrastructure (product team)", 420, 490, 360, 400, parent="tgt")
    d.box("infra", "Terraform: Aurora, SQS, S3, IAM,<br>secret metadata, alarms", 450, 540, 300, 60, "blue", parent="l2")
    d.svc("aur", "aurora", "Aurora", 470, 680, parent="l2")
    d.svc("sqs", "sqs", "SQS", 576, 680, parent="l2")
    d.svc("sec", "secrets", "Secrets", 680, 680, parent="l2")

    d.group("l3", "plain", "Layer 3 — Application code (product team)", 800, 490, 380, 400, parent="tgt")
    d.box("app", "Helm: services, immutable images,<br>approved HTTPRoutes, DB migrations", 830, 540, 320, 60, "blue", parent="l3")
    d.svc("eks", "eks", "Private EKS — three AZs,<br>namespace-scoped RBAC", 966, 680, parent="l3")

    d.box("verify", "Canary / SLO / payment probes — approve promotion or compatible rollback", 40, 920, 1140, 50, "green", parent="tgt")
    d.box("independent", "Independent approved emergency runner — prepositioned artifacts, no GitHub dependency; audited recovery only, DR safety gates still apply", 40, 1000, 1140, 60, "orange", parent="tgt", dashed=True)

    d.legend(1220, 60, [
        ("flow", "Promotion flow"),
        ("deploy", "Scoped role assumption / deploy"),
        ("control", "Versioned contract / output"),
        ("fenced", "Emergency-only path"),
    ], width=460)

    d.group("rules", "plain", "Identity, artifact and rollback rules", 1220, 230, 460, 890)
    notes = [
        "Issuer token.actions.githubusercontent.com, aud = sts.amazonaws.com, exact sub. No org- or repo-wide wildcards for production.",
        "An environment subject does not contain the branch: enforce deployment branches, reviewers and workflow-change control separately.",
        "Roles split by layer + entity + environment; limit session duration, iam:PassRole and EKS access entries.",
        "Build once, promote the same digest; verify signatures in each registry. Never deploy a mutable tag.",
        "Apply only the approved saved Terraform plan; drift or state change means re-plan and re-approve.",
        "AWS LB Controller owns Kong-fronting ALBs; Terraform must not also declare them. Helm and Terraform never own the same workload.",
        "Expand/contract migrations. Roll back only to approved digests with proven DB compatibility; otherwise roll forward.",
    ]
    y = 265
    for i, n in enumerate(notes):
        d.add_text(f"n{i}", "• " + n, 1230, y, 440, 110, parent="rules", size=12)
        y += 120

    d.edge("pr", "reviewed", "flow", "review + merge")
    d.edge("reviewed", "build", "flow", "")
    d.edge("build", "approval", "flow", "")
    d.edge("build", "ecr", "flow", "publish (artifact role)", exit=(0.3, 1), entry=(0.5, 0), points=[(729, 240), (154, 240)])
    d.edge("approval", "runner", "flow", "", exit=(0.3, 1), entry=(0.5, 0), points=[(1009, 245), (584, 245)])
    d.edge("runner", "sts", "deploy", "assume role")
    d.edge("sts", "f", "deploy", "foundation role", exit=(0.2, 1), entry=(0.5, 0), points=[(970, 440), (220, 440)])
    d.edge("sts", "infra", "deploy", "app-infra role", exit=(0.5, 1), entry=(0.5, 0), points=[(984, 460), (600, 460)])
    d.edge("sts", "app", "deploy", "app-code role + RBAC", exit=(0.8, 1), entry=(0.5, 0), points=[(998, 470), (990, 470)])
    d.edge("ecr", "app", "flow", "same verified digests", exit=(1, 0.5), entry=(0, 0.5), points=[(400, 324), (400, 480), (810, 480), (810, 570)])
    d.edge("f", "platform", "flow", "")
    d.edge("f", "infra", "control", "versioned outputs")
    d.edge("platform", "app", "control", "Gateway + policy contract", exit=(1, 0.8), entry=(0.2, 1), points=[(410, 708), (410, 630), (894, 630)])
    d.edge("platform", "state", "control", "")
    d.edge("infra", "aur", "flow", "", exit=(0.2, 1), entry=(0.5, 0))
    d.edge("infra", "sqs", "flow", "", exit=(0.5, 1), entry=(0.5, 0))
    d.edge("infra", "sec", "flow", "", exit=(0.8, 1), entry=(0.5, 0))
    d.edge("app", "eks", "flow", "helm upgrade")
    d.edge("eks", "verify", "flow", "", exit=(0.5, 1), entry=(0.87, 0))
    d.edge("independent", "eks", "fenced", "", exit=(1, 0.5), entry=(1, 0.5), points=[(1190, 1030), (1190, 704)])
    return d


if __name__ == "__main__":
    ok = all([build(dr(), OUT, WORK), build(hybrid(), OUT, WORK), build(pipelines(), OUT, WORK)])
    sys.exit(0 if ok else 1)
