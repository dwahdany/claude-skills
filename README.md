# claude-skills

My personal [Claude Code](https://code.claude.com) skills. They install into `~/.claude/skills` so they load un-namespaced (`/bro`, not `/plugin:bro`).

## Install

Two options — pick one, not both. Both end up at `~/.claude/skills/<name>/`, so mixing them means the CLI writes copies into a git working tree.

### Clone — if you want to edit the skills

The checkout *is* the repo, so you can hack on a skill and push it back.

```sh
git clone https://github.com/dwahdany/claude-skills.git ~/.claude/skills
```

Or with SSH: `git clone git@github.com:dwahdany/claude-skills.git ~/.claude/skills`

### `npx skills` — if you just want to use them

Installs copies, lets you pick individual skills, and works with [Claude Code and 70+ other agents](https://github.com/vercel-labs/skills):

```sh
npx skills add dwahdany/claude-skills            # pick skills and agents interactively
npx skills add dwahdany/claude-skills --list     # just list what's available
npx skills add dwahdany/claude-skills --skill '*' -a claude-code -g -y   # all skills, globally, no prompts
```

## Update

```sh
git -C ~/.claude/skills pull   # if cloned
npx skills update              # if installed via npx skills
```

## Skills

| Skill | Description |
|-------|-------------|
| `/bro` | Restate the last message in plain human language, with no jargon. |
| `/pro` | Rewrite prose into a dense internal register (acronym coinage, telegraphed body, term block) at a chosen depth `1`–`3`. Counterpart to `/bro`. |
| `/paper-figure` | Publication-ready figure styling for ML papers (ICML format) — matplotlib/seaborn setup, vector PDF output, colorblind-safe palettes, separate legend export, LaTeX integration. |
| `/i-have-adhd` | ADHD-friendly output shaping: lead with the next action, number multi-step work, restate state each turn, cap lists, no preamble or closers. Vendored from [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) (MIT). |
| `/gworkspace` | Read and write Google Docs, Drive, Gmail, Calendar, Sheets and Slides through a local [`workspace-mcp`](https://github.com/taylorwilsdon/google_workspace_mcp) server; tools are discovered from the server at runtime. |
| `/nexudus` | Member API client for [Nexudus](https://www.nexudus.com)-powered coworking portals (`*.nexudus.site`): parcels/deliveries, room bookings, visitor invites, invoices, plans. 39 endpoint aliases plus a raw-path escape hatch. |

## Python-backed skills (Prime Agent)

`gworkspace` and `nexudus` are *Python-backed* skills: alongside `SKILL.md` they ship a
`pyproject.toml` and `src/<import_name>/__init__.py`. [Prime Agent](https://github.com/PrimeIntellect-ai/prime-agent)
installs the package into its persistent IPython kernel, so the agent calls the capability
directly (`await nexudus("deliveries")`) instead of shelling out.

- In Prime Agent: clone or symlink the skill directory into `~/.prime/agent/skills/<name>/`.
- In Claude Code and other agents: they still load as ordinary markdown skills — the
  instructions and endpoint reference are useful, but `await <name>(...)` needs the
  Prime Agent kernel. Run the module directly (`uv run python -m <name>`) or port the calls.

Neither skill contains credentials. `nexudus` reads them from `~/.config/nexudus/credentials.json`
or `NEXUDUS_SITE`/`NEXUDUS_EMAIL`/`NEXUDUS_PASSWORD`; `gworkspace` talks to a localhost MCP
server and expects `GWORKSPACE_MCP_TOKEN` in the environment.

## Third-party skills

Some skills here are vendored from upstream projects rather than written by me. Each vendored
skill keeps its upstream `LICENSE` in its own folder and a provenance comment at the top of
`SKILL.md` naming the source repository and commit.

| Skill | Upstream | Author | License |
|-------|----------|--------|---------|
| `i-have-adhd` | [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) | Ayoub Ghriss | MIT |

To refresh a vendored skill, re-copy `SKILL.md` and `LICENSE` from upstream and update the
provenance comment's commit hash.

### `i-have-adhd` always-on

Installing the skill only registers the command; nothing changes until you invoke it. To apply
the rules from message one of every session, put upstream's condensed snippet
([INSTALL.md](https://github.com/ayghri/i-have-adhd/blob/main/INSTALL.md), "Always-on") into the
agent's persistent context file:

| Runtime | File | Loaded from |
|---------|------|-------------|
| Prime Agent | `~/.prime/agent/AGENTS.md` | agent dir, every session (`core/resource-loader.js`) |
| Claude Code | `~/.claude/CLAUDE.md` | global memory, every session |

Upstream also ships a Claude Code `SessionStart` hook gated on `~/.claude/.i-have-adhd-always`,
but that needs the full plugin (`claude plugin marketplace add ayghri/i-have-adhd`), which
installs a second copy of the skill and collides with this one. The context-file route avoids
that. Delete the snippet to go back to on-demand; "stop adhd mode" disables it for one session.

## Adding a skill

Create `<name>/SKILL.md` with frontmatter (`name`, `description`, optionally `disable-model-invocation: true`), then commit and push. Top-level skill directories are picked up by both install methods — the `skills` CLI walks the repo root one level deep, so no `skills/` container directory is needed.
