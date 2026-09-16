# /// script
# requires-python = ">=3.10,<3.13"
# dependencies = ["srt", "argostranslate"]
# ///
"""Offline baseline/fallback: translate an SRT with Argos Translate.

Usage: argos_translate.py IN.srt OUT.srt [SRC=en] [DST=ru]   (downloads the language pack once, ~100 MB)
Quality is basic MT; use it as --fallback for assemble.py or for a quick first pass."""
import sys, textwrap, time
import srt
import argostranslate.package as pkg
import argostranslate.translate as tr

SRC, DST = sys.argv[3] if len(sys.argv) > 3 else "en", sys.argv[4] if len(sys.argv) > 4 else "ru"
inp, outp = sys.argv[1], sys.argv[2]

# Ensure the language package is installed (downloads ~100 MB once).
installed = {(p.from_code, p.to_code) for p in pkg.get_installed_packages()}
if (SRC, DST) not in installed:
    pkg.update_package_index()
    cand = [p for p in pkg.get_available_packages() if p.from_code == SRC and p.to_code == DST]
    if not cand:
        sys.exit("no en->ru package available")
    print("downloading model ...", flush=True)
    pkg.install_from_path(cand[0].download())

langs = tr.get_installed_languages()
src = next(l for l in langs if l.code == SRC)
dst = next(l for l in langs if l.code == DST)
engine = src.get_translation(dst)

def wrap(text, width=42, max_lines=2):
    lines = textwrap.wrap(text, width=width)
    if len(lines) > max_lines:
        # balance into max_lines lines instead of dropping anything
        lines = textwrap.wrap(text, width=max(width, -(-len(text) // max_lines) + 5))
    return "\n".join(lines)

subs = list(srt.parse(open(inp, encoding="utf-8").read()))
t0 = time.time()
out = []
for i, s in enumerate(subs, 1):
    flat = " ".join(s.content.split())
    if flat:
        ru = engine.translate(flat).strip()
        s.content = wrap(ru) if ru else s.content
    out.append(s)
    if i % 100 == 0:
        print(f"{i}/{len(subs)} cues, {time.time()-t0:.0f}s", flush=True)

open(outp, "w", encoding="utf-8").write(srt.compose(out))
print(f"done: {len(out)} cues written to {outp} in {time.time()-t0:.0f}s")
