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

## Adding a skill

Create `<name>/SKILL.md` with frontmatter (`name`, `description`, optionally `disable-model-invocation: true`), then commit and push. Top-level skill directories are picked up by both install methods — the `skills` CLI walks the repo root one level deep, so no `skills/` container directory is needed.
