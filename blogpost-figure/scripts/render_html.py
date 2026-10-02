# /// script
# requires-python = ">=3.10"
# dependencies = ["pillow"]
# ///
"""Render an HTML file to a retina PNG with headless Chrome/Chromium.

    uv run render_html.py diagram.html diagram.png --width 1000 [--scale 2] [--height auto]

The page is laid out at `--width` CSS px (a blog column: 650–1000; ~1500 for card dashboards) and
screenshotted at `--scale`x (2 = retina). Height is measured from the document (the template's
measure.js sets data-doc-height) unless --height is given. Relative `figure.css` / `measure.js`
links that do not resolve next to the HTML are rewritten to the skill's assets/ copies, so a template
copied elsewhere still renders styled. Falls back to Playwright if no Chrome binary is found
(`uv run --with playwright python -m playwright install chromium`). Writes a .webp next to the PNG.
"""
import argparse
import os
import pathlib
import re
import shutil
import subprocess
import sys

CANDIDATES = [
    os.environ.get("CHROME_BIN", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    shutil.which("google-chrome") or "", shutil.which("google-chrome-stable") or "",
    shutil.which("chromium") or "", shutil.which("chromium-browser") or "", shutil.which("chrome") or "",
]


def find_chrome() -> str | None:
    for c in CANDIDATES:
        if c and pathlib.Path(c).exists():
            return c
    return None


def measure_height(chrome: str, url: str, width: int) -> int:
    """Ask headless Chrome for the document height: --dump-dom runs the page's measure.js, which writes
    data-doc-height on <html> once web fonts are ready."""
    out = subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={width},800",
                          "--virtual-time-budget=4000", "--run-all-compositor-stages-before-draw", "--dump-dom", url],
                         capture_output=True, text=True, timeout=60)
    m = re.search(r'data-doc-height="(\d+)"', out.stdout)
    return int(m.group(1)) if m else 0


ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"


def resolve_assets(src: pathlib.Path) -> pathlib.Path:
    """If the HTML links figure.css / measure.js relatively and they are not next to it, write a temp copy
    with those links pointed at the skill's assets/ directory (fonts then resolve via ../fonts)."""
    html = src.read_text(encoding="utf-8")
    changed = False
    for name in ("figure.css", "measure.js"):
        if not (src.parent / name).exists() and (ASSETS / name).exists():
            new, n = re.subn(r'(href|src)=(["\'])(?:\./)?' + re.escape(name) + r'\2',
                             lambda m: f"{m.group(1)}={m.group(2)}{(ASSETS / name).as_uri()}{m.group(2)}", html)
            if n:
                html, changed = new, True
    if "measure.js" not in html:
        print("render_html: page has no measure.js; height will fall back to a tall window + crop", file=sys.stderr)
    if not changed:
        return src
    tmp = src.parent / f".{src.stem}.resolved.html"
    tmp.write_text(html, encoding="utf-8")
    return tmp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("png")
    ap.add_argument("--width", type=int, default=1000, help="CSS px width of the page (default 1000)")
    ap.add_argument("--height", default="auto", help="CSS px height or 'auto' (measured)")
    ap.add_argument("--scale", type=int, default=2, help="device scale factor (2 = retina)")
    ap.add_argument("--no-webp", action="store_true")
    a = ap.parse_args()
    src = pathlib.Path(a.html).resolve()
    page = resolve_assets(src)
    url = page.as_uri()
    chrome = find_chrome()
    out = pathlib.Path(a.png).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    if chrome:
        if a.height == "auto":
            # The template's own measure.js (assets/) sets data-doc-height once fonts are ready; --dump-dom runs it.
            h = measure_height(chrome, url, a.width) or 0
            if not h:
                print("render_html: could not measure the document height; using a 4000 px window and cropping",
                      file=sys.stderr)
                h = 4000
        else:
            h = int(a.height)
        cmd = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--default-background-color=00000000",
               f"--window-size={a.width},{h}", f"--force-device-scale-factor={a.scale}", "--virtual-time-budget=3000",
               f"--screenshot={out}", url]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if r.returncode != 0 or not out.exists():
            print(r.stderr[-2000:], file=sys.stderr)
            sys.exit("chrome screenshot failed")
        if a.height == "auto" and h == 4000:
            try:
                from PIL import Image, ImageChops
                im = Image.open(out).convert("RGBA")
                bg = Image.new("RGBA", im.size, im.getpixel((0, 0)))
                bbox = ImageChops.difference(im, bg).getbbox()
                if bbox:
                    im.crop((0, 0, im.width, min(im.height, bbox[3] + 24 * a.scale))).save(out)
            except ImportError:
                print("render_html: Pillow missing, cannot crop the fallback screenshot", file=sys.stderr)
    else:
        try:
            from playwright.sync_api import sync_playwright  # type: ignore
        except ImportError:
            sys.exit("No Chrome/Chromium found and Playwright not installed. Install Google Chrome, or:\n"
                     "  uv run --with playwright python -m playwright install chromium\n"
                     "  uv run --with playwright render_html.py ...")
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": a.width, "height": 800}, device_scale_factor=a.scale)
            pg.goto(url)
            pg.wait_for_timeout(300)
            pg.screenshot(path=str(out), full_page=(a.height == "auto"))
            b.close()
    if page is not src:
        page.unlink(missing_ok=True)
    print(out)
    if not a.no_webp:
        try:
            from PIL import Image
            Image.open(out).save(out.with_suffix(".webp"), quality=90, method=6)
            print(out.with_suffix(".webp"))
        except ImportError:
            print("render_html: Pillow missing, WebP skipped (run with --with pillow)", file=sys.stderr)


if __name__ == "__main__":
    main()
