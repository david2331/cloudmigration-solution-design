import html
import os
import re
import subprocess
import sys

DARK = "#232F3E"

SVC = {
    "eks": ("eks", "#ED7100"), "ecr": ("ecr", "#ED7100"), "lambda": ("lambda", "#ED7100"),
    "fargate": ("fargate", "#ED7100"), "ecs": ("ecs", "#ED7100"),
    "aurora": ("aurora", "#C925D1"), "rds": ("rds", "#C925D1"), "dms": ("database_migration_service", "#C925D1"),
    "sqs": ("sqs", "#E7157B"), "mq": ("mq", "#E7157B"),
    "s3": ("s3", "#7AA116"), "backup": ("backup", "#7AA116"),
    "waf": ("waf", "#DD344C"), "shield": ("shield", "#DD344C"), "nfw": ("network_firewall", "#DD344C"),
    "kms": ("key_management_service", "#DD344C"), "secrets": ("secrets_manager", "#DD344C"),
    "guardduty": ("guardduty", "#DD344C"), "sechub": ("security_hub", "#DD344C"),
    "iam": ("identity_and_access_management", "#DD344C"), "idc": ("single_sign_on", "#DD344C"),
    "pca": ("private_certificate_authority", "#DD344C"), "cloudhsm": ("cloudhsm", "#DD344C"),
    "paycrypto": ("payment_cryptography", "#DD344C"), "inspector": ("inspector", "#DD344C"),
    "route53": ("route_53", "#8C4FFF"), "dx": ("direct_connect", "#8C4FFF"), "tgw": ("transit_gateway", "#8C4FFF"),
    "vpn": ("site_to_site_vpn", "#8C4FFF"), "arc": ("application_recovery_controller", "#8C4FFF"),
    "cloudtrail": ("cloudtrail", "#E7157B"), "cloudwatch": ("cloudwatch_2", "#E7157B"), "config": ("config", "#E7157B"),
    "orgs": ("organizations", "#E7157B"), "controltower": ("control_tower", "#E7157B"),
    "fis": ("fault_injection_simulator", "#E7157B"), "ssm": ("systems_manager", "#E7157B"),
    "transfer": ("transfer_family", "#01A88D"), "cur": ("cost_and_usage_report", "#7AA116"),
}

RES = {
    "alb": ("application_load_balancer", "#8C4FFF"), "nat": ("nat_gateway", "#8C4FFF"),
    "igw": ("internet_gateway", "#8C4FFF"), "endpoints": ("endpoints", "#8C4FFF"),
    "tgw_att": ("transit_gateway_attachment", "#8C4FFF"), "cgw": ("customer_gateway", "#8C4FFF"),
    "vpn_conn": ("vpn_connection", "#8C4FFF"), "resolver": ("route_53_resolver", "#8C4FFF"),
    "routing_controls": ("route_53_routing_controls", "#8C4FFF"), "readiness": ("route_53_readiness_checks", "#8C4FFF"),
    "flow_logs": ("flow_logs", "#8C4FFF"), "hosted_zone": ("hosted_zone", "#8C4FFF"),
    "aurora_inst": ("aurora_instance", "#C925D1"), "replica": ("db_instance_read_replica", "#C925D1"),
    "queue": ("queue", "#E7157B"), "alarm": ("alarm", "#E7157B"),
    "bucket": ("bucket", "#7AA116"), "vault": ("vault", "#7AA116"),
    "role": ("role", "#DD344C"), "sts": ("sts", "#DD344C"), "padlock": ("ssl_padlock", "#DD344C"),
    "policy": ("policy", "#DD344C"), "dek": ("data_encryption_key", "#DD344C"), "permissions": ("permissions", "#DD344C"),
    "image": ("container_registry_image", "#ED7100"),
    "users": ("users", DARK), "user": ("user", DARK), "client": ("client", DARK), "mobile": ("mobile_client", DARK),
    "dc": ("corporate_data_center", DARK), "server": ("traditional_server", DARK), "bank": ("bank", DARK),
    "office": ("office_building", DARK), "internet": ("internet_alt1", DARK), "generic": ("generic", DARK),
}

K8S = {"pod", "deploy", "svc", "ing", "netpol", "ns", "job", "crd", "control_plane", "sa", "secret", "api", "c_m", "node"}

