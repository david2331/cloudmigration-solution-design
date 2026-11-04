import sys
sys.path.insert(0, "/Users/david/Documents/work/cloudmigration-solution-design/tier1-payments-modernisation/.qwen/tmp/dgen")
from lib import Diagram, build

OUT = "/Users/david/Documents/work/cloudmigration-solution-design/tier1-payments-modernisation/diagrams"
WORK = "/Users/david/Documents/work/cloudmigration-solution-design/tier1-payments-modernisation/.qwen/tmp/dgen"


def context():
    d = Diagram("context-diagram", "Payment platform context — AWS only; P = Malaysia ap-southeast-5, R = Singapore ap-southeast-1", 1700, 1180)

    d.group("ext", "external", "External actors and trust boundaries", 20, 60, 1660, 150)
    d.res("public", "users", "Customers / approved<br>internet channels", 80, 100, parent="ext")
    d.res("hybrid", "dc", "On-premises channels<br>and payment operations", 420, 100, parent="ext")
    d.res("rails", "bank", "External payment /<br>settlement partners", 780, 100, parent="ext")
    d.github("gh", "GitHub Actions — external<br>CI/CD trust boundary", 1140, 100, parent="ext")

    d.group("org", "cloud", "AWS Organization — account and residency boundaries", 20, 230, 1660, 930)

    d.group("net", "account", "Network account(s) — region-local connectivity", 40, 270, 360, 300, parent="org")
    d.svc("dx", "dx", "Direct Connect", 80, 320, parent="net")
    d.svc("vpn", "vpn", "Site-to-Site VPN", 250, 320, parent="net")
    d.svc("tgw", "tgw", "Transit Gateway", 80, 450, parent="net")
    d.svc("nfw", "nfw", "Network Firewall", 250, 450, parent="net")

    d.group("tooling", "account", "Platform tooling account — deployment trust", 40, 590, 360, 250, parent="org")
    d.res("runner", "server", "Ephemeral<br>runners", 75, 640, parent="tooling")
    d.res("sts", "sts", "AWS STS /<br>scoped IAM roles", 190, 640, parent="tooling")
    d.svc("ecr", "ecr", "Amazon ECR", 310, 640, parent="tooling")

    d.group("assure", "account", "Security tooling + log archive accounts", 40, 860, 360, 280, parent="org")
    d.svc("trail", "cloudtrail", "CloudTrail", 70, 910, parent="assure")
    d.svc("guard", "guardduty", "GuardDuty", 190, 910, parent="assure")
    d.svc("sechub", "sechub", "Security Hub", 310, 910, parent="assure")
    d.res("logs", "bucket", "Region-local encrypted<br>log stores + KMS", 190, 1040, parent="assure")

    for i, (ent, y) in enumerate((("a", 270), ("b", 600))):
        g = f"acct{ent}"
        d.group(g, "account", f"entity-{ent}-prod — isolated workload account", 420, y, 900, 310, parent="org")
        d.group(f"p{ent}", "region", "P: Malaysia (active)", 440, y + 40, 420, 250, parent=g)
        d.svc(f"waf{ent}", "waf", "WAF", 470, y + 90, parent=f"p{ent}")
        d.res(f"alb{ent}", "alb", "ALB", 570, y + 90, parent=f"p{ent}")
        d.k8s(f"kong{ent}", "pod", "Kong", 670, y + 90, parent=f"p{ent}")
        d.svc(f"eks{ent}", "eks", "EKS services", 770, y + 90, parent=f"p{ent}")
        d.svc(f"aur{ent}", "aurora", "Aurora writer", 520, y + 190, parent=f"p{ent}")
        d.svc(f"sqs{ent}", "sqs", "SQS", 650, y + 190, parent=f"p{ent}")
        d.svc(f"s3{ent}", "s3", "S3", 770, y + 190, parent=f"p{ent}")
        d.group(f"r{ent}", "region", "R: Singapore (pre-provisioned, fenced)", 880, y + 40, 420, 250, parent=g)
        d.svc(f"ralb{ent}", "waf", "WAF + ALB", 910, y + 90, parent=f"r{ent}")
        d.svc(f"reks{ent}", "eks", "EKS + Kong", 1060, y + 90, parent=f"r{ent}")
        d.svc(f"raur{ent}", "aurora", "Aurora secondary", 960, y + 190, parent=f"r{ent}")
        d.svc(f"rsqs{ent}", "sqs", "Local SQS", 1160, y + 190, parent=f"r{ent}")

    d.group("rec", "account", "Entity recovery accounts — not live databases", 420, 930, 900, 210, parent="org")
    d.svc("bkpa", "backup", "Entity A: Backup Vault Lock<br>+ clean-room", 560, 980, parent="rec")
    d.svc("bkpb", "backup", "Entity B: Backup Vault Lock<br>+ clean-room", 960, 980, parent="rec")

    d.legend(1340, 270, [
        ("flow", "Payment / request traffic"),
        ("hybrid", "Hybrid private connectivity"),
        ("async", "Asynchronous replication"),
        ("deploy", "Scoped deployment"),
        ("backup", "Backup copy, independent custody"),
        ("fenced", "Pre-built, fenced until DR"),
        ("security", "Sanitised telemetry / findings"),
    ], parent="org", width=320)

    d.group("notes", "plain", "Trust and responsibility", 1340, 480, 320, 660, parent="org")
    notes = [
        "Workload accounts are separated by legal entity, not by region: each has its own EKS cluster in P and in R.",
        "No default cross-entity routes, shared payment databases or shared Kong instances.",
        "Recovery accounts hold immutable backups and clean-room restores; live Aurora Global Database members stay in the workload account.",
        "Platform owns self-hosted Kong; application teams consume governed routes. No Amazon API Gateway or Konnect.",
        "Logs, backups, artifacts and telemetry need explicit residency, KMS and retention controls; cross-border approval (C05) is not a blanket export permission.",
        "Recovery endpoints exist, but writers and submitters are never active in both regions; traffic switching cannot enforce this.",
    ]
    y = 515
    for i, n in enumerate(notes):
        h = 95 if len(n) > 110 else 80
        d.add_text(f"n{i}", "• " + n, 1350, y, 300, h, parent="notes", size=11)
        y += h + 8

    d.edge("public", "wafa", "flow", "HTTPS / WAF", points=[(104, 220), (494, 220)], exit=(0.5, 1), entry=(0.5, 0))
    d.edge("public", "wafb", "flow", "", points=[(120, 225), (412, 225), (412, 714), (470, 714)], exit=(0.85, 1), entry=(0, 0.5))
    d.edge("wafa", "alba", "flow", "")
    d.edge("alba", "konga", "flow", "")
    d.edge("konga", "eksa", "flow", "")
    d.edge("wafb", "albb", "flow", "")
    d.edge("albb", "kongb", "flow", "")
    d.edge("kongb", "eksb", "flow", "")
    d.edge("hybrid", "dx", "hybrid", "TLS / mTLS over DX / VPN", points=[(444, 245), (104, 245)], exit=(0.5, 1), entry=(0.5, 0))
    d.edge("dx", "tgw", "hybrid", "")
    d.edge("tgw", "nfw", "hybrid", "")
    d.edge("vpn", "nfw", "hybrid", "")
    d.edge("nfw", "alba", "hybrid", "entity A routes", points=[(380, 474), (380, 255), (594, 255)], exit=(1, 0.5), entry=(0.5, 0))
    d.edge("nfw", "albb", "hybrid", "entity B routes", points=[(390, 484), (390, 585), (594, 585)], exit=(1, 0.7), entry=(0.5, 0))
    d.edge("nfw", "ralba", "fenced", "pre-built R paths", points=[(395, 494), (395, 262), (934, 262)], exit=(1, 0.9), entry=(0.5, 0))
    d.edge("aura", "raura", "async", "Aurora Global DB (async)", points=[(544, 555), (984, 555)], exit=(0.5, 1), entry=(0.5, 1))
    d.edge("aurb", "raurb", "async", "Aurora Global DB (async)", points=[(544, 885), (984, 885)], exit=(0.5, 1), entry=(0.5, 1))
    d.edge("gh", "runner", "deploy", "OIDC: exact aud / sub", points=[(1164, 228), (1164, 236), (30, 236), (30, 664)], exit=(0.5, 1), entry=(0, 0.5))
    d.edge("runner", "sts", "deploy", "")
    d.edge("sts", "ecr", "deploy", "")
    d.edge("eksa", "rails", "flow", "idempotent submission", points=[(830, 384), (830, 250), (804, 250)], exit=(1, 0.5), entry=(0.5, 1))
    d.edge("aura", "bkpa", "backup", "", points=[(462, 484), (462, 1004), (560, 1004)], exit=(0, 0.5), entry=(0, 0.5))
    d.edge("aurb", "bkpb", "backup", "approved copies", points=[(544, 920), (984, 920)], exit=(0.5, 1), entry=(0.5, 0))
    d.edge("s3a", "sechub", "security", "", points=[(818, 484), (850, 484), (850, 575), (410, 575), (410, 934)], exit=(1, 0.5), entry=(1, 0.5))
    return d


