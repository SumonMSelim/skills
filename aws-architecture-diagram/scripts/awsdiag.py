#!/usr/bin/env python3
"""awsdiag: tiny SVG toolkit for AWS architecture diagrams with official AWS icons.

Usage as a library (in your spec file):

    from awsdiag import Diagram
    d = Diagram(
        2280,
        1720,
        title="...",
        subtitle="...",
        aria="...",
        theme="standard-light",
        clean_labels=True,
    )
    d.group(...); d.icon(...); d.arrow(...); d.flow(...); d.legend(...)
    d.write(out_dir, name="architecture")   # -> architecture.svg / .html / render.html

Usage as a CLI:

    python awsdiag.py themes                       # list supported themes
    python awsdiag.py icons cloudfront             # search icon file names
    python awsdiag.py icons "kinesis" --all        # include all sizes / variants

Icon root resolution order:
1) Diagram(icon_root="...")
2) $AWS_ICONS
3) bundled folders inside the skill package (e.g. ./icons)
"""
import base64
import glob
import os
import sys

DEFAULT_THEME = "standard-light"

COLORS = {
    "cloud": "#232F3E",
    "region": "#00A4A6",
    "vpc": "#8C4FFF",
    "public_subnet": "#7AA116",
    "private_subnet": "#147EBA",
    "account": "#E7157B",
    "corp": "#7D8998",
    "autoscaling": "#ED7100",
}

SANS = "'IBM Plex Sans', 'Helvetica Neue', Arial, 'Liberation Sans', sans-serif"
MONO = "'IBM Plex Mono', Menlo, Consolas, 'DejaVu Sans Mono', monospace"
HAND = "'Patrick Hand', 'Comic Sans MS', 'Segoe Print', cursive"

THEMES = {
    "standard-light": {
        "hand": False,
        "ink": "#232F3E",
        "slate": "#4A5060",
        "muted": "#6B7280",
        "rust": "#B3541E",
        "bg": "#F5F6F8",
        "panel": "#FFFFFF",
        "panel_stroke": "#D9DCE3",
        "strip_fill": "#FAFAFB",
        "strip_stroke": "#C9CDD6",
        "halo": "#FFFFFF",
        "font_sans": SANS,
        "font_mono": MONO,
    },
    "standard-dark": {
        "hand": False,
        "ink": "#F4F7FB",
        "slate": "#C9D2E3",
        "muted": "#B8C3D8",
        "rust": "#FFB17A",
        "bg": "#0F131A",
        "panel": "#171C24",
        "panel_stroke": "#303846",
        "strip_fill": "#1A202A",
        "strip_stroke": "#3A4559",
        "halo": "#0F131A",
        "font_sans": SANS,
        "font_mono": MONO,
    },
    "hand-drawn-light": {
        "hand": True,
        "ink": "#232F3E",
        "slate": "#596170",
        "muted": "#6E7788",
        "rust": "#A44A1A",
        "bg": "#F6F5F2",
        "panel": "#FFFDF9",
        "panel_stroke": "#D8D3C8",
        "strip_fill": "#F7F3EA",
        "strip_stroke": "#CEC4B4",
        "halo": "#FFFDF9",
        "font_sans": SANS,
        "font_mono": MONO,
    },
    "hand-drawn-dark": {
        "hand": True,
        "ink": "#F7F0DF",
        "slate": "#D8CDB8",
        "muted": "#CFC6B2",
        "rust": "#FFD2AE",
        "bg": "#181512",
        "panel": "#221D18",
        "panel_stroke": "#4A3D31",
        "strip_fill": "#2A241E",
        "strip_stroke": "#5A4C40",
        "halo": "#181512",
        "font_sans": SANS,
        "font_mono": MONO,
    },
}

