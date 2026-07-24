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

## Adding a skill

Create `<name>/SKILL.md` with frontmatter (`name`, `description`, optionally `disable-model-invocation: true`), then commit and push.
