import sys
sys.path.insert(0, "/Users/david/Documents/work/cloudmigration-solution-design/tier1-payments-modernisation/.qwen/tmp/dgen")
from lib import Diagram, build

OUT = "/Users/david/Documents/work/cloudmigration-solution-design/tier1-payments-modernisation/diagrams"
WORK = "/Users/david/Documents/work/cloudmigration-solution-design/tier1-payments-modernisation/.qwen/tmp/dgen"


def accounts():
    d = Diagram("deployment-accounts", "Deployment — account and regional topology (AWS Organization)", 1700, 1000)
    d.group("org", "cloud", "AWS Organization — isolated account boundaries; Control Tower guardrails and SCP region allow-list", 20, 60, 1660, 920)

    d.group("ou_sec", "ou", "Security OU", 40, 100, 380, 300, parent="org")
    d.group("sec", "account", "Security tooling account", 60, 140, 340, 110, parent="ou_sec")
    d.svc("guard", "guardduty", "GuardDuty", 100, 180, parent="sec")
    d.svc("sechub", "sechub", "Security Hub", 280, 180, parent="sec")
    d.group("log", "account", "Log archive account — residency-controlled", 60, 270, 340, 110, parent="ou_sec")
    d.svc("trail", "cloudtrail", "Regional CloudTrail", 100, 310, parent="log")
    d.svc("kmslog", "kms", "Log stores + KMS", 280, 310, parent="log")

    d.group("ou_inf", "ou", "Infrastructure OU", 40, 420, 380, 300, parent="org")
    d.group("net", "account", "Network account(s)", 60, 460, 340, 110, parent="ou_inf")
    d.svc("tgw", "tgw", "Regional TGW", 80, 500, parent="net")
    d.svc("dx", "dx", "DX / VPN", 180, 500, parent="net")
    d.svc("nfw", "nfw", "Network Firewall", 300, 500, parent="net")
    d.group("tools", "account", "Platform tooling account", 60, 590, 340, 110, parent="ou_inf")
    d.svc("ecr", "ecr", "ECR", 80, 630, parent="tools")
    d.res("runner", "server", "Isolated runners", 180, 630, parent="tools")
    d.res("sts", "sts", "Scoped STS", 310, 630, parent="tools")

    d.group("ou_prod", "ou", "Production OU", 440, 100, 1220, 620, parent="org")
    for i, ent in enumerate("ab"):
        y = 140 + i * 290
        d.group(f"prod{ent}", "account", f"entity-{ent}-prod workload account", 460, y, 780, 270, parent="ou_prod")
        d.group(f"p{ent}", "region", "P: Malaysia ap-southeast-5", 480, y + 40, 360, 210, parent=f"prod{ent}")
        d.svc(f"peks{ent}", "eks", "EKS + DB-less<br>Kong, 3 AZs", 520, y + 90, parent=f"p{ent}")
        d.svc(f"paur{ent}", "aurora", "Aurora primary", 660, y + 90, parent=f"p{ent}")
        d.svc(f"psqs{ent}", "sqs", "Local SQS / S3", 770, y + 90, parent=f"p{ent}")
        d.group(f"r{ent}", "region", "R: Singapore ap-southeast-1", 860, y + 40, 360, 210, parent=f"prod{ent}")
        d.svc(f"reks{ent}", "eks", "EKS + Kong<br>submitters fenced", 890, y + 90, parent=f"r{ent}")
        d.svc(f"raur{ent}", "aurora", "Aurora secondary", 1040, y + 90, parent=f"r{ent}")
        d.svc(f"rsqs{ent}", "sqs", "Local SQS / S3", 1150, y + 90, parent=f"r{ent}")
        d.group(f"rec{ent}", "account", f"entity-{ent}-recovery", 1260, y, 380, 270, parent="ou_prod")
        d.svc(f"bkp{ent}", "backup", "AWS Backup<br>Vault Lock", 1320, y + 90, parent=f"rec{ent}")
        d.res(f"vault{ent}", "vault", "Isolated clean-room<br>VPC", 1500, y + 90, parent=f"rec{ent}")

    d.group("ou_np", "ou", "Non-production OU", 440, 740, 600, 220, parent="org")
    d.group("npa", "account", "entity-a-nonprod", 460, 780, 270, 160, parent="ou_np")
    d.svc("npeksa", "eks", "EKS (no prod data)", 570, 830, parent="npa")
    d.group("npb", "account", "entity-b-nonprod", 750, 780, 270, 160, parent="ou_np")
    d.svc("npeksb", "eks", "EKS (no prod data)", 860, 830, parent="npb")
    d.group("ou_sb", "ou", "Sandbox OU — no regulated production data", 1060, 740, 280, 220, parent="org")
    d.add_text("sbnote", "Experimentation only; SCPs block access to production accounts and regulated data.", 1080, 790, 240, 90, parent="ou_sb", size=11)

    d.legend(1360, 740, [
        ("async", "Aurora Global DB (async)"),
        ("backup", "Approved backup copies"),
        ("hybrid", "Segmented TGW attachment"),
        ("deploy", "Role + EKS RBAC deploy"),
    ], parent="org", width=300)

    for ent in "ab":
        d.edge(f"paur{ent}", f"raur{ent}", "async", "asynchronous", exit=(0.5, 1), entry=(0.5, 1), points=[(684, 140 + "ab".index(ent) * 290 + 235), (1064, 140 + "ab".index(ent) * 290 + 235)])
    d.edge("paura", "bkpa", "backup", "approved copies", exit=(0.5, 0), entry=(0.5, 0), points=[(684, 205), (1344, 205)])
    d.edge("paurb", "bkpb", "backup", "approved copies", exit=(0.5, 0), entry=(0.5, 0), points=[(684, 495), (1344, 495)])
    d.edge("nfw", "peksa", "hybrid", "entity A attachment", exit=(1, 0.3), entry=(0, 0.5), points=[(426, 514), (426, 254)])
    d.edge("nfw", "peksb", "hybrid", "entity B attachment", exit=(1, 0.7), entry=(0, 0.5), points=[(434, 534), (434, 544)])
    d.edge("sts", "peksb", "deploy", "role + EKS RBAC", exit=(1, 0.5), entry=(0.5, 1), points=[(444, 654), (444, 690), (534, 690)])
    return d