ICONS = {
    "lambda": "Arch_AWS-Lambda_64.svg",
    "ec2": "Arch_Amazon-EC2_64.svg",
    "ecs": "Arch_Amazon-Elastic-Container-Service_64.svg",
    "eks": "Arch_Amazon-Elastic-Kubernetes-Service_64.svg",
    "fargate": "Arch_AWS-Fargate_64.svg",
    "batch": "Arch_AWS-Batch_64.svg",
    "stepfunctions": "Arch_AWS-Step-Functions_64.svg",
    "eventbridge": "Arch_Amazon-EventBridge_64.svg",
    "cloudfront": "Arch_Amazon-CloudFront_64.svg",
    "route53": "Arch_Amazon-Route-53_64.svg",
    "apigw": "Arch_Amazon-API-Gateway_64.svg",
    "alb": "Arch_Elastic-Load-Balancing_64.svg",
    "vpc": "Arch_Amazon-Virtual-Private-Cloud_64.svg",
    "waf": "Arch_AWS-WAF_64.svg",
    "shield": "Arch_AWS-Shield_64.svg",
    "acm": "Arch_AWS-Certificate-Manager_64.svg",
    "vpce": "Res_Amazon-VPC_Endpoints_48.svg",
    "natgw": "Res_Amazon-VPC_NAT-Gateway_48.svg",
    "igw": "Res_Amazon-VPC_Internet-Gateway_48.svg",
    "dynamodb": "Arch_Amazon-DynamoDB_64.svg",
    "rds": "Arch_Amazon-RDS_64.svg",
    "aurora": "Arch_Amazon-Aurora_64.svg",
    "redis": "Arch_Amazon-ElastiCache_64.svg",
    "s3": "Arch_Amazon-Simple-Storage-Service_64.svg",
    "opensearch": "Arch_Amazon-OpenSearch-Service_64.svg",
    "efs": "Arch_Amazon-EFS_64.svg",
    "sqs": "Arch_Amazon-Simple-Queue-Service_64.svg",
    "sns": "Arch_Amazon-Simple-Notification-Service_64.svg",
    "kinesis": "Arch_Amazon-Kinesis-Data-Streams_64.svg",
    "firehose": "Arch_Amazon-Data-Firehose_64.svg",
    "msk": "Arch_Amazon-Managed-Streaming-for-Apache-Kafka_64.svg",
    "athena": "Arch_Amazon-Athena_64.svg",
    "glue": "Arch_AWS-Glue_64.svg",
    "kms": "Arch_AWS-Key-Management-Service_64.svg",
    "secrets": "Arch_AWS-Secrets-Manager_64.svg",
    "ssm": "Arch_AWS-Systems-Manager_64.svg",
    "iam": "Arch_AWS-Identity-and-Access-Management_64.svg",
    "cognito": "Arch_Amazon-Cognito_64.svg",
    "cloudwatch": "Arch_Amazon-CloudWatch_64.svg",
    "xray": "Arch_AWS-X-Ray_64.svg",
    "cloudtrail": "Arch_AWS-CloudTrail_64.svg",
    "budgets": "Arch_AWS-Budgets_64.svg",
    "codepipeline": "Arch_AWS-CodePipeline_64.svg",
    "codebuild": "Arch_AWS-CodeBuild_64.svg",
    "ecr": "Arch_Amazon-Elastic-Container-Registry_64.svg",
    "users": "Res_Users_48_Light.svg",
    "user": "Res_User_48_Light.svg",
    "client": "Res_Client_48_Light.svg",
    "mobile": "Res_Mobile-client_48_Light.svg",
    "internet": "Res_Internet_48_Light.svg",
    "git": "Res_Git-Repository_48_Light.svg",
    "email": "Res_Email_48_Light.svg",
    "server": "Res_Server_48_Light.svg",
    "app": "Res_Generic-Application_48_Light.svg",
    "cdn": "Res_Amazon-CloudFront_Edge-Location_48.svg",
    "g_cloud": "AWS-Cloud_32.svg",
    "g_region": "Region_32.svg",
    "g_vpc": "Virtual-private-cloud-VPC_32.svg",
    "g_public_subnet": "Public-subnet_32.svg",
    "g_private_subnet": "Private-subnet_32.svg",
    "g_account": "AWS-Account_32.svg",
    "g_corp": "Corporate-data-center_32.svg",
    "g_autoscaling": "Auto-Scaling-group_32.svg",
}


