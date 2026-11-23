# claude-skills

My personal [Claude Code](https://code.claude.com) skills. They install into `~/.claude/skills` so they load un-namespaced (`/bro`, not `/plugin:bro`).

## Install

Two options — pick one, not both. Both end up at `~/.claude/skills/<name>/`, so mixing them means the CLI writes copies into a git working tree.

### Clone — if you want to edit the skills

The checkout *is* the repo, so you can hack on a skill and push it back.

```sh
git clone --recurse-submodules https://github.com/dwahdany/claude-skills.git ~/.claude/skills
```

Or with SSH: `git clone --recurse-submodules git@github.com:dwahdany/claude-skills.git ~/.claude/skills`

`--recurse-submodules` checks out the [third-party skills](#third-party-skills) that are vendored as
git submodules under `vendor/`. Without it their top-level symlinks (e.g. `socratic-tutor`) dangle
and Claude Code silently skips them; `git submodule update --init` fixes an existing clone.

### `npx skills` — if you just want to use them

Installs copies, lets you pick individual skills, and works with [Claude Code and 70+ other agents](https://github.com/vercel-labs/skills):

```sh
npx skills add dwahdany/claude-skills            # pick skills and agents interactively
npx skills add dwahdany/claude-skills --list     # just list what's available
npx skills add dwahdany/claude-skills --skill '*' -a claude-code -g -y   # all skills, globally, no prompts
```

The CLI initialises git submodules after cloning, and `skills.sh.json` points it at `vendor/`, so
the vendored skills show up in the list alongside the rest.

## Update

```sh
git -C ~/.claude/skills pull --recurse-submodules   # if cloned
npx skills update                                   # if installed via npx skills
```

## Skills

| Skill | Description |
|-------|-------------|
| `/bro` | Restate the last message in plain human language, with no jargon. |
| `/pro` | Rewrite prose into a dense internal register (acronym coinage, telegraphed body, term block) at a chosen depth `1`–`3`. Counterpart to `/bro`. |
| `/paper-figure` | Publication-ready figure styling for ML papers (ICML format) — matplotlib/seaborn setup, vector PDF output, colorblind-safe palettes, separate legend export, LaTeX integration. |
| `/blogpost-figure` | Screen-first figures for blog posts in a research-blog house style — takeaway-sentence headline, gray subtitle, direct labels instead of legends, terracotta hero vs steel-blue baseline, retina PNG + WebP. Ships a matplotlib helper module (`blogfig.py`) with rendered recipes for every chart form, HTML/CSS templates for flow diagrams, quote cards, heatmap tables and card dashboards, and a headless-Chrome renderer. Counterpart to `/paper-figure`. One-time setup: `uv run --with matplotlib blogpost-figure/scripts/fetch_fonts.py` (OFL fonts into the git-ignored `fonts/`); the HTML templates need Google Chrome/Chromium or Playwright. |
| `/buchhaltungsbutler` | Operate [BuchhaltungsButler](https://www.buchhaltungsbutler.de/) through its API (Belege hochladen, Zahlungen zuordnen, buchen, Auswertungen) and apply German bookkeeping rules for a small UG/GmbH — SKR03/SKR04, Steuerschlüssel, §13b, UStVA, GoBD. API credentials come from Bitwarden CLI; see [setup](#buchhaltungsbutler-setup). |
| `/i-have-adhd` | ADHD-friendly output shaping: lead with the next action, number multi-step work, restate state each turn, cap lists, no preamble or closers. Vendored from [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) (MIT). |
| `/gworkspace` | Read and write Google Docs, Drive, Gmail, Calendar, Sheets and Slides through a local [`workspace-mcp`](https://github.com/taylorwilsdon/google_workspace_mcp) server; tools are discovered from the server at runtime. |
| `/nexudus` | Member API client for [Nexudus](https://www.nexudus.com)-powered coworking portals (`*.nexudus.site`): parcels/deliveries, room bookings, visitor invites, invoices, plans. 39 endpoint aliases plus a raw-path escape hatch. |
| `/socratic-tutor` | Strict personal tutor using the Socratic method, for when you explicitly ask to be taught, quizzed or drilled on a topic: diagnostic placement, a skill map with levels 0–5, one question at a time, spaced review, final assessment. From [janestreet/agent_skills](https://github.com/janestreet/agent_skills) (MIT), vendored as a git submodule. |
| `/subtitle-translate` | Translate a video's subtitle track (or an `.srt`) into another language with a subagent workflow (style guide → per-batch translation → per-batch review), retime cues so they stay readable, and mux the new track into a copy of the MKV. Ships `uv run` scripts for batching, assembly, retiming and muxing plus an offline Argos fallback. |

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

Some skills here come from upstream projects rather than written by me. They are pulled in one
of two ways:

- **Copied** — `SKILL.md` and `LICENSE` live in the skill's own folder, with a provenance comment
  at the top of `SKILL.md` naming the source repository and commit.
- **Git submodule** — the whole upstream repository is checked out under `vendor/<name>/` at a
  pinned commit, license included, and never edited here. Two small pieces of glue make the
  skills inside it installable:
  - `skills.sh.json` lists `./vendor` in `paths`, so the `skills` CLI searches it. The CLI only
    scans the repo root one level deep, but walks declared container directories up to three
    levels, which reaches `vendor/<name>/<skill>/SKILL.md`.
  - A top-level symlink per skill (`socratic-tutor → vendor/janestreet/socratic-tutor`) exposes
    it at `~/.claude/skills/<skill>/` for the clone install. Claude Code only loads skills one
    level deep but does follow symlinked skill directories. The CLI ignores the symlinks, so
    nothing is listed twice.

| Skill | Upstream | Author | License | How |
|-------|----------|--------|---------|-----|
| `i-have-adhd` | [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) | Ayoub Ghriss | MIT | copied |
| `socratic-tutor` | [janestreet/agent_skills](https://github.com/janestreet/agent_skills) | Jane Street Group | MIT | submodule at `vendor/janestreet` |

To refresh a copied skill, re-copy `SKILL.md` and `LICENSE` from upstream and update the
provenance comment's commit hash. To refresh a submodule, move it to upstream's current HEAD and
commit the new pin:

```sh
git submodule update --remote vendor/janestreet
git add vendor/janestreet && git commit -m "Bump janestreet/agent_skills"
```

If upstream adds a skill, add a matching top-level symlink (`ln -s vendor/janestreet/<skill> <skill>`).

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

### `buchhaltungsbutler` setup

The skill never stores API credentials. `scripts/bb.sh` reads them per call from a Bitwarden
login item (username = API Client, password = API Secret, hidden field `api_key`) using the
[Bitwarden CLI](https://bitwarden.com/help/cli/). One-time setup, in your own terminal:

```sh
bw config server https://your-vault.example   # self-hosted only; skip for bitwarden.com
bw login
export BW_SESSION="$(bw unlock --raw)"
~/.claude/skills/buchhaltungsbutler/scripts/bb-setup.sh   # prompts for the three values from BB → Einstellungen → Schnittstellen und API-Zugang
```

Afterwards start Claude Code from a shell that has `BW_SESSION` exported (`export BW_SESSION="$(bw unlock --raw)"`).
Without it `bb.sh` prints `NOT_UNLOCKED` and does nothing (`bb-setup.sh` asks for your master password instead). `bw` is fetched via `nix-shell -p bitwarden-cli`
if it is not installed; `jq` and `curl` are required. Read calls run freely; anything that writes needs
`--write`, deletes/cancels need `--destructive`, and the skill tells Claude to confirm both with you first.

## Adding a skill

Create `<name>/SKILL.md` with frontmatter (`name`, `description`, optionally `disable-model-invocation: true`), then commit and push. Top-level skill directories are picked up by both install methods — the `skills` CLI walks the repo root one level deep, so no `skills/` container directory is needed.

To pull in a whole upstream repository instead, add it as a submodule and symlink its skills to the root:

```sh
git submodule add https://github.com/<owner>/<repo>.git vendor/<name>
ln -s vendor/<name>/<skill> <skill>
```

`skills.sh.json` already covers everything under `vendor/`; add a row to the [third-party table](#third-party-skills).