def logical():
    d = Diagram("logical-architecture", "Logical architecture — one entity workload account, one regional instance (repeat for each entity in P and R)", 1700, 1080)

    d.group("ext", "external", "Callers and partners", 20, 60, 1660, 130)
    d.res("internet", "users", "Internet channels", 120, 90, parent="ext")
    d.res("onprem", "dc", "On-premises consumers<br>via DX / VPN / TGW", 600, 90, parent="ext")
    d.res("partners", "bank", "Payment partners", 1300, 90, parent="ext")

    d.group("acct", "account", "Entity workload account — one region", 20, 210, 1660, 850)
    d.group("ingress", "public_subnet", "VPC ingress boundary — public and private entry points", 40, 250, 1000, 130, parent="acct")
    d.svc("waf", "waf", "AWS WAF web ACL", 90, 290, parent="ingress")
    d.res("alb", "alb", "Internet-facing ALB<br>(LB Controller owned)", 300, 290, parent="ingress")
    d.res("ialb", "alb", "Private internal ALB<br>(LB Controller owned)", 640, 290, parent="ingress")

    d.group("eks", "eks", "Private EKS data plane — AZ-a / AZ-b / AZ-c", 40, 400, 1000, 400, parent="acct")
    d.group("plat", "ns", "Platform namespace — privileged trust boundary", 60, 440, 960, 150, parent="eks")
    d.k8s("kong", "pod", "Self-hosted DB-less Kong<br>(3+ replicas across AZs)", 130, 480, parent="plat")
    d.k8s("kic", "control_plane", "Kong Ingress<br>Controller (KIC)", 380, 480, parent="plat")
    d.k8s("policy", "crd", "GatewayClass / Gateway /<br>allowedRoutes + baseline auth", 600, 480, parent="plat")
    d.k8s("lbc", "deploy", "AWS Load Balancer<br>Controller", 880, 480, parent="plat")

    d.group("app", "ns", "Application namespaces — scoped RBAC", 60, 610, 960, 170, parent="eks")
    d.k8s("route", "ing", "Approved namespaced<br>HTTPRoutes", 110, 650, parent="app")
    d.k8s("svc", "svc", "ClusterIP services -> payment<br>pods (authZ + idempotency)", 380, 650, parent="app")
    d.k8s("workers", "pod", "Outbox publisher / queue<br>workers (fenced submitters)", 720, 650, parent="app")

    d.group("data", "private_subnet", "Private data / AWS service boundary", 40, 820, 1000, 220, parent="acct")
    d.svc("aurora", "aurora", "Aurora PostgreSQL<br>single writer + readers", 90, 870, parent="data")
    d.svc("sqs", "sqs", "Regional SQS + DLQ", 300, 870, parent="data")
    d.svc("s3", "s3", "Private S3 + SSE-KMS", 480, 870, parent="data")
    d.svc("secrets", "secrets", "Secrets Manager / KMS", 660, 870, parent="data")
    d.svc("identity", "iam", "EKS Pod Identity -><br>scoped IAM roles", 860, 870, parent="data")

    d.group("side", "plain", "Egress and observability", 1060, 250, 260, 550, parent="acct")
    d.svc("nfw", "nfw", "Controlled egress via<br>Network Firewall", 1166, 300, parent="side")
    d.svc("cw", "cloudwatch", "CloudWatch metrics /<br>alarms / redacted logs", 1166, 650, parent="side")

    d.legend(1340, 250, [
        ("flow", "Request / data path"),
        ("hybrid", "Private hybrid ingress"),
        ("async", "Asynchronous / at-least-once"),
        ("control", "Control-plane reconciliation"),
        ("security", "Identity / secret access"),
    ], parent="acct", width=320)

    d.group("contracts", "plain", "Controller and security contracts", 1340, 410, 320, 630, parent="acct")
    notes = [
        "<b>Entry:</b> LB Controller owns Kong-fronting ALBs; KIC owns HTTPRoute reconciliation. No two controllers own the same object.",
        "<b>Kong admin:</b> private Admin API reached only by KIC and platform operators. DB-less: no config database, no decK sync.",
        "<b>Route delegation:</b> platform owns GatewayClass, Gateway, allowedRoutes; apps get namespaced HTTPRoutes only.",
        "<b>Bypass prevention:</b> SGs, NetworkPolicy and admission block public LoadBalancer/NodePort services. ClusterIP is not a boundary.",
        "<b>Identity:</b> Kong authentication never replaces application authorisation, entity checks or idempotency.",
        "<b>Semantics:</b> ledger + outbox commit atomically; SQS is regional and not transactional with the commit.",
    ]
    y = 445
    for i, n in enumerate(notes):
        d.add_text(f"c{i}", n, 1350, y, 300, 90, parent="contracts", size=11)
        y += 97

    d.edge("internet", "waf", "flow", "HTTPS", exit=(0.5, 1), entry=(0.5, 0))
    d.edge("waf", "alb", "flow", "")
    d.edge("onprem", "ialb", "hybrid", "private HTTPS", exit=(0.5, 1), entry=(0.5, 0))
    d.edge("alb", "kong", "flow", "TLS, restricted SG", exit=(0.5, 1), entry=(0.5, 0), points=[(324, 420), (154, 420)])
    d.edge("ialb", "kong", "hybrid", "", exit=(0.5, 1), entry=(0.8, 0), points=[(664, 430), (168, 430)])
    d.edge("kong", "svc", "flow", "TLS / mTLS", exit=(0.5, 1), entry=(0, 0.5), points=[(154, 600), (360, 600), (360, 674)])
    d.edge("lbc", "alb", "control", "reconciles ALBs", exit=(0.5, 0), entry=(1, 0.5), points=[(904, 395), (500, 395), (500, 314)])
    d.edge("policy", "kic", "control", "")
    d.edge("route", "kic", "control", "admission", exit=(0.5, 0), entry=(0, 0.8), points=[(134, 620), (340, 620), (340, 518)])
    d.edge("kic", "kong", "control", "private Admin API")
    d.edge("svc", "aurora", "flow", "ledger + outbox (atomic)", exit=(0.5, 1), entry=(0.5, 0), points=[(404, 800), (114, 800)])
    d.edge("workers", "aurora", "flow", "read / mark outbox", exit=(0.2, 1), entry=(0.85, 0), points=[(730, 810), (131, 810)])
    d.edge("workers", "sqs", "async", "publish", exit=(0.5, 1), entry=(0.5, 0), points=[(744, 815), (324, 815)])
    d.edge("workers", "nfw", "flow", "idempotency key", exit=(1, 0.5), entry=(0, 0.5), points=[(1100, 674), (1100, 324)])
    d.edge("nfw", "partners", "flow", "TLS / mTLS", exit=(0.5, 0), entry=(0.5, 1))
    d.edge("svc", "s3", "flow", "", exit=(0.8, 1), entry=(0.5, 0), points=[(418, 790), (504, 790)])
    d.edge("identity", "workers", "security", "service-account roles", exit=(0.5, 0), entry=(0.8, 1))
    d.edge("svc", "secrets", "security", "runtime access", exit=(0.9, 1), entry=(0.5, 0), points=[(423, 805), (684, 805)])
    d.edge("workers", "cw", "async", "", exit=(1, 0.8), entry=(0, 0.5), points=[(1130, 688), (1130, 674)])
    return d


if __name__ == "__main__":
    ok = all([build(context(), OUT, WORK), build(logical(), OUT, WORK)])
    sys.exit(0 if ok else 1)
