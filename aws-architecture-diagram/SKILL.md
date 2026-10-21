---
name: aws-architecture-diagram
description: Generate an accurate AWS system architecture diagram (SVG + render HTML + PNG) for any codebase that deploys to AWS, in the official AWS reference-architecture style with official AWS icons. Use when the user asks for an architecture / system design / infrastructure diagram of an AWS project, or to update an existing one. Read IaC (Terraform, CDK, CloudFormation, SAM) and application code first so every box and arrow is real.
---

# AWS Architecture Diagram

Produce a diagram that an engineer can trust: every component traces to infrastructure code,
every arrow names the real call. Output is an editable SVG, a 2x PNG, and `render.html`
for deterministic screenshot rendering. Generation prefers Docker and falls back to local
Python automatically.

Files in this skill:
- `scripts/awsdiag.py`   drawing library (icons, groups, arrows, badges, legend) and icon lookup CLI
- `scripts/gen.sh`       run a spec (Docker first, local Python fallback)
- `scripts/render.sh`    SVG → PNG via headless Chrome (`zenika/alpine-chrome:124`) + Pillow crop
- `reference/accuracy.md`  how to audit the codebase before drawing (read this first)
- `reference/style.md`     layout grid, label rules, collision checklist
- `reference/icons.md`     icon pack download, naming, lookup

## Prerequisites
- Docker (recommended).
- Python 3 (fallback path if Docker unavailable).
- Official AWS Architecture Icons (SVG asset package): https://aws.amazon.com/architecture/icons/
  pack can be bundled under this skill folder (`icons/`, etc.) or provided via
  `AWS_ICONS=/path/to/unzipped/package`.

## Theme and readability controls
- Themes:
  - `standard-light`
  - `standard-dark`
  - `hand-drawn-light`
  - `hand-drawn-dark`
- Set via `Diagram(..., theme="...")` or `THEME=... scripts/gen.sh ...`.
- Use `clean_labels=True` in `Diagram(...)` to fail fast when label overlap cannot be resolved.

## Workflow

### 1. Audit the source of truth (do not skip)
Follow `reference/accuracy.md`. Read IaC, then application code, then CI workflows, then docs.
Build a component inventory: resource → purpose → in/out edges with the concrete API action
or path pattern. Ask the user which environment/stack is the target if there is more than one.
Follow code over docs when they disagree, and say so.

Do not include instance sizes, node counts, memory, CIDRs, retention or other capacity
details unless the user asks. Components, roles, and communication only.

### 2. Plan the layout
Follow `reference/style.md`. Decide canvas size, the scenario order for numbered badges
(e.g. 1–4 user request, 5–6 async processing, 7 deploy), which services go in the platform
strip, and where third parties sit (outside the AWS Cloud box). Sketch coordinates on a
20 px grid before writing code.

### 3. Write the spec
Create a spec in the project's scratch location (or `docs/` if the user wants it versioned).
Unknown icon name → look it up:

    python scripts/awsdiag.py icons "<keyword>"
    python scripts/awsdiag.py themes

Add new icons with `Diagram(..., extra_icons={"key": "Arch_..._64.svg"})`.

### 4. Generate and render

    scripts/gen.sh <spec.py> <out_dir>
    scripts/render.sh <out_dir> architecture <W> <H>

Outputs `architecture.svg`, `architecture.render.html`, `architecture.png` (2x).

### 5. Review the PNG, then fix
Open the PNG and run the collision checklist in `reference/style.md`: overlapping labels,
labels outside the panel, legend clipped, crossing lines without jumps. Fix coordinates and
re-render. One or two passes is normal.

### 6. Final accuracy pass
Re-read the IaC once more and tick every component and arrow against the render. Tell the
user about any deliberate simplification (an omitted edge, merged tables) so nothing is
silently made up.

### 7. Deliver
Copy `architecture.png` and `architecture.svg` to where the user wants them (commonly
`docs/`). Do not commit unless asked.

## Conventions baked into the library
- Palette: AWS squid ink text, slate arrows, rust flow badges, white panel on light grey.
- Solid arrow = synchronous request. Dashed = asynchronous or control plane.
- Rust mono labels on arrows carry the real API action or path pattern.
- Group colours follow the AWS icon pack (Region teal, VPC purple, private subnet blue,
  public subnet green, account pink).
- Platform strip on the right for shared services (KMS, CloudWatch, X-Ray, ACM, SNS…);
  no arrows into it.
