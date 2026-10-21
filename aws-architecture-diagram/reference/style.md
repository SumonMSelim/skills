# Visual style

Target look: the AWS reference-architecture style (white panel, squid-ink text, official
icons, thin slate arrows, numbered flow badges). `awsdiag.py` encodes the palette and type;
this file covers the judgment calls.

## Canvas and grid
- Width 2000–2400, height as content needs. Title at y 62, subtitle y 90, panel from y 120.
- Snap every centre to a 20 px grid. Column pitch between icons: 200–320. Row pitch: 200–240.
- Icon size 80 for workload services, 64 for actors, endpoints and the platform strip.
- Groups nest with a 30 px inset: AWS Cloud > Region (dashed) > VPC > Subnet (light fill).
- Legend row sits inside the panel, ~40 px above its bottom edge.

## Layout pattern
- Left column: actors outside AWS (users, operator, CI). Keep them at x ≈ 115.
- Top row: edge and API path left→right (CDN → API → compute → data).
- Middle: VPC with private compute and cache. Bottom: async/analytics fan-out.
- Right strip: platform services used by everything (KMS, SSM, CloudWatch, X-Ray, SNS,
  Budgets, ACM). No arrows into the strip; it is shared context, not a flow.
- Third parties (Cloudflare, GitHub, Datadog…) sit outside the AWS Cloud box.

## Labels
- Icon title: service name plus its role, e.g. `S3 · UI bucket`, `redirect Lambda`.
- Sub-lines (muted): only content/role facts, e.g. table names, function roles. Never
  sizes, counts, memory, node types, CIDRs, retention days.
- Arrow labels are rust mono: the real API action or path pattern
  (`GetItem links`, `/api/* (no cache)`, `OIDC AssumeRole`), not prose.
- Numbered badges mark one request's hops in order. Group the numbers by scenario and
  explain the grouping in the legend line.
- Solid arrow = synchronous request/response. Dashed = async, event-driven or control plane.
- Use `jumps=` to arc over a crossing line rather than letting two lines cross flat.

## Collision checklist (check the PNG, not the SVG)
- No label touches an icon, a group header, or another label.
- Nothing extends past the panel edge; left-column labels are the usual offender.
- Legend fully visible; Chrome clips the viewport, so render.sh pads and crops.
- Badge digits stay white: halo only on rust labels, never on badge text.
