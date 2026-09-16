# /// script
# requires-python = ">=3.10"
# dependencies = ["srt"]
# ///
"""Split an SRT into JSON batches for the translation workflow.

Usage: make_batches.py IN.srt OUT_DIR [--size 35]
Each OUT_DIR/NN.json = {"batch": n, "context": [last 4 source lines of previous batch],
                        "items": [{"i": cue_index, "en": flattened_text}, ...]}
Cue text is flattened (internal line breaks -> spaces); a leading "- " marks a speaker change.
Empty cues are skipped but keep their index, so assemble.py can map results back.
"""
import argparse, json, os
import srt

p = argparse.ArgumentParser()
p.add_argument("inp"); p.add_argument("out_dir"); p.add_argument("--size", type=int, default=35)
a = p.parse_args()
subs = list(srt.parse(open(a.inp, encoding="utf-8").read()))
flat = lambda t: " ".join(l.strip() for l in t.splitlines() if l.strip())
items = [{"i": i, "en": flat(s.content)} for i, s in enumerate(subs) if flat(s.content)]
batches = [items[k:k + a.size] for k in range(0, len(items), a.size)]
os.makedirs(a.out_dir, exist_ok=True)
for n, b in enumerate(batches):
    ctx = [x["en"] for x in batches[n - 1][-4:]] if n else []
    with open(os.path.join(a.out_dir, f"{n:02d}.json"), "w", encoding="utf-8") as f:
        json.dump({"batch": n, "context": ctx, "items": b}, f, ensure_ascii=False, indent=1)
print(f"{len(subs)} cues, {len(items)} non-empty, {len(batches)} batches of <= {a.size}")
