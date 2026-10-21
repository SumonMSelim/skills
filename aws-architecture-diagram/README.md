# aws-architecture-diagram

Generate AWS architecture diagrams from IaC/code with official AWS icons.

Current outputs:
- `architecture.svg` (editable source)
- `architecture.render.html` (render-only HTML)
- `architecture.png` (2x raster output via `render.sh`)

`architecture.html` is optional and disabled by default.

## Is this Claude-only?
No. The **scripts/library are agent-agnostic** (`scripts/awsdiag.py`, `scripts/gen.sh`,
`scripts/render.sh`) and can be used from any agent or directly from shell/Python.

This folder also includes `SKILL.md`, which is Claude-skill metadata/instructions.

## Install
Two common options:
- Claude skill install: `~/.claude/skills/aws-architecture-diagram/`
- Any repo/tooling folder: copy anywhere and run scripts directly

## Requirements
- Docker (preferred path)
- Python 3 (`gen.sh` falls back to local Python if Docker is unavailable)
- AWS icon pack available either:
  - bundled under this skill folder (e.g. `icons/`), or
  - via `AWS_ICONS=/path/to/unzipped-pack`

## Themes
Supported themes:
- `standard-light`
- `standard-dark`
- `hand-drawn-light`
- `hand-drawn-dark`

Pass via environment:

    THEME=hand-drawn-dark scripts/gen.sh /path/to/spec.py out

Or in Python spec:

    Diagram(..., theme="hand-drawn-dark")

## Clean labels mode
Set `clean_labels=True` in `Diagram(...)` to enforce strict label placement.
If a label cannot be placed without overlap, generation fails with a clear error.

## Manual use

    scripts/gen.sh /path/to/spec.py out
    scripts/render.sh out architecture 2300 1400

## Notes
- `render.sh` runs headless Chrome in Docker and then crops with Pillow.
- Dark-mode readability was tuned for high contrast and crisp text.