GROUPS = {
    "cloud": ("shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_aws_cloud_alt;strokeColor=#232F3E;fillColor=none;fontColor=#232F3E;dashed=0;", True),
    "region": ("shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_region;strokeColor=#00A4A6;fillColor=none;fontColor=#147EBA;dashed=1;", True),
    "account": ("shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_account;strokeColor=#CD2264;fillColor=none;fontColor=#CD2264;dashed=0;", True),
    "vpc": ("shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_vpc2;strokeColor=#8C4FFF;fillColor=none;fontColor=#8C4FFF;dashed=0;", True),
    "private_subnet": ("shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;grStroke=0;strokeColor=#00A4A6;fillColor=#E6F6F7;fontColor=#147EBA;dashed=0;", True),
    "public_subnet": ("shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_security_group;grStroke=0;strokeColor=#7AA116;fillColor=#F2F6E8;fontColor=#248814;dashed=0;", True),
    "dc": ("shape=mxgraph.aws4.group;grIcon=mxgraph.aws4.group_corporate_data_center;strokeColor=#7D8998;fillColor=none;fontColor=#5A6C86;dashed=0;", True),
    "az": ("fillColor=none;strokeColor=#147EBA;dashed=1;fontColor=#147EBA;", False),
    "sg": ("fillColor=none;strokeColor=#DD3522;dashed=1;fontColor=#DD3522;", False),
    "ou": ("fillColor=#F7F7F7;strokeColor=#CD2264;dashed=1;fontColor=#CD2264;", False),
    "eks": ("fillColor=none;strokeColor=#ED7100;dashed=1;fontColor=#ED7100;", False),
    "ns": ("fillColor=#EEF3FC;strokeColor=#326CE5;dashed=1;fontColor=#326CE5;", False),
    "external": ("fillColor=#FFF8EF;strokeColor=#D79B00;dashed=0;fontColor=#9A6700;", False),
    "trust": ("fillColor=#FDF1F1;strokeColor=#B85450;dashed=1;fontColor=#B85450;", False),
    "plain": ("fillColor=#F7F7F7;strokeColor=#999999;dashed=0;fontColor=#333333;", False),
    "github": ("fillColor=#F6F8FA;strokeColor=#24292F;dashed=0;fontColor=#24292F;", False),
}

BOX = {
    "blue": "fillColor=#dae8fc;strokeColor=#6c8ebf;",
    "green": "fillColor=#d5e8d4;strokeColor=#82b366;",
    "yellow": "fillColor=#fff2cc;strokeColor=#d6b656;",
    "orange": "fillColor=#ffe6cc;strokeColor=#d79b00;",
    "red": "fillColor=#f8cecc;strokeColor=#b85450;",
    "purple": "fillColor=#e1d5e7;strokeColor=#9673a6;",
    "grey": "fillColor=#f5f5f5;strokeColor=#666666;",
    "white": "fillColor=#ffffff;strokeColor=#666666;",
}

EDGE = {
    "flow": "strokeColor=#232F3E;strokeWidth=1.5;endArrow=block;endFill=1;",
    "hybrid": "strokeColor=#8C4FFF;strokeWidth=1.5;endArrow=block;endFill=1;",
    "async": "strokeColor=#C925D1;strokeWidth=1.5;dashed=1;endArrow=block;endFill=1;",
    "control": "strokeColor=#147EBA;strokeWidth=1.2;dashed=1;dashPattern=4 3;endArrow=open;endFill=0;",
    "deploy": "strokeColor=#ED7100;strokeWidth=1.5;endArrow=block;endFill=1;",
    "security": "strokeColor=#DD344C;strokeWidth=1.2;dashed=1;endArrow=open;endFill=0;",
    "backup": "strokeColor=#7AA116;strokeWidth=1.5;dashed=1;endArrow=block;endFill=1;",
    "fenced": "strokeColor=#B85450;strokeWidth=1.5;dashed=1;dashPattern=8 4;endArrow=block;endFill=1;",
    "line": "strokeColor=#666666;strokeWidth=1;endArrow=none;",
}

CHAR_W = 6.4
LINE_H = 15


def _plain(text):
    return [re.sub(r"<[^>]+>", "", html.unescape(t)) for t in re.split(r"<br\s*/?>", text)]


def text_size(text, font=12, wrap_width=None):
    lines = _plain(text)
    cw = CHAR_W * font / 12
    lh = LINE_H * font / 12
    if wrap_width:
        n = 0
        for l in lines:
            words, cur, cnt = l.split(), 0, 1
            for w_ in words:
                ww = (len(w_) + 1) * cw
                if cur + ww > wrap_width and cur > 0:
                    cnt += 1
                    cur = ww
                else:
                    cur += ww
            n += cnt
        return min(wrap_width, max((len(l) for l in lines), default=0) * cw), n * lh
    w = max((len(l) for l in lines), default=0) * cw
    return w, len(lines) * lh


