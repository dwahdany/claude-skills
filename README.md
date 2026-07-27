# claude-skills

My personal [Claude Code](https://code.claude.com) skills. Cloned directly into `~/.claude/skills` so they load un-namespaced (`/bro`, not `/plugin:bro`).

## Install

```sh
git clone https://github.com/dwahdany/claude-skills.git ~/.claude/skills
```

Or with SSH: `git clone git@github.com:dwahdany/claude-skills.git ~/.claude/skills`

## Update

```sh
git -C ~/.claude/skills pull
```

## Skills

| Skill | Description |
|-------|-------------|
| `/bro` | Restate the last message in plain human language, with no jargon. |
| `/pro` | Rewrite prose into a dense internal register (acronym coinage, telegraphed body, term block) at a chosen depth `1`–`3`. Counterpart to `/bro`. |
| `/paper-figure` | Publication-ready figure styling for ML papers (ICML format) — matplotlib/seaborn setup, vector PDF output, colorblind-safe palettes, separate legend export, LaTeX integration. |

## Adding a skill

Create `<name>/SKILL.md` with frontmatter (`name`, `description`, optionally `disable-model-invocation: true`), then commit and push.