def cell():
    d = Diagram("deployment-regional-cell", "Deployment — regional cell (repeat independently for each entity and region)", 1700, 1120)

    d.group("ext", "external", "Callers", 20, 60, 1180, 120)
    d.res("clients", "users", "Internet clients", 160, 92, parent="ext")
    d.res("hybrid", "dc", "Hybrid clients via regional<br>TGW (private routes only)", 860, 92, parent="ext")

    d.group("acct", "account", "One entity workload account — one region", 20, 194, 1180, 906)
    d.svc("cp", "eks", "AWS-managed EKS control<br>plane (outside VPC)", 1080, 230, parent="acct")
    d.group("vpc", "vpc", "Customer VPC — SG / subnet / NetworkPolicy boundaries", 40, 230, 980, 850, parent="acct")
    d.group("ing", "public_subnet", "Ingress subnets spanning AZ-a / AZ-b / AZ-c", 60, 270, 940, 130, parent="vpc")
    d.svc("waf", "waf", "AWS WAF", 110, 310, parent="ing")
    d.res("pub", "alb", "Internet-facing ALB<br>(LB Controller)", 290, 310, parent="ing")
    d.res("priv", "alb", "Private internal ALB<br>(LB Controller)", 760, 310, parent="ing")

    for i, az in enumerate("abc"):
        x = 60 + i * 320
        d.group(f"az{az}", "az", f"AZ-{az} — private compute and DB subnets", x, 420, 300, 330, parent="vpc")
        d.k8s(f"kong{az}", "pod", "Kong replica", x + 40, 470, parent=f"az{az}")
        d.k8s(f"app{az}", "pod", "Payment pods<br>(ClusterIP)", x + 200, 470, parent=f"az{az}")
        label = "Aurora writer<br>(active region)" if az == "a" else "Aurora reader /<br>failover candidate"
        d.res(f"db{az}", "aurora_inst" if az == "a" else "replica", label, x + 126, 620, parent=f"az{az}")

    d.group("plat", "plain", "Platform controllers and shared VPC services", 60, 770, 940, 290, parent="vpc")
    d.k8s("ctrl", "control_plane", "KIC + AWS LB Controller<br>(spread across AZs)", 110, 810, parent="plat")
    d.k8s("admin", "api", "Private Kong Admin API<br>(KIC + platform only)", 330, 810, parent="plat")
    d.res("storage", "aurora_inst", "Aurora cluster storage<br>(replicated across 3 AZs)", 560, 810, parent="plat")
    d.res("ep", "endpoints", "Private VPC endpoints:<br>S3, ECR, SQS, Secrets, STS", 800, 810, parent="plat")
    d.add_text("platnote", "Payment pods reach the writer through the cluster endpoint; readers are failover capacity, not authoritative reads.", 80, 960, 900, 40, parent="plat", size=11)

    d.group("svcs", "plain", "Regional AWS services", 1040, 470, 140, 610, parent="acct")
    d.svc("sqs", "sqs", "SQS", 1086, 510, parent="svcs")
    d.svc("s3", "s3", "S3", 1086, 620, parent="svcs")
    d.svc("ecr", "ecr", "ECR", 1086, 730, parent="svcs")
    d.svc("secrets", "secrets", "Secrets<br>Manager", 1086, 840, parent="svcs")
    d.svc("kms", "kms", "KMS", 1086, 970, parent="svcs")

    d.legend(1220, 60, [
        ("flow", "HTTPS / TLS request path"),
        ("hybrid", "Private hybrid ingress"),
        ("control", "Control / configuration"),
        ("async", "Storage replication"),
        ("security", "IAM / endpoint policy"),
    ], width=460)
    d.group("notes", "plain", "Availability and implementation constraints", 1220, 230, 460, 870)
    notes = [
        "At least three ready Kong replicas spread across AZs with topology spread, PDBs and tested spare capacity for one AZ loss. Replica count alone is not resilience.",
        "Platform owns Gateway/GatewayClass, allowedRoutes, baseline plugins and private Kong administration; applications own namespaced HTTPRoutes only.",
        "Kong -> application hop is TLS/mTLS. No Amazon API Gateway or Konnect. DB-less uses Git/Kubernetes desired state, not decK sync.",
        "Aurora has a single regional writer; storage replicates across AZs. Global Database to R is asynchronous: AZ-loss zero loss is not regional zero RPO.",
        "In R before promotion: Aurora secondary readers replace the writer and payment submitters stay disabled; everything else is pre-provisioned.",
        "Terraform owns AWS provisioning; Helm owns Kubernetes workloads; LB Controller owns its ALBs. Never declare a resource twice.",
        "AZ-a/b/c are logical slots: map actual AZ IDs per account. Confirm EKS, endpoint, backup and engine support in both regions (S6, S33).",
    ]
    y = 265
    for i, n in enumerate(notes):
        d.add_text(f"n{i}", "• " + n, 1230, y, 440, 100, parent="notes", size=12)
        y += 115

    d.edge("clients", "waf", "flow", "HTTPS", exit=(0.5, 1), entry=(0.5, 0), points=[(184, 250), (134, 250)])
    d.edge("waf", "pub", "flow", "WAF inspection")
    d.edge("hybrid", "priv", "hybrid", "HTTPS, internal DNS", exit=(0.5, 1), entry=(0.5, 0), points=[(884, 250), (784, 250)])
    for az in "abc":
        x = 60 + "abc".index(az) * 320
        d.edge("pub", f"kong{az}", "flow", "TLS" if az == "a" else "", exit=(0.5, 1), entry=(0.5, 0), points=[(314, 410), (x + 64, 410)])
        d.edge("priv", f"kong{az}", "hybrid", "", exit=(0.5, 1), entry=(0.75, 0), points=[(784, 414), (x + 76, 414)])
        d.edge(f"kong{az}", f"app{az}", "flow", "mTLS")
        d.edge(f"app{az}", "dba", "flow", "writer endpoint" if az == "a" else "", exit=(0.5, 1), entry=(1, 0.5) if az != "a" else (0.5, 0), points=[(x + 224, 600), (230, 600)] if az == "a" else [(x + 224, 580), (240, 580), (240, 644)])
        d.edge(f"db{az}", "storage", "async", "", exit=(0.5, 1), entry=(0.5, 0), points=[(x + 150, 760), (584, 760)])
    d.edge("ctrl", "admin", "control", "private config path")
    d.edge("cp", "appc", "control", "managed API / nodes", exit=(0.5, 1), entry=(1, 0.5), points=[(1104, 450), (1030, 450), (1030, 494)])
    d.edge("ep", "sqs", "security", "endpoint policy", exit=(1, 0.5), entry=(0, 0.5), points=[(1030, 834), (1030, 534)])
    return d


if __name__ == "__main__":
    ok = all([build(accounts(), OUT, WORK), build(cell(), OUT, WORK)])
    sys.exit(0 if ok else 1)
