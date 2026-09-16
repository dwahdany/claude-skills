---
name: subtitle-translate
description: Translate a video's embedded subtitle track (or a standalone .srt) into another language with a subagent workflow (style guide → per-batch translation → per-batch editorial review), fix reading speed with a retiming pass, and mux the new track into a copy of the MKV. Use when the user asks to add translated subtitles to an .mkv/.mp4, translate an .srt, or says subtitles disappear too fast. Includes an offline Argos MT fallback.
---

# Subtitle translate + retime + mux

End-to-end pipeline that was built for a 45-minute episode (660 cues) and takes ~25 min wall-clock,
~20 of them in the subagent workflow (~1.2 M subagent tokens for 19 batches).

Scripts live in `scripts/` next to this file (call them with absolute paths, expand `~`).
All Python scripts are `uv run` scripts with inline deps. `ffmpeg`/`ffprobe` come from `nix-shell -p ffmpeg`
(do **not** add `mkvtoolnix` to the nix-shell: it builds Qt/Ruby from source and times out; ffmpeg alone is enough).

## Ground rules

- The user's own media file is the input. Translating it for them is ordinary work on a provided document.
  Never paste subtitle text into the chat; agents write to files, and you report only statistics.
- Never modify or overwrite the original video. Write `<name>+<LANG>.mkv` next to it (`mux.sh` refuses to overwrite).
- Invoking this skill counts as the user's opt-in for the Workflow tool.

## Procedure

1. **Probe** and check whether the target language already exists:
   ```sh
   ffprobe -v error -show_entries stream=index,codec_type,codec_name:stream_tags=language,title:stream_disposition=default -of compact FILE.mkv
   ```
2. **Extract** the best source track (usually English `subrip`) — work in a scratch dir such as `_subwork/` next to the video:
   ```sh
   ffmpeg -v error -y -i FILE.mkv -map 0:<idx> -c:s srt _subwork/src.srt
   ```
   Count cues with the `srt` library, not `grep -c '^[0-9]*$'` (that also matches blank lines and doubles the count).
3. **Batch**: `uv run scripts/make_batches.py _subwork/src.srt _subwork/batches --size 35`
   → `batches/NN.json` (`{"batch", "context", "items":[{"i","en"}]}`; empty cues skipped but indices preserved).
4. **Translate with the workflow** (background; you get a notification):
   ```
   Workflow({ scriptPath: "<abs>/scripts/translate_workflow.js",
              args: { dir: "<abs>/_subwork", srcSrt: "<abs>/_subwork/src.srt", batches: <N>,
                      src: "English", dst: "Russian",
                      notes: "Chinese-language drama; names are pinyin → Palladius transliteration", maxChars: 70 } })
   ```
   Phases: one style-guide agent reads the whole SRT (names, terms, formal/informal address, tone) → one translator per
   batch (writes `NN.draft.json`) → one editor per batch (writes `NN.reviewed.json`, returns `changed` + `issues`).
   Read the returned `issues`: they list cues where the speaker is ambiguous (form of address / gender may be wrong) — relay those to the user.
5. **Assemble**: 
   ```sh
   uv run scripts/assemble.py --src _subwork/src.srt --batches _subwork/batches --out _subwork/tgt.srt --dash "— " --script "[А-Яа-яЁё]" [--fallback argos.srt]
   ```
   Uses reviewed → draft → fallback → source text; normalises two-speaker cues (reviewers return mixed `-X. -Y.` / `— X. — Y.`
   styles) to one speaker per line with `--dash` (`"— "` for Russian, `"- "` for most other languages); strips U+200E marks;
   wraps at 42 chars, never 3 lines. Exit 1 if anything is missing/untranslated — fix before muxing.
6. **Retime** (this is what fixes "the text is too fast"):
   ```sh
   uv run scripts/retime.py --merge _subwork/tgt.srt _subwork/final.srt
   ```
   Prints before/after stats (`over_15cps`, `over_20cps`, `under_1s`, p90, max, overlaps). Passes: extend into free gaps →
   delay a slack next cue ≤ 0.5 s while balancing CPS → lead-in ≤ 0.3 s (trimming a slack previous cue) → `--merge` joins two
   adjacent single-line cues that are still starving into one 2-line block → repeat. Defaults: target 15 CPS, min 1.0 s,
   max 7 s, gap 0.08 s. Never introduces overlaps. Residual fast cues are dense 2-line dialogue with no slack on either side;
   only shorter text helps there (hence `maxChars` in the workflow). Netflix source timing is itself fast (median ≈ 16 CPS),
   so always retime, even without translation.
7. **Mux + verify** (writes a new file, round-trips the track and compares it cue by cue):
   ```sh
   nix-shell -p ffmpeg --run 'sh scripts/mux.sh FILE.mkv _subwork/final.srt rus "Русский" "FILE+RUS.mkv" --default'
   ```
   `--default` makes the new track the default subtitle and clears the flag on the others. ffmpeg syntax pitfalls:
   the new track is `s:<number of existing subtitle streams>`; disposition is `-disposition:s:N`, not `-disposition:s:s:N`.
8. **Report**: what was translated (agents, batches, glossary size), the retiming table (before/after), the reviewers'
   ambiguous-speaker cues, where the SRT and batches live, and that the original is untouched.

## Fallbacks and alternatives

- `scripts/argos_translate.py IN.srt OUT.srt en ru` — offline Argos MT (~1 min for 660 cues, basic quality). Use as
  `--fallback` for assemble.py or when subagents are not wanted. Google Translate web endpoints (deep-translator, gtx) were
  blocked from this network; don't bother.
- A local Ollama model (gemma3:12b, 8 GB, ~25 min on an M4) also works but the user preferred subagents; only do it on request.
- If the workflow is stopped mid-way, finished `NN.reviewed.json` / `NN.draft.json` files are reused by assemble.py; resume the
  workflow with `resumeFromRunId` to fill the rest.
