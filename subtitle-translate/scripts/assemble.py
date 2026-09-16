# /// script
# requires-python = ">=3.10"
# dependencies = ["srt"]
# ///
"""Assemble translated batches back into an SRT with the source file's timings.

Usage: assemble.py --src IN.srt --batches DIR --out OUT.srt [--fallback F.srt] [--dash "— "] [--script REGEX]
  Reads DIR/NN.reviewed.json first, then DIR/NN.draft.json (translator drafts) for anything missing,
  then --fallback (an SRT with identical cue count, e.g. an offline MT pass), else keeps the source text.
  --dash    prefix for each speaker line in two-speaker cues (Russian: "— ", most others: "- ")
  --script  regex a translated cue must match (e.g. "[А-Яа-яЁё]"); cues failing it while containing
            Latin words are reported as untranslated
Exit code 1 if any cue is missing or looks untranslated.
"""
import argparse, glob, json, re, sys, textwrap
from collections import Counter
import srt

p = argparse.ArgumentParser()
p.add_argument("--src", required=True); p.add_argument("--batches", required=True); p.add_argument("--out", required=True)
p.add_argument("--fallback"); p.add_argument("--dash", default="- "); p.add_argument("--script")
p.add_argument("--width", type=int, default=42)
a = p.parse_args()

# Two-speaker cues come back with mixed markers ("-X. -Y.", "- X. - Y.", "— X. — Y.").
# Normalise: each speaker on its own line, introduced by --dash. Only split at a dash that follows
# sentence-final punctuation and precedes a new sentence, so mid-sentence dashes survive.
DASH_SPLIT = re.compile(r'(?<=[.?!…»"”])\s+(?=[-–—]\s?[«"“A-ZА-ЯЁ0-9♪\[])')
LEAD_DASH = re.compile(r'^[-–—]\s?(?=\S)')

def dialogue_lines(text):
    if not LEAD_DASH.match(text):
        return None
    parts = [LEAD_DASH.sub("", x).strip() for x in DASH_SPLIT.split(text)]
    return [a.dash + x for x in parts if x]

def wrap(text, source):
    text = text.replace("‎", "").strip()
    if len(text) > 1 and text[0] in '"«“' and text[-1] in '"»”' and source[:1] not in '"«“':
        text = text[1:-1].strip()
    lines = dialogue_lines(text)
    if lines:
        return "\n".join(lines)
    lines = textwrap.wrap(text, width=a.width)
    if len(lines) > 2:                                   # never 3 lines: balance into two longer ones
        lines = textwrap.wrap(text, width=max(a.width, -(-len(text) // 2) + 5))
    return "\n".join(lines)

subs = list(srt.parse(open(a.src, encoding="utf-8").read()))
fallback = list(srt.parse(open(a.fallback, encoding="utf-8").read())) if a.fallback else None
if fallback and len(fallback) != len(subs):
    sys.exit("fallback cue count differs from source")
flat = lambda t: " ".join(l.strip() for l in t.splitlines() if l.strip())

tr, origin = {}, {}
for path in sorted(glob.glob(f"{a.batches}/*.json")):
    kind = "reviewed" if path.endswith(".reviewed.json") else "draft" if path.endswith((".draft.json", ".ru.json")) else None
    if not kind:
        continue
    try:
        data = json.load(open(path, encoding="utf-8"))
    except Exception as e:
        print("bad json:", path, e); continue
    for t in data.get("translations", []):
        i, text = t.get("i"), (t.get("ru") or t.get("text") or "").strip()
        if isinstance(i, int) and text and (kind == "reviewed" or i not in tr):
            tr[i], origin[i] = text, kind

missing, untranslated = [], []
for i, s in enumerate(subs):
    en = flat(s.content)
    if not en:
        continue
    if i in tr:
        if a.script and not re.search(a.script, tr[i]) and re.search(r"[A-Za-z]{3,}", tr[i]):
            untranslated.append(i)
        s.content = wrap(tr[i], en)
    else:
        missing.append(i)
        if fallback:
            s.content = fallback[i].content
open(a.out, "w", encoding="utf-8").write(srt.compose(subs))
three = [i for i, s in enumerate(subs) if s.content.count("\n") >= 2]
print("sources:", dict(Counter(origin.values())), "| missing:", len(missing), missing[:15],
      "| untranslated:", len(untranslated), untranslated[:15], "| 3-line cues:", len(three))
sys.exit(1 if (missing or untranslated) else 0)
