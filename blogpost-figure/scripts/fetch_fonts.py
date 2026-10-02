# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Download open-licensed (OFL) web fonts as static per-weight TTFs so matplotlib can use real
bold/medium weights (matplotlib cannot select weights inside a variable font).

Default target: <skill>/fonts/ (git-ignored; blogfig.py and assets/figure.css both look there).
    uv run fetch_fonts.py                 # DM Sans, Inter, Source Serif 4
    uv run fetch_fonts.py --user          # ~/.local/share/blogfig-fonts instead (matplotlib only)
    uv run fetch_fonts.py --family "Plus Jakarta Sans:400,500,600,700"
Prints the family names matplotlib will see (static instances carry names like "DM Sans 9pt").
"""
import argparse
import pathlib
import re
import sys
import urllib.request

UA = ("Mozilla/5.0 (Linux; U; Android 4.0.3; en-us; KFTT Build/IML74K) "
      "AppleWebKit/535.19 (KHTML, like Gecko) Silk/3.4 Mobile Safari/535.19")  # Google serves TTF to this UA
DEFAULT = ["DM Sans:400,500,600,700", "Inter:400,500,600,700", "Source Serif 4:400,600,700"]

p = argparse.ArgumentParser()
p.add_argument("--family", action="append", help='"Family:400,700" (repeatable)')
p.add_argument("--user", action="store_true", help="store in ~/.local/share/blogfig-fonts instead of <skill>/fonts")
a = p.parse_args()

dest = pathlib.Path.home() / ".local" / "share" / "blogfig-fonts" if a.user \
    else pathlib.Path(__file__).resolve().parent.parent / "fonts"
dest.mkdir(parents=True, exist_ok=True)

for spec in a.family or DEFAULT:
    fam, weights = spec.split(":") if ":" in spec else (spec, "400,700")
    q = fam.strip().replace(" ", "+") + ":" + weights
    req = urllib.request.Request(f"https://fonts.googleapis.com/css?family={q}", headers={"User-Agent": UA})
    try:
        css = urllib.request.urlopen(req, timeout=20).read().decode()
    except Exception as e:
        print(f"{fam}: download failed ({e})", file=sys.stderr)
        continue
    got = 0
    for w, url in re.findall(r"font-weight:\s*(\d+);\s*src:\s*url\(([^)]+\.ttf)\)", css):
        out = dest / f"{fam.replace(' ', '')}-{w}.ttf"
        if not out.exists():
            urllib.request.urlretrieve(url, out)
        got += 1
    print(f"{fam}: {got} weights -> {dest}")

try:
    import matplotlib.font_manager as fm  # noqa
    names = {}
    for f in dest.glob("*.ttf"):
        try:
            names.setdefault(fm.ttfFontProperty(fm.ft2font.FT2Font(str(f))).name, []).append(f.name)
        except Exception:
            pass
    for n, fs in sorted(names.items()):
        print(f'  matplotlib family name: "{n}"  ({len(fs)} files)')
except ImportError:
    print("(run with --with matplotlib to print the family names matplotlib will see)")