def _esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _normalize_theme(theme):
    key = (theme or DEFAULT_THEME).strip().lower().replace("_", "-")
    aliases = {
        "standard": "standard-light",
        "standard-light": "standard-light",
        "standard-dark": "standard-dark",
        "hand": "hand-drawn-light",
        "hand-drawn": "hand-drawn-light",
        "handdrawn": "hand-drawn-light",
        "hand-drawn-light": "hand-drawn-light",
        "hand-drawn-dark": "hand-drawn-dark",
    }
    key = aliases.get(key, key)
    if key not in THEMES:
        valid = ", ".join(sorted(THEMES.keys()))
        raise SystemExit(f"unknown theme '{theme}'. valid themes: {valid}")
    return key, THEMES[key]


def _skill_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _find_pack_root(base):
    markers = [
        "Arch_AWS-Lambda_64.svg",
        "AWS-Cloud_32.svg",
        "Res_Users_48_Light.svg",
    ]
    for marker in markers:
        hits = glob.glob(os.path.join(base, "**", marker), recursive=True)
        if hits:
            return os.path.dirname(hits[0])
    return None


def resolve_icon_root(explicit_root=None):
    if explicit_root and os.path.isdir(explicit_root):
        return explicit_root
    env_root = os.environ.get("AWS_ICONS")
    if env_root and os.path.isdir(env_root):
        return env_root

    root = _skill_root()
    candidates = [
        os.path.join(root, "icons"),
        os.path.join(root, "assets", "icons"),
        os.path.join(root, "aws-icons"),
        os.path.join(root, "icon-pack"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            found = _find_pack_root(c)
            if found:
                return c

    found = _find_pack_root(root)
    if found:
        return root

    raise SystemExit(
        "AWS icon pack not found. Put pack under the skill folder (e.g. ./icons) "
        "or set AWS_ICONS=/path/to/unzipped-pack."
    )


def find_icons(icon_root, query, all_sizes=False):
    words = query.lower().split()
    hits = []
    for p in glob.glob(os.path.join(icon_root, "**", "*.svg"), recursive=True):
        n = os.path.basename(p)
        low = n.lower()
        if not all(w in low for w in words):
            continue
        if not all_sizes and not (
            n.endswith("_64.svg")
            or n.endswith("_48.svg")
            or n.endswith("_48_Light.svg")
            or n.endswith("_32.svg")
        ):
            continue
        hits.append(n)
    return sorted(set(hits))


class Diagram:
    def __init__(
        self,
        width,
        height,
        title,
        subtitle="",
        aria="",
        icon_root=None,
        extra_icons=None,
        panel=True,
        theme=DEFAULT_THEME,
        clean_labels=False,
    ):
        self.W, self.H = width, height
        self.title, self.subtitle, self.aria = title, subtitle, aria or title
        self.panel = panel
        self.clean_labels = clean_labels
        self.root = resolve_icon_root(icon_root)
        self.theme_name, t = _normalize_theme(theme)
        self.hand = t["hand"]
        self.ink = t["ink"]
        self.slate = t["slate"]
        self.muted = t["muted"]
        self.rust = t["rust"]
        self.bg = t["bg"]
        self.panel_fill = t["panel"]
        self.panel_stroke = t["panel_stroke"]
        self.strip_fill = t["strip_fill"]
        self.strip_stroke = t["strip_stroke"]
        self.halo = t["halo"]
        self.font_sans = t["font_sans"]
        self.font_mono = t["font_mono"]
        self.line_width = 2.6 if self.hand else 2.2
        self.icons = dict(ICONS, **(extra_icons or {}))
        self._uri = {}
        self.body = []
        self.overlay_bg = []
        self.text_body = []
        self._occupied = []
        self._arrow_segments = []

    def _find(self, name):
        hits = glob.glob(os.path.join(self.root, "**", name), recursive=True)
        if not hits:
            raise SystemExit(f"icon not found in pack: {name}  (try: awsdiag.py icons <word>)")
        return hits[0]

    def uri(self, key):
        if key not in self._uri:
            with open(self._find(self.icons[key]), "rb") as f:
                self._uri[key] = "data:image/svg+xml;base64," + base64.b64encode(f.read()).decode()
        return self._uri[key]

    def raw(self, svg_fragment):
        self.body.append(svg_fragment)

    def _estimate_text_width(self, text, size):
        return max(8.0, len(str(text)) * size * 0.60)

    def _lines_box(self, x, y, lines, anchor="middle", gap=16):
        # lines: [(text, size, weight, fill, family), ...]
        widths = [self._estimate_text_width(t, s) for t, s, *_ in lines]
        max_w = max(widths) if widths else 0
        top = min(y + i * gap - s for i, (_, s, *_rest) in enumerate(lines))
        bottom = max(y + i * gap + 4 for i, _ in enumerate(lines))
        if anchor == "start":
            x1, x2 = x - 4, x + max_w + 4
        elif anchor == "end":
            x1, x2 = x - max_w - 4, x + 4
        else:
            x1, x2 = x - max_w / 2 - 4, x + max_w / 2 + 4
        return (x1, top - 3, x2, bottom + 3)

    @staticmethod
    def _overlap(a, b):
        return not (a[2] <= b[0] or a[0] >= b[2] or a[3] <= b[1] or a[1] >= b[3])

    def _reserve_box(self, box):
        self._occupied.append(box)

    def _is_clear(self, box):
        if box[0] < 0 or box[1] < 0 or box[2] > self.W or box[3] > self.H:
            return False
        for b in self._occupied:
            if self._overlap(box, b):
                return False
        return True

    def _candidate_offsets(self, step=12, tries=14, bias=0):
        # bias: +1 prefer downward, -1 prefer upward, 0 symmetric.
        if bias > 0:
            primary = [i * step for i in range(0, tries + 1)]
            secondary = [-(i * step) for i in range(1, tries + 1)]
            return primary + secondary
        if bias < 0:
            primary = [-(i * step) for i in range(0, tries + 1)]
            secondary = [i * step for i in range(1, tries + 1)]
            return primary + secondary
        offsets = [0]
        for i in range(1, tries + 1):
            offsets.extend([i * step, -(i * step)])
        return offsets

    def _draw_label_lines(
        self,
        x,
        y,
        lines,
        anchor="middle",
        gap=16,
        bias=0,
        halo=False,
        backplate=False,
    ):
        best_y = y
        lines_text = " | ".join(str(t) for t, *_ in lines)
        for off in self._candidate_offsets(step=12, tries=14, bias=bias):
            test_y = y + off
            box = self._lines_box(x, test_y, lines, anchor=anchor, gap=gap)
            if self._is_clear(box):
                best_y = test_y
                self._reserve_box(box)
                break
        else:
            if self.clean_labels:
                raise SystemExit(
                    "label overlap unresolved for: "
                    f"{lines_text}. Move elements farther apart or disable clean_labels."
                )
            # Best-effort fallback when strict clean labels are disabled.
            self._reserve_box(self._lines_box(x, y, lines, anchor=anchor, gap=gap))

        if backplate:
            box = self._lines_box(x, best_y, lines, anchor=anchor, gap=gap)
            self.overlay_bg.append(
                f'<rect x="{box[0]-3}" y="{box[1]-2}" width="{(box[2]-box[0])+6}" '
                f'height="{(box[3]-box[1])+4}" rx="4" fill="{self.panel_fill}" opacity="0.92"/>'
            )

        for i, (txt, size, weight, fill, family) in enumerate(lines):
            self.text(
                x,
                best_y + i * gap,
                txt,
                size,
                weight,
                fill,
                anchor=anchor,
                family=family,
                halo=halo,
            )

    def text(self, x, y, s, size=13, weight=400, fill=None, anchor="middle", family=None, halo=False):
        fill = fill or self.ink
        family = family or self.font_sans
        h = (
            f' paint-order="stroke" stroke="{self.halo}" stroke-width="2.5" stroke-linejoin="round"'
            if halo
            else ""
        )
        self.text_body.append(
            f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
            f'text-rendering="geometricPrecision"{h}>{_esc(s)}</text>'
        )

    def icon(self, x, y, key, title, subs=(), size=80, place="below"):
        h = size / 2
        transform = ""
        klass = ""
        if self.hand:
            # Deterministic tiny wobble so hand-drawn mode is visibly different.
            wobble = ((sum(ord(c) for c in (key + title)) % 9) - 4) * 0.9
            transform = f' transform="rotate({wobble:.2f} {x} {y})"'
            klass = ' class="sketch"'
        self.body.append(
            f'<image href="{self.uri(key)}" x="{x-h}" y="{y-h}" width="{size}" height="{size}"'
            f'{transform}{klass}/>'
        )
        self._reserve_box((x - h - 6, y - h - 6, x + h + 6, y + h + 6))
        n = len(subs)
        lines = [(title, 14, 600, self.ink, self.font_sans)]
        lines.extend((s, 12, 400, self.muted, self.font_sans) for s in subs)
        if place == "below":
            ty = y + h + 22
            self._draw_label_lines(x, ty, lines, anchor="middle", gap=18, bias=1)
        elif place == "above":
            top = y - h - 12 - n * 16
            self._draw_label_lines(x, top, lines, anchor="middle", gap=18, bias=-1)
        else:
            anchor = "start" if place == "right" else "end"
            tx = x + h + 12 if place == "right" else x - h - 12
            ty = y - (18 + 16 * n) / 2 + 14
            self._draw_label_lines(tx, ty, lines, anchor=anchor, gap=18, bias=0)

    def arrow(self, points, dashed=False, color=None, head=True, jumps=()):
        color = color or self.slate
        auto_jumps = []
        for i in range(1, len(points)):
            x1, y1 = points[i - 1]
            x2, y2 = points[i]
            if y1 == y2:
                x_lo, x_hi = sorted((x1, x2))
                y = y1
                for seg in self._arrow_segments:
                    if seg["orient"] != "v":
                        continue
                    vx = seg["x"]
                    vy1, vy2 = seg["y1"], seg["y2"]
                    if x_lo + 8 < vx < x_hi - 8 and min(vy1, vy2) + 8 < y < max(vy1, vy2) - 8:
                        auto_jumps.append((vx, y))
        merged_jumps = list({(int(x), int(y)) for x, y in (list(jumps) + auto_jumps)})
        d = ""
        for i, (x, y) in enumerate(points):
            if i == 0:
                d += f"M{x},{y}"
                continue
            px, py = points[i - 1]
            seg = [j for j in merged_jumps if j[1] == y == py and min(px, x) < j[0] < max(px, x)]
            if seg:
                dr = 1 if x > px else -1
                for jx, _ in sorted(seg, key=lambda j: dr * j[0]):
                    d += f" L{jx - 12 * dr},{y} A12,12 0 0 {1 if dr > 0 else 0} {jx + 12 * dr},{y}"
            d += f" L{x},{y}"
        dash = ' stroke-dasharray="7,6"' if dashed else ""
        if self.hand and not dashed:
            dash = ' stroke-dasharray="1,0.01"'
        marker = ' marker-end="url(#arrow)"' if head else ""
        klass = ' class="sketch"' if self.hand else ""
        self.body.append(
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{self.line_width}"{dash}'
            f'{marker}{klass} stroke-linejoin="round" stroke-linecap="round"/>'
        )
        for i in range(1, len(points)):
            x1, y1 = points[i - 1]
            x2, y2 = points[i]
            if x1 == x2:
                self._arrow_segments.append({"orient": "v", "x": x1, "y1": y1, "y2": y2})
                x_lo, x_hi = x1 - 3, x1 + 3
                y_lo, y_hi = sorted((y1, y2))
                self._reserve_box((x_lo, y_lo, x_hi, y_hi))
            elif y1 == y2:
                self._arrow_segments.append({"orient": "h", "y": y1, "x1": x1, "x2": x2})
                x_lo, x_hi = sorted((x1, x2))
                y_lo, y_hi = y1 - 3, y1 + 3
                self._reserve_box((x_lo, y_lo, x_hi, y_hi))

    def flow(self, x, y, n, s, anchor="start"):
        stroke = f' stroke="{self.ink}" stroke-width="1.1"' if self.hand else ""
        klass = ' class="sketch"' if self.hand else ""
        self.body.append(f'<circle cx="{x}" cy="{y}" r="10" fill="{self.rust}"{stroke}{klass}/>')
        self._reserve_box((x - 12, y - 12, x + 12, y + 12))
        self.text(x, y + 4, str(n), 11, 700, "#fff")
        tx = x + 18 if anchor == "start" else x - 18
        lines = [(s, 12.5, 500, self.rust, self.font_mono)]
        self._draw_label_lines(
            tx,
            y + 4,
            lines,
            anchor=anchor,
            gap=16,
            bias=0,
            halo=False,
            backplate=True,
        )

    def note(self, x, y, s, anchor="start"):
        lines = [(s, 12.5, 500, self.rust, self.font_mono)]
        self._draw_label_lines(
            x,
            y,
            lines,
            anchor=anchor,
            gap=16,
            bias=0,
            halo=False,
            backplate=True,
        )

    def group(self, x1, y1, x2, y2, kind, label, dashed=False, fill="none", color=None):
        color = color or COLORS[kind]
        dash = ' stroke-dasharray="9,6"' if dashed else ""
        if self.hand and not dashed:
            dash = ' stroke-dasharray="1,0.01"'
        klass = ' class="sketch"' if self.hand else ""
        self.body.append(
            f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" rx="6" '
            f'fill="{fill}" stroke="{color}" stroke-width="2"{dash}{klass}/>'
        )
        self.body.append(f'<image href="{self.uri("g_" + kind)}" x="{x1}" y="{y1}" width="36" height="36"/>')
        self.text(x1 + 46, y1 + 24, label, 15, 600, self.ink, "start")

    def strip(self, x, y, w, h, title, subtitle=""):
        klass = ' class="sketch"' if self.hand else ""
        self.body.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{self.strip_fill}" '
            f'stroke="{self.strip_stroke}" stroke-dasharray="4,4"{klass}/>'
        )
        self.text(x + w / 2, y + 25, title, 14, 600, self.ink)
        if subtitle:
            self.text(x + w / 2, y + 42, subtitle, 11, 400, self.muted)

    def legend(self, y, sequence=""):
        klass = ' class="sketch"' if self.hand else ""
        self.body.append(
            f'<line x1="40" y1="{y}" x2="80" y2="{y}" stroke="{self.slate}" '
            f'stroke-width="{self.line_width}"{klass}/>'
        )
        self.text(90, y + 4, "synchronous request", 13, 400, self.slate, "start")
        self.body.append(
            f'<line x1="260" y1="{y}" x2="300" y2="{y}" stroke="{self.slate}" '
            f'stroke-width="{self.line_width}" stroke-dasharray="7,6"{klass}/>'
        )
        self.text(310, y + 4, "asynchronous / control plane", 13, 400, self.slate, "start")
        if sequence:
            self.body.append(f'<circle cx="530" cy="{y}" r="10" fill="{self.rust}"{klass}/>')
            self.text(530, y + 4, "1", 11, 700, "#fff")
            self.text(548, y + 4, "flow sequence: " + sequence, 13, 400, self.slate, "start")

    def svg(self):
        W, H = self.W, self.H
        extra_defs = ""
        style = ""
        if self.hand:
            extra_defs = (
                '<filter id="roughen">'
                '<feTurbulence type="fractalNoise" baseFrequency="0.95" numOctaves="2" seed="8" result="noise"/>'
                '<feDisplacementMap in="SourceGraphic" in2="noise" scale="3.2"/>'
                "</filter>"
            )
            style = "<style>.sketch{filter:url(#roughen)}</style>"
        head = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{_esc(self.aria)}">',
            f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{self.slate}"/></marker>{extra_defs}</defs>',
            style,
            f'<rect width="{W}" height="{H}" fill="{self.bg}"/>',
        ]
        head.append(
            f'<text x="40" y="62" font-family="{self.font_sans}" font-size="34" font-weight="700" fill="{self.ink}">{_esc(self.title)}</text>'
        )
        if self.subtitle:
            head.append(
                f'<text x="40" y="90" font-family="{self.font_sans}" font-size="14" fill="{self.slate}">{_esc(self.subtitle)}</text>'
            )
        if self.panel:
            klass = ' class="sketch"' if self.hand else ""
            head.append(
                f'<rect x="30" y="120" width="{W-60}" height="{H-160}" rx="8" fill="{self.panel_fill}" stroke="{self.panel_stroke}"{klass}/>'
            )
        return "\n".join(
            [s for s in head if s]
            + self.body
            + self.overlay_bg
            + self.text_body
            + ["</svg>"]
        )

    def write(self, out_dir, name="architecture", caption="", include_html=False):
        os.makedirs(out_dir, exist_ok=True)
        svg = self.svg()
        with open(os.path.join(out_dir, f"{name}.svg"), "w") as f:
            f.write(svg)

        if include_html:
            font_link = (
                '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family='
                'IBM+Plex+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@500&display=swap">'
            )
            if self.hand:
                font_link = (
                    '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family='
                    'Patrick+Hand&display=swap">'
                )

            html = f"""<title>{_esc(self.title)}</title>
{font_link}
<style>
:root {{ --bg:{self.bg}; --ink:{self.ink}; }}
body {{ margin:0; background:var(--bg); color:var(--ink); padding-block:24px; padding-inline:16px; }}
figure {{ margin:0 auto; max-width:{self.W}px; }}
svg {{ display:block; width:100%; height:auto; }}
figcaption {{ font:13px/1.5 {self.font_sans}; color:{self.slate}; margin-top:12px; max-width:70ch; }}
</style>
<figure>
{svg}
<figcaption>{caption}</figcaption>
</figure>
"""
            with open(os.path.join(out_dir, f"{name}.html"), "w") as f:
                f.write(html)

        render = (
            '<!doctype html><html><head><meta charset="utf-8">'
            f'<style>html,body{{margin:0;background:{self.bg}}} svg{{display:block}}</style>'
            f"</head><body>{svg}</body></html>"
        )
        with open(os.path.join(out_dir, f"{name}.render.html"), "w") as f:
            f.write(render)
        wrote_html = f" / {name}.html" if include_html else ""
        print(f"wrote {name}.svg{wrote_html} / {name}.render.html ({self.W}x{self.H}) theme={self.theme_name}")


def _cli():
    if len(sys.argv) >= 2 and sys.argv[1] == "themes":
        for t in sorted(THEMES.keys()):
            print(t)
        return
    if len(sys.argv) >= 3 and sys.argv[1] == "icons":
        root = resolve_icon_root()
        for n in find_icons(root, sys.argv[2], all_sizes="--all" in sys.argv):
            print(n)
        return
    print(__doc__)


if __name__ == "__main__":
    _cli()
