# skills

A collection of [Claude Code](https://claude.com/claude-code) skills I create or use. One folder
per skill. Each folder has a `SKILL.md` (what triggers it and the workflow the agent follows) and
its own `README.md` with install notes, usage and limitations.

## Skills

| Skill | What it does | Changes your system? |
|---|---|---|
| [`aws-architecture-diagram`](aws-architecture-diagram/) | Reads IaC and application code and generates an AWS reference-style architecture diagram (SVG, HTML, PNG) with official icons. | Writes diagram files only. |
| [`php2shell-defense`](php2shell-defense/) | Defensive response to the PHP runtime RCEs CVE-2026-109618 / CVE-2026-109619 ("PHP2Shell"): inventory, patch when available, temporary mitigation when it is not (config, edge block, firewall, offline), verification on the serving SAPI, exploitation hunt. Every change after your approval. No exploit code. | Only with `--apply`; see its README. |

## Install

Claude Code loads skills from `~/.claude/skills/` (all projects) or `<repo>/.claude/skills/`
(one project). Clone this repo and link the skills you want:

    git clone https://github.com/SumonMSelim/skills.git ~/src/skills
    mkdir -p ~/.claude/skills
    ln -s ~/src/skills/php2shell-defense ~/.claude/skills/php2shell-defense
    ln -s ~/src/skills/aws-architecture-diagram ~/.claude/skills/aws-architecture-diagram

Or copy a single folder instead of linking. Start a new Claude Code session afterwards.

## Use

Skills trigger automatically when your request matches the `description` in their `SKILL.md`,
or explicitly by name: `/php2shell-defense <request>`, `/aws-architecture-diagram <request>`.

Skills that act on servers do not need Claude installed there. Run Claude Code locally; the agent
works over your existing `ssh` access and shows every change before applying it.

## Disclaimer

Everything here is provided "as is", without warranty of any kind. Some skills run scripts that
change system state when you ask them to. Read a skill's README and dry-run output before
applying anything. Use at your own risk. See [LICENSE](LICENSE).

## License

MIT, unless a skill folder states otherwise.