class Diagram:
    def __init__(self, name, title, width, height):
        self.name, self.title, self.W, self.H = name, title, width, height
        self.cells = {}
        self.order = []
        self.edges = []
        self.add_text("title", title, 20, 10, width - 40, 30, size=20, bold=True, align="left")

    def _add(self, cid, kind, x, y, w, h, parent, style, value, extra=None):
        if cid in self.cells:
            raise ValueError("duplicate id " + cid)
        self.cells[cid] = dict(id=cid, kind=kind, x=x, y=y, w=w, h=h, parent=parent, style=style, value=value, **(extra or {}))
        self.order.append(cid)
        return cid

    def group(self, cid, kind, label, x, y, w, h, parent=None, font=12):
        style, iconic = GROUPS[kind]
        base = "points=[[0,0],[0.25,0],[0.5,0],[0.75,0],[1,0],[1,0.25],[1,0.5],[1,0.75],[1,1],[0.75,1],[0.5,1],[0.25,1],[0,1],[0,0.75],[0,0.5],[0,0.25]];outlineConnect=0;gradientColor=none;html=1;whiteSpace=wrap;fontStyle=1;container=1;pointerEvents=0;collapsible=0;recursiveResize=0;verticalAlign=top;align=left;"
        style = base + style + ("spacingLeft=30;" if iconic else "spacingLeft=8;spacingTop=2;") + f"fontSize={font};"
        return self._add(cid, "group", x, y, w, h, parent, style, label)

    def svc(self, cid, key, label, x, y, parent=None, size=48, font=12):
        name, color = SVC[key]
        style = f"sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor={color};strokeColor=#ffffff;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize={font};fontStyle=0;aspect=fixed;shape=mxgraph.aws4.resourceIcon;resIcon=mxgraph.aws4.{name};"
        return self._add(cid, "icon", x, y, size, size, parent, style, label, dict(min_paths=2, font=font))

    def res(self, cid, key, label, x, y, parent=None, size=48, font=12):
        name, color = RES[key]
        style = f"sketch=0;outlineConnect=0;fontColor=#232F3E;gradientColor=none;fillColor={color};strokeColor=none;dashed=0;verticalLabelPosition=bottom;verticalAlign=top;align=center;html=1;fontSize={font};fontStyle=0;aspect=fixed;pointerEvents=1;shape=mxgraph.aws4.{name};"
        return self._add(cid, "icon", x, y, size, size, parent, style, label, dict(min_paths=1, font=font))

    def k8s(self, cid, key, label, x, y, parent=None, size=48, font=12):
        assert key in K8S
        style = f"aspect=fixed;html=1;dashed=0;whiteSpace=wrap;fillColor=#326CE5;strokeColor=#ffffff;verticalLabelPosition=bottom;verticalAlign=top;align=center;fontSize={font};fontColor=#232F3E;outlineConnect=0;shape=mxgraph.kubernetes.icon2;prIcon={key};"
        return self._add(cid, "icon", x, y, size, size * 0.97, parent, style, label, dict(min_paths=2, font=font))

    def github(self, cid, label, x, y, parent=None, size=48, font=12):
        style = f"dashed=0;outlineConnect=0;html=1;align=center;labelPosition=center;verticalLabelPosition=bottom;verticalAlign=top;fontSize={font};fontColor=#232F3E;shape=mxgraph.weblogos.github;"
        return self._add(cid, "icon", x, y, size, size, parent, style, label, dict(min_paths=1, font=font))

    def box(self, cid, label, x, y, w, h, color="blue", parent=None, font=12, bold=False, rounded=True, align="center", dashed=False):
        style = f"rounded={1 if rounded else 0};whiteSpace=wrap;html=1;arcSize=8;{BOX[color]}fontSize={font};fontColor=#232F3E;align={align};verticalAlign=middle;spacing=6;" + ("fontStyle=1;" if bold else "") + ("dashed=1;" if dashed else "")
        return self._add(cid, "box", x, y, w, h, parent, style, label, dict(font=font))

    def diamond(self, cid, label, x, y, w, h, color="yellow", parent=None, font=12):
        style = f"rhombus;whiteSpace=wrap;html=1;{BOX[color]}fontSize={font};fontColor=#232F3E;"
        return self._add(cid, "diamond", x, y, w, h, parent, style, label, dict(font=font))

    def add_text(self, cid, label, x, y, w, h, parent=None, size=12, bold=False, align="left", color="#232F3E"):
        style = f"text;html=1;whiteSpace=wrap;strokeColor=none;fillColor=none;align={align};verticalAlign=middle;fontSize={size};fontColor={color};" + ("fontStyle=1;" if bold else "")
        return self._add(cid, "text", x, y, w, h, parent, style, label, dict(font=size))

    def badge(self, cid, num, x, y, parent=None, color="#232F3E"):
        style = f"ellipse;html=1;whiteSpace=wrap;fillColor={color};strokeColor=none;fontColor=#ffffff;fontStyle=1;fontSize=11;align=center;verticalAlign=middle;"
        return self._add(cid, "badge", x, y, 20, 20, parent, style, str(num), dict(font=11))

    def edge(self, src, dst, kind="flow", label="", points=None, style_extra="", ortho=True, exit=None, entry=None, both=False):
        st = EDGE[kind] + "html=1;fontSize=11;fontColor=#232F3E;labelBackgroundColor=#ffffff;rounded=1;"
        if ortho:
            st += "edgeStyle=orthogonalEdgeStyle;"
        if exit:
            st += f"exitX={exit[0]};exitY={exit[1]};exitDx=0;exitDy=0;"
        if entry:
            st += f"entryX={entry[0]};entryY={entry[1]};entryDx=0;entryDy=0;"
        if both:
            st += "startArrow=block;startFill=1;"
        st += style_extra
        eid = f"e{len(self.edges)}"
        self.edges.append(dict(id=eid, src=src, dst=dst, style=st, value=label, points=points or []))
        return eid

    def legend(self, x, y, items, parent=None, title="Legend", width=None):
        width = width or 300
        rows = len(items)
        gid = self.group("legend", "plain", title, x, y, width, 34 + rows * 22, parent=parent)
        for i, (kind, text) in enumerate(items):
            yy = y + 30 + i * 22
            a = self.add_text(f"lg_a{i}", "", x + 10, yy + 4, 2, 2, parent=gid)
            b = self.add_text(f"lg_b{i}", "", x + 56, yy + 4, 2, 2, parent=gid)
            self.cells[a]["legend_anchor"] = True
            self.cells[b]["legend_anchor"] = True
            self.edge(a, b, kind, ortho=False, style_extra="noEdgeStyle=1;")
            self.add_text(f"lg_t{i}", text, x + 66, yy - 4, width - 76, 18, parent=gid, size=11)
        return gid

    def abs_of(self, cid):
        c = self.cells[cid]
        return c["x"], c["y"]

    def ancestors(self, cid):
        out = []
        p = self.cells[cid]["parent"]
        while p:
            out.append(p)
            p = self.cells[p]["parent"]
        return out

    def common_parent(self, a, b):
        aa = [a] + self.ancestors(a)
        bb = set([b] + self.ancestors(b))
        for x in aa[1:] if a in bb else aa:
            if x in bb and self.cells[x]["kind"] == "group":
                return x
        return None

    def to_xml(self):
        out = ['<mxfile host="drawio" type="device"><diagram id="%s" name="%s"><mxGraphModel dx="0" dy="0" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="%d" pageHeight="%d" math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>' % (self.name, html.escape(self.title, quote=True), self.W, self.H)]
        for cid in self.order:
            c = self.cells[cid]
            px, py = (0, 0)
            if c["parent"]:
                px, py = self.abs_of(c["parent"])
            par = c["parent"] or "1"
            out.append('<mxCell id="%s" value="%s" style="%s" vertex="1" parent="%s"><mxGeometry x="%g" y="%g" width="%g" height="%g" as="geometry"/></mxCell>' % (
                cid, html.escape(c["value"], quote=True), c["style"], par, c["x"] - px, c["y"] - py, c["w"], c["h"]))
        for e in self.edges:
            par = self.common_parent(e["src"], e["dst"])
            ox, oy = self.abs_of(par) if par else (0, 0)
            pts = ""
            if e["points"]:
                pts = '<Array as="points">' + "".join('<mxPoint x="%g" y="%g"/>' % (x - ox, y - oy) for x, y in e["points"]) + "</Array>"
            out.append('<mxCell id="%s" value="%s" style="%s" edge="1" parent="%s" source="%s" target="%s"><mxGeometry relative="1" as="geometry">%s</mxGeometry></mxCell>' % (
                e["id"], html.escape(e["value"], quote=True), e["style"], par or "1", e["src"], e["dst"], pts))
        out.append("</root></mxGraphModel></diagram></mxfile>")
        return "".join(out)

    def bboxes(self):
        boxes = {}
        for cid, c in self.cells.items():
            if c.get("legend_anchor"):
                continue
            shape = (c["x"], c["y"], c["x"] + c["w"], c["y"] + c["h"])
            label = None
            if c["kind"] == "icon" and c["value"]:
                tw, th = text_size(c["value"], c.get("font", 12))
                cx = c["x"] + c["w"] / 2
                label = (cx - tw / 2, c["y"] + c["h"] + 1, cx + tw / 2, c["y"] + c["h"] + 3 + th)
            boxes[cid] = (shape, label)
        return boxes

    def lint(self):
        errs = []
        ids = set(self.cells)
        for e in self.edges:
            for k in ("src", "dst"):
                if e[k] not in ids:
                    errs.append(f"edge {e['id']} references missing {e[k]}")
        bb = self.bboxes()

        def ov(a, b, m=0):
            return a[0] < b[2] - m and b[0] < a[2] - m and a[1] < b[3] - m and b[1] < a[3] - m

        def inside(a, b):
            return a[0] >= b[0] - 0.5 and a[1] >= b[1] - 0.5 and a[2] <= b[2] + 0.5 and a[3] <= b[3] + 0.5

        for cid, (shape, label) in bb.items():
            c = self.cells[cid]
            if c["parent"]:
                p = bb[c["parent"]][0]
                if not inside(shape, p):
                    errs.append(f"{cid} shape outside parent {c['parent']}")
                if label and not inside(label, p):
                    errs.append(f"{cid} label outside parent {c['parent']} by {max(p[0]-label[0], label[2]-p[2], label[3]-p[3]):.0f}px")
                if shape[1] < p[1] + 26 and self.cells[c["parent"]]["kind"] == "group":
                    errs.append(f"{cid} intrudes into title bar of {c['parent']}")
            if shape[2] > self.W or shape[3] > self.H:
                errs.append(f"{cid} beyond page {self.W}x{self.H}")
            if c["kind"] in ("box", "diamond", "text") and c["value"] and cid != "title":
                slack = 12 if c["kind"] != "diamond" else c["w"] * 0.45
                avail = c["w"] - slack
                tw, th = text_size(c["value"], c.get("font", 12), wrap_width=avail)
                longest = max((len(w_) for l in _plain(c["value"]) for w_ in l.split()), default=0) * CHAR_W * c.get("font", 12) / 12
                if longest > avail + 2:
                    errs.append(f"{cid} word too wide ({longest:.0f} > {avail:.0f})")
                if th > c["h"] - (2 if c["kind"] == "text" else 6) + 1:
                    errs.append(f"{cid} wrapped text too tall ({th:.0f} > {c['h']})")
        keys = list(bb)
        for i, a in enumerate(keys):
            for b in keys[i + 1:]:
                ca, cb = self.cells[a], self.cells[b]
                anc_a, anc_b = self.ancestors(a), self.ancestors(b)
                if b in anc_a or a in anc_b:
                    continue
                sa, la = bb[a]
                sb, lb = bb[b]
                parts_a = [("shape", sa)] + ([("label", la)] if la else [])
                parts_b = [("shape", sb)] + ([("label", lb)] if lb else [])
                for na, ra in parts_a:
                    for nb, rb in parts_b:
                        if ov(ra, rb, 1):
                            errs.append(f"overlap {a}.{na} x {b}.{nb}")
        return errs

    def write(self, outdir):
        os.makedirs(outdir, exist_ok=True)
        path = os.path.join(outdir, self.name + ".drawio")
        with open(path, "w") as f:
            f.write(self.to_xml())
        return path


def render_checks(d, drawio_path, workdir):
    errs = []
    svg = os.path.join(workdir, d.name + ".svg")
    subprocess.run(["drawio", "-x", "-f", "svg", "-b", "0", "-o", svg, drawio_path], capture_output=True, timeout=180)
    s = open(svg).read()
    groups = {}
    for part in re.split(r'(?=<g data-cell-id=")', s):
        m = re.match(r'<g data-cell-id="([^"]+)"', part)
        if m:
            groups[m.group(1)] = part
    for cid, c in d.cells.items():
        if c["kind"] == "icon":
            n = len(re.findall(r"<path", groups.get(cid, "")))
            if n < c.get("min_paths", 1):
                errs.append(f"icon {cid} renders blank ({n} paths)")
    minx = min([c["x"] for c in d.cells.values()] + [p[0] for e in d.edges for p in e["points"]] or [0])
    miny = min([c["y"] for c in d.cells.values()] + [p[1] for e in d.edges for p in e["points"]] or [0])
    bb = d.bboxes()
    leafs = {k: v for k, v in bb.items() if d.cells[k]["kind"] in ("icon", "box", "diamond", "badge")}
    for e in d.edges:
        g = groups.get(e["id"], "")
        m = re.search(r'<path d="([^"]+)"', g)
        if not m:
            continue
        nums = re.findall(r"[MLQ]|-?\d+(?:\.\d+)?", m.group(1))
        pts = []
        i = 0
        while i < len(nums):
            t = nums[i]
            if t in ("M", "L"):
                pts.append((float(nums[i + 1]), float(nums[i + 2])))
                i += 3
            elif t == "Q":
                pts.append((float(nums[i + 3]), float(nums[i + 4])))
                i += 5
            else:
                i += 1
        abs_pts = [(x + minx, y + miny) for x, y in pts]
        if e["value"] and len(abs_pts) >= 2:
            segs = list(zip(abs_pts, abs_pts[1:]))
            lens = [((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 for (x1, y1), (x2, y2) in segs]
            half, acc = sum(lens) / 2, 0
            mx, my = abs_pts[0]
            for ((x1, y1), (x2, y2)), L in zip(segs, lens):
                if acc + L >= half and L > 0:
                    t = (half - acc) / L
                    mx, my = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
                    break
                acc += L
            tw, th = text_size(e["value"], 11)
            lab = (mx - tw / 2, my - th / 2, mx + tw / 2, my + th / 2)
            texts = {k: v for k, v in bb.items() if d.cells[k]["kind"] == "text" and d.cells[k]["value"] and k != "title"}
            for k, (shape, label) in list(leafs.items()) + list(texts.items()):
                if k in (e["src"], e["dst"]):
                    continue
                for part, r in (("shape", shape), ("label", label)):
                    if r and lab[0] < r[2] and r[0] < lab[2] and lab[1] < r[3] and r[1] < lab[3]:
                        errs.append(f"edge label '{e['value']}' of {e['id']} overlaps {k}.{part}")
        skip = {e["src"], e["dst"]} | set(d.ancestors(e["src"])) | set(d.ancestors(e["dst"]))
        for k, (shape, label) in leafs.items():
            if k in skip:
                continue
            for part, r in (("shape", shape), ("label", label)):
                if not r:
                    continue
                r2 = (r[0] + 2, r[1] + 2, r[2] - 2, r[3] - 2)
                for (x1, y1), (x2, y2) in zip(abs_pts, abs_pts[1:]):
                    if _seg_hits(x1, y1, x2, y2, r2):
                        errs.append(f"edge {e['id']} ({e['src']}->{e['dst']}) crosses {k}.{part}")
                        break
    return errs


def _seg_hits(x1, y1, x2, y2, r):
    if max(x1, x2) < r[0] or min(x1, x2) > r[2] or max(y1, y2) < r[1] or min(y1, y2) > r[3]:
        return False
    steps = int(max(abs(x2 - x1), abs(y2 - y1)) / 2) + 1
    for s in range(steps + 1):
        t = s / steps
        x, y = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        if r[0] < x < r[2] and r[1] < y < r[3]:
            return True
    return False


def build(d, outdir, workdir, png=True):
    errs = d.lint()
    path = d.write(outdir)
    errs += render_checks(d, path, workdir)
    if png and not errs:
        out = os.path.join(outdir, d.name + ".png")
        subprocess.run(["drawio", "-x", "-f", "png", "-s", "2", "-b", "20", "-o", out, path], capture_output=True, timeout=180)
        r = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", out], capture_output=True, text=True)
        dims = re.findall(r"pixel\w+: (\d+)", r.stdout)
        print(f"OK {d.name}: {len(d.cells)} shapes, {len(d.edges)} edges, png {'x'.join(dims)}")
    else:
        print(f"FAIL {d.name}: {len(errs)} issue(s)")
        for x in errs:
            print("  -", x)
    return not errs
