# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.8", "numpy"]
# ///
"""blogfig — matplotlib helpers for blog-post figures (web, raster, retina).

Design language (derived from a set of research-blog figures): the title states the takeaway, a
gray subtitle states the measure, horizontal gridlines only, no left/top/right spines, every mark
carries its value, series are labelled directly (not in a legend box), one warm "hero" color
against steel blue / gray, uncertainty drawn as thin dark whiskers and explained in words,
footnotes carry the caveats.

Sizes are CSS pixels at 1x (a blog column is 650–1000 px wide). `save()` exports the designed
canvas at 2x (plus WebP), so the PNG is exactly 2 × the width you asked for.

    import sys; sys.path.insert(0, "/path/to/blogpost-figure/scripts")
    import blogfig as bf
    bf.use_style()                                   # white paper, sans font, px-based sizes
    fig, ax = bf.figure(width=900, height=540)       # px at 1x
    ...                                              # plot with the helpers below
    bf.headline(fig, "Takeaway as a sentence", "What is measured, in gray")
    bf.footnote(fig, "Whiskers: 95% intervals. n = 50 per bar.")
    bf.save(fig, "figures/fig_name")                 # fit() + fig_name.png (2x) + fig_name.webp

Order: plot → headline/footnote → save. `save()` calls `fit()`, which lays the axes out between
the title and the footnote and aligns everything on one left margin.
"""
from __future__ import annotations

import logging
import os
import pathlib
import re
import sys
import textwrap
from dataclasses import dataclass, fields

import matplotlib

if not os.environ.get("MPLBACKEND") and "matplotlib.pyplot" not in sys.modules:
    matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.font_manager as fm  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
import numpy as np  # noqa: E402

# --------------------------------------------------------------------------------------
# Palette (hex values sampled from the reference figures)
# --------------------------------------------------------------------------------------

# Text and chrome
INK = "#1F1F1E"            # titles, category labels, dark text
INK_SOFT = "#5A5A57"       # axis titles, group headers
MUTED = "#8A8A86"          # subtitles, sublabels, footnotes, tick labels
MUTED_LIGHT = "#AAAAA7"    # de-emphasized marks (rejected points, context series)
GRID = "#EAE9E5"           # gridlines, hairline rules
BASELINE = "#AFAFAB"       # x-axis baseline (a step darker than the grid)
PAPER = "#FFFFFF"          # default background
CREAM = "#FAF9F5"          # warm background ("ivory") for in-page / editorial figures
PANEL = "#F1F0EC"          # card / cell fill (warm light gray)
WHISKER = "#2B2B2A"        # error bars

# Hero (warm terracotta) and its tints
ACCENT = "#B86046"         # bars, lines, accent bar, panel letters, hero value labels (on white)
ACCENT_BRIGHT = "#D97757"  # brand-saturated variant (titles on cream, icons)
ACCENT_DARK = "#8F4A35"
ACCENT_MID = "#C7816C"     # secondary marks of the hero family; text color for pale tint bars
ACCENT_TINT = "#E0BAAF"    # lollipop stems, previous-generation bars
ACCENT_PALE = "#F7E9E3"    # gap bands, quote-bubble / card fills

# Comparison / baseline
BLUE = "#40668C"           # steel blue: the baseline or "before" series
BLUE_MID = "#7E98B1"
BLUE_TINT = "#9DB1C6"
NAVY = "#083262"
BLUE_RAMP = ["#70B0DC", "#3788C0", "#08529D"]          # ordinal: older -> newer generation

# Further families (one hue per family of things, ramps for ordinal conditions)
GREEN = "#0E6B54"
GREEN_BRIGHT = "#019E73"
GREEN_TINT = "#7DD0B6"
PURPLE = "#5C4474"
VIOLET = "#6258D2"
LAVENDER = "#8A6DC4"
PLUM = "#47267F"
OCHRE = "#B58C60"
OCHRE_DARK = "#8D5017"
SLATE = "#585850"
CRIMSON_RAMP = ["#EABBB1", "#BC5F67", "#992031", "#8E1025"]  # ordinal: mild -> severe

# Default categorical order: hero first, then baseline, then the rest.
SERIES = [ACCENT, BLUE, GREEN, VIOLET, OCHRE, SLATE, PLUM, GREEN_BRIGHT]


def ramp(color_list: list[str], n: int) -> list[str]:
    """Pick n evenly spaced colors from an ordinal ramp (keeps the end points)."""
    if n <= 1:
        return [color_list[-1]]
    idx = np.linspace(0, len(color_list) - 1, n)
    return [color_list[int(round(i))] for i in idx]


# --------------------------------------------------------------------------------------
# Type scale (CSS px at 1x) and px -> pt conversion
# --------------------------------------------------------------------------------------
LAYOUT_DPI = 100  # 1 inch of figure == 100 CSS px at 1x; save() multiplies by `scale`


def px(p: float) -> float:
    """Convert CSS px (at 1x) to matplotlib points for the LAYOUT_DPI canvas."""
    return p * 72.0 / LAYOUT_DPI


@dataclass
class TypeScale:
    title: int = 26        # bold, INK, the takeaway sentence at a 1000 px canvas; headline() scales it with width (20–28)
    subtitle: int = 16     # regular, MUTED, the measure / encoding
    section: int = 19      # medium, INK, header of a stacked section
    panel: int = 16        # semibold, INK, per-panel takeaway ("a  Safety improves...")
    axis: int = 14         # regular, INK_SOFT axis titles; INK category labels
    tick: int = 13         # regular, MUTED
    value: int = 17        # semibold, series color — the loudest text after the title
    label: int = 14        # direct series labels, legends
    sublabel: int = 12     # gray second line under a category
    footnote: int = 12     # regular, MUTED


T = TypeScale()
_T_BASE = TypeScale()

SANS_STACK = ["DM Sans 9pt", "DM Sans", "Figtree Light", "Figtree", "Inter", "Helvetica Neue",
              "Helvetica", "Arial", "DejaVu Sans"]
SERIF_STACK = ["Source Serif 4", "Newsreader 16pt 16pt", "Newsreader", "Charter", "Georgia", "DejaVu Serif"]

_FONT_DIRS = [
    pathlib.Path(__file__).resolve().parent.parent / "fonts",
    pathlib.Path.home() / ".local" / "share" / "blogfig-fonts",
]
_STATE: dict = {}


def register_fonts() -> list[str]:
    """Register any .ttf/.otf found in <skill>/fonts or ~/.local/share/blogfig-fonts."""
    added = []
    for d in _FONT_DIRS:
        if d.is_dir():
            for p in list(d.glob("*.ttf")) + list(d.glob("*.otf")):
                try:
                    fm.fontManager.addfont(str(p))
                    added.append(p.name)
                except Exception:
                    pass
    return added


def pick_font(stack: list[str]) -> str:
    names = {f.name for f in fm.fontManager.ttflist}
    for n in stack:
        if n in names:
            return n
    return "DejaVu Sans"


def use_style(theme: str = "white", font: str | None = None, serif_titles: bool = False, scale: float = 1.0,
              quiet: bool = False) -> dict:
    """Apply the blog style globally.

    theme: 'white' (default) or 'cream' (warm in-page / editorial variant).
    font: a registered family name (default: first of SANS_STACK that is installed).
    scale: multiplies the whole type scale (1.2 for phone-first figures).
    """
    logging.getLogger("matplotlib.font_manager").setLevel(logging.ERROR)  # fallback probes are noisy
    register_fonts()
    for f in fields(TypeScale):
        setattr(T, f.name, int(round(getattr(_T_BASE, f.name) * scale)))
    bg = CREAM if theme == "cream" else PAPER
    sans = font or pick_font(SANS_STACK)
    rc = {
        "figure.dpi": LAYOUT_DPI,
        "savefig.dpi": LAYOUT_DPI * 2,
        "figure.facecolor": bg,
        "axes.facecolor": bg,
        "savefig.facecolor": bg,
        "font.family": [sans] + [f for f in ("Inter", "DejaVu Sans") if f != sans],  # glyph fallback (†, ‡, →)
        "font.size": px(T.axis),
        "text.color": INK,
        "axes.labelcolor": INK_SOFT,
        "axes.labelsize": px(T.axis),
        "axes.labelpad": 8,
        "axes.titlesize": px(T.panel),
        "axes.titleweight": "semibold",
        "axes.titlelocation": "left",
        "axes.titlepad": 14,
        "axes.edgecolor": BASELINE,
        "axes.linewidth": 1.0,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.axisbelow": True,
        "grid.color": GRID,
        "grid.linewidth": 1.0,
        "grid.alpha": 1.0,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelcolor": MUTED,
        "ytick.labelcolor": MUTED,
        "xtick.labelsize": px(T.tick),
        "ytick.labelsize": px(T.tick),
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "xtick.minor.size": 0,
        "ytick.minor.size": 0,
        "xtick.major.pad": 8,
        "ytick.major.pad": 6,
        "lines.linewidth": 2.4,
        "lines.markersize": 7,
        "lines.solid_capstyle": "round",
        "patch.linewidth": 0,
        "legend.frameon": False,
        "legend.fontsize": px(T.label),
        "legend.handlelength": 1.2,
        "legend.handleheight": 0.9,
        "legend.borderaxespad": 0.2,
        "legend.columnspacing": 1.6,
        "errorbar.capsize": 0,
        "axes.prop_cycle": matplotlib.cycler(color=SERIES),
        "savefig.bbox": None,
        "savefig.pad_inches": 0.0,
        "svg.fonttype": "none",
    }
    plt.rcParams.update(rc)
    _STATE.update({"_sans": sans, "_bg": bg, "_theme": theme, "_scale": scale,
                   "_serif": pick_font(SERIF_STACK) if serif_titles else None})
    if not quiet and not _STATE.get("_announced"):
        print(f"blogfig: font {sans!r}, theme {theme}", file=sys.stderr)
        _STATE["_announced"] = True
    return rc


def _font(kind: str) -> list[str]:
    """Family list (with glyph fallbacks for †, ‡, →, ×) for text artists."""
    if kind == "serif":
        fam = _STATE.get("_serif") or pick_font(SERIF_STACK)
    else:
        fam = _STATE.get("_sans") or pick_font(SANS_STACK)
    return [fam] + [f for f in ("Inter", "DejaVu Sans") if f != fam]


# --------------------------------------------------------------------------------------
# Figure construction, measurement and layout
# --------------------------------------------------------------------------------------

def _meta(fig) -> dict:
    """Per-figure layout state; works for figures not created by bf.figure() too."""
    if not hasattr(fig, "_blogfig"):
        fig._blogfig = {"width": fig.get_figwidth() * fig.dpi, "height": fig.get_figheight() * fig.dpi}
    return fig._blogfig


def figure(width: int = 900, height: int | None = None, nrows: int = 1, ncols: int = 1, **kw):
    """Create a figure sized in CSS px at 1x. Default aspect 1:0.6; stacks are taller, 2×2 grids ≈ square.
    Budget: a 2-line title ≈ 70 px, subtitle ≈ 22 px per line, footnote ≈ 18 px per line, plus the plot."""
    if height is None:
        height = int(width * 0.6)
    fig, axes = plt.subplots(nrows, ncols, figsize=(width / LAYOUT_DPI, height / LAYOUT_DPI), **kw)
    fig._blogfig = {"width": width, "height": height}
    return fig, axes


def _renderer(fig):
    fig.canvas.draw()
    return fig.canvas.get_renderer()


def _fig_px(fig):
    return fig.get_figwidth() * fig.dpi, fig.get_figheight() * fig.dpi


def _text_height_frac(fig, artist) -> float:
    bb = artist.get_window_extent(renderer=_renderer(fig))
    return bb.height / _fig_px(fig)[1]


def wrap_to_width(fig, text: str, max_px: float, *, size_px: float, weight: str = "normal",
                  family: list[str] | None = None, balance: bool = True) -> str:
    """Greedy word-wrap using measured glyph widths; two-line results are balanced so the
    second line is not a one-word orphan."""
    renderer = _renderer(fig)
    probe = fig.text(0, 0, "", fontsize=px(size_px), fontweight=weight, fontfamily=family or _font("sans"))

    def width(s):
        probe.set_text(s)
        return probe.get_window_extent(renderer=renderer).width

    out = []
    for para in text.split("\n"):
        words = para.split()
        lines, line = [], ""
        for w in words:
            cand = (line + " " + w).strip()
            if width(cand) <= max_px or not line:
                line = cand
            else:
                lines.append(line)
                line = w
        lines.append(line)
        if balance and len(lines) == 2:
            a, b = lines[0].split(), lines[1].split()
            # move words from line 1 to line 2 while that makes the lines more even
            while len(a) > 1:
                na, nb = a[:-1], [a[-1]] + b
                if abs(width(" ".join(na)) - width(" ".join(nb))) < abs(width(" ".join(a)) - width(" ".join(b))) \
                        and width(" ".join(nb)) <= max_px:
                    a, b = na, nb
                else:
                    break
            lines = [" ".join(a), " ".join(b)]
        out.extend(lines)
    probe.remove()
    return "\n".join(out)


def headline(fig, title: str, subtitle: str | None = None, *, accent_bar: bool = True, x: float | None = None,
             top: float = 0.985, gap_px: int = 10, max_width_frac: float = 0.78, sub_width_frac: float = 0.82,
             serif: bool = False, color: str = INK, size: int | None = None, weight: str = "bold",
             ha: str = "left"):
    """Takeaway title (+ gray subtitle) at the top of the figure.

    Left-aligned on the figure's shared left margin by default (fit() aligns it with the tick labels);
    pass ha="center" for the plain centred variant (cream/matplotlib-native family, usually with
    accent_bar=False, weight="normal", color=ACCENT_BRIGHT). Title size follows the figure width
    (clamped 20–28 px at 1x) unless `size` is given. Call after plotting; save() lays the axes out below.
    """
    W, H = _fig_px(fig)
    meta = _meta(fig)
    scale = _STATE.get("_scale", 1.0)
    size = size or int(round(min(28, max(20, T.title * W / 1000)) * scale))  # T.title at 1000 px, clamped 20–28
    sub_size = T.subtitle if size >= 24 else max(13, int(round(size * 0.62)))
    if x is None:
        x = 0.5 if ha == "center" else 0.035
    max_px = (max_width_frac if ha != "center" else 0.9) * W
    y = top
    arts, fam = [], _font("serif" if serif else "sans")
    if accent_bar:
        bar = fig.add_artist(Line2D([x, x + 44 / W], [y - 2 / H] * 2, color=ACCENT, linewidth=px(5),
                                    solid_capstyle="butt", transform=fig.transFigure))
        y -= 20 / H
        arts.append(bar)
    t = fig.text(x, y, wrap_to_width(fig, title, max_px, size_px=size, weight=weight, family=fam), ha=ha,
                 va="top", fontsize=px(size), fontweight=weight, color=color, linespacing=0.95, fontfamily=fam)
    arts.append(t)
    y -= _text_height_frac(fig, t)
    if subtitle:
        y -= gap_px / H
        s = fig.text(x, y, wrap_to_width(fig, subtitle, (sub_width_frac if ha != "center" else 0.9) * W,
                                         size_px=sub_size), ha=ha, va="top", fontsize=px(sub_size), color=MUTED,
                     linespacing=1.05)
        arts.append(s)
        y -= _text_height_frac(fig, s)
    meta["headline_bottom"] = y
    meta["headline_artists"] = arts
    meta["headline_ha"] = ha
    return arts


def footnote(fig, text: str, *, x: float | None = None, y: float = 0.012, max_width_frac: float = 0.93):
    """Gray footnote at the bottom-left, aligned with the title (use † ‡ markers to tie it to items)."""
    W, H = _fig_px(fig)
    meta = _meta(fig)
    x = 0.035 if x is None else x
    t = fig.text(x, y, wrap_to_width(fig, text, (max_width_frac - x) * W, size_px=T.footnote, balance=False),
                 ha="left", va="bottom", fontsize=px(T.footnote), color=MUTED, linespacing=1.15)
    meta["footnote_top"] = y + _text_height_frac(fig, t)
    meta["footnote_artists"] = [t]
    return t


def section_header(target, *args, above_px: int | None = None, x: float | None = None, **kw):
    """Header for a stacked section, aligned on the shared left margin.

    Preferred form — anchored to the section's axes so fit() reserves room for it:
        section_header(ax, "Refusal rate on harmful requests", "Share of requests refused — higher is safer")
    The title sits `above_px` (default 96, or 70 without a subtitle) above the axes top, the gray method
    line below it; group headers at y=1.0 fit underneath. Legacy form: section_header(fig, y, title, sub).
    """
    from matplotlib.transforms import blended_transform_factory, ScaledTranslation
    if hasattr(target, "transAxes"):
        ax = target
        title, subtitle = args[0], (args[1] if len(args) > 1 else kw.get("subtitle"))
        fig = ax.figure
        margin = 0.035 if x is None else x
        above = above_px if above_px is not None else (96 if subtitle else 70)
        arts = []
        tr = blended_transform_factory(fig.transFigure, ax.transAxes) + ScaledTranslation(0, above / LAYOUT_DPI, fig.dpi_scale_trans)
        t = ax.text(margin, 1.0, title, transform=tr, ha="left", va="bottom", fontsize=px(T.section), fontweight="medium",
                    color=INK, clip_on=False)
        arts.append(t)
        if subtitle:
            tr2 = blended_transform_factory(fig.transFigure, ax.transAxes) + ScaledTranslation(0, (above - 28) / LAYOUT_DPI, fig.dpi_scale_trans)
            arts.append(ax.text(margin, 1.0, subtitle, transform=tr2, ha="left", va="bottom", fontsize=px(T.subtitle - 1),
                                color=MUTED, clip_on=False, linespacing=1.05))
        _meta(fig).setdefault("margin_artists", []).extend(arts)
        return arts
    fig, y, title = target, args[0], args[1]
    subtitle = args[2] if len(args) > 2 else kw.get("subtitle")
    x = 0.035 if x is None else x
    t = fig.text(x, y, title, ha="left", va="top", fontsize=px(T.section), fontweight="medium", color=INK)
    if subtitle:
        yy = y - _text_height_frac(fig, t) - 6 / _fig_px(fig)[1]
        fig.text(x, yy, subtitle, ha="left", va="top", fontsize=px(T.subtitle - 1), color=MUTED, linespacing=1.05)
    _meta(fig).setdefault("margin_artists", []).append(t)
    return t


def fit(fig, *, margin_frac: float = 0.035, gap_top_px: int = 30, gap_bottom_px: int = 22, iterations: int = 3,
        grow: bool = True, min_plot_frac: float = 0.3):
    """Lay the axes out so that everything they own (tick labels, titles, annotations) sits between the
    headline and the footnote and inside the side margins, then align headline/footnote on the left
    margin. If the text leaves less than `min_plot_frac` of the height for the plot, the figure grows
    (grow=True) instead of squeezing the axes. Called by save(); call it yourself to inspect."""
    meta = _meta(fig)
    if not fig.axes:
        return
    grows = 0
    for _ in range(iterations + 4):
        W, H = _fig_px(fig)
        top_limit = meta.get("headline_bottom", 1.0) - (gap_top_px / H if "headline_bottom" in meta else 0.03)
        bottom_limit = meta.get("footnote_top", 0.0) + (gap_bottom_px / H if "footnote_top" in meta else 0.03)
        renderer = _renderer(fig)
        bbs = [b for b in (a.get_tightbbox(renderer) for a in fig.axes) if b is not None]
        if not bbs:
            return
        ext_top, ext_bot = max(b.y1 for b in bbs) / H, min(b.y0 for b in bbs) / H
        ext_left, ext_right = min(b.x0 for b in bbs) / W, max(b.x1 for b in bbs) / W
        ax_top, ax_bot = max(a.get_position().y1 for a in fig.axes), min(a.get_position().y0 for a in fig.axes)
        ax_left, ax_right = min(a.get_position().x0 for a in fig.axes), max(a.get_position().x1 for a in fig.axes)
        new_top = top_limit - (ext_top - ax_top)
        new_bot = bottom_limit + (ax_bot - ext_bot)
        if new_top - new_bot < min_plot_frac:
            if grow and grows < 4:
                deficit = min_plot_frac - (new_top - new_bot)
                fig.set_figheight(fig.get_figheight() * (1 + deficit + 0.02))
                meta["height"] = fig.get_figheight() * fig.dpi
                _reflow_text(fig)          # text is fixed in px, so its figure-fraction anchors moved
                grows += 1
                continue
            new_bot = new_top - min_plot_frac
        sy = (new_top - new_bot) / (ax_top - ax_bot) if ax_top > ax_bot else 1.0
        # horizontal: content between margin and 1 - margin
        new_left = margin_frac + (ax_left - ext_left)
        new_right = (1 - margin_frac) - (ext_right - ax_right)
        sx = (new_right - new_left) / (ax_right - ax_left) if ax_right > ax_left else 1.0
        for a in fig.axes:
            p = a.get_position()
            a.set_position([new_left + (p.x0 - ax_left) * sx, new_bot + (p.y0 - ax_bot) * sy,
                            p.width * sx, p.height * sy])
        if abs(ext_top - top_limit) < 1 / H and abs(ext_bot - bottom_limit) < 1 / H \
                and abs(ext_left - margin_frac) < 1 / W:
            break
    _align_margin_text(fig, margin_frac)
    for hook in meta.get("relayout", []):
        hook()


def _reflow_text(fig):
    """After the figure height changed, re-anchor headline/footnote (figure-fraction coords moved)."""
    meta = _meta(fig)
    W, H = _fig_px(fig)
    arts = meta.get("headline_artists", [])
    if arts:
        y = 0.985
        for a in arts:
            if isinstance(a, Line2D):
                a.set_ydata([y - 2 / H] * 2)
                y -= 20 / H
            else:
                a.set_y(y)
                y -= _text_height_frac(fig, a) + (10 / H if a is not arts[-1] else 0)
        meta["headline_bottom"] = y
        for row in meta.get("below_headline", []):   # shared legend rows hang under the headline
            yy = meta["headline_bottom"] - (16 + row["row_px"] / 2) / H
            for a in row["artists"]:
                if isinstance(a, Line2D):
                    a.set_ydata([yy] * len(a.get_ydata()))
                else:
                    a.set_y(yy)
            meta["headline_bottom"] = yy - (row["row_px"] / 2 + 4) / H
    if meta.get("footnote_artists"):
        t = meta["footnote_artists"][0]
        meta["footnote_top"] = t.get_position()[1] + _text_height_frac(fig, t)


def _align_margin_text(fig, margin_frac: float):
    meta = _meta(fig)
    if meta.get("headline_ha", "left") == "left":
        for a in meta.get("headline_artists", []):
            if isinstance(a, Line2D):
                W = _fig_px(fig)[0]
                a.set_xdata([margin_frac, margin_frac + 44 / W])
            else:
                a.set_x(margin_frac)
    for a in meta.get("footnote_artists", []) + meta.get("margin_artists", []):
        a.set_x(margin_frac)


def panel_title(ax, text: str, letter: str | None = None, *, sub: str | None = None, sub_color: str = ACCENT,
                wrap: int | None = None, pad: int = 14):
    """Per-panel header: a takeaway sentence (semibold, INK) wrapped to the axes width, an optional small
    accent letter (a, b, c…) hanging left of the first line, and an optional one-line subtitle in the
    accent color naming the metric and its direction ("Strike rate — higher is better").
    Give panels that share a row the same `pad` so their headers align."""
    fig = ax.figure
    if wrap:
        wrapped = textwrap.fill(text, wrap)
    else:
        ax_w = ax.get_window_extent(renderer=_renderer(fig)).width
        wrapped = wrap_to_width(fig, text, ax_w * 1.04, size_px=T.panel, weight="semibold")
    nlines = wrapped.count("\n") + 1
    title_pad = pad + (T.label + 6 if sub else 0)
    ax.set_title(wrapped, loc="left", fontsize=px(T.panel), fontweight="semibold", color=INK, pad=title_pad, x=0.0,
                 linespacing=1.15)
    if sub:
        ax.annotate(sub, xy=(0, 1), xycoords="axes fraction", xytext=(0, pad - 2), textcoords="offset points",
                    ha="left", va="bottom", fontsize=px(T.label), color=sub_color, annotation_clip=False)
    if letter:
        first_line_offset = title_pad + (nlines - 1) * px(T.panel) * 1.15 * 1.2
        ax.annotate(letter, xy=(0, 1), xycoords="axes fraction", xytext=(-6, first_line_offset + 1),
                    textcoords="offset points", ha="right", va="bottom", fontsize=px(T.panel),
                    fontweight="semibold", color=ACCENT, annotation_clip=False)


def group_header(ax, x0: float, x1: float, text: str, *, y: float = 1.0, color: str = INK_SOFT, rule: bool = True):
    """Label a group of bars (data x-range x0..x1) with text and a hairline, just above the plot area.
    Leave ~15 % headroom above the tallest value label (e.g. ylim top = 1.18 × max)."""
    trans = ax.get_xaxis_transform()  # x in data, y in axes fraction
    ax.text(x0, y + 0.02, text, transform=trans, ha="left", va="bottom", fontsize=px(T.label), color=color,
            clip_on=False, linespacing=1.15)
    if rule:
        ax.plot([x0, x1], [y, y], transform=trans, color=BASELINE, linewidth=1, clip_on=False, solid_capstyle="butt")


# --------------------------------------------------------------------------------------
# Axes tidying
# --------------------------------------------------------------------------------------

def tidy(ax, *, xlabel: str | None = None, ylabel: str | None = None, ypct: bool = False, xpct: bool = False,
         yunit: str = "", xunit: str = "", baseline: bool = True, grid: str = "y", ymax_pad: float = 0.0,
         left_spine: bool = False, ymin0: bool = True, nticks: int | None = 5):
    """Apply the house axes conventions: only the bottom spine (a light baseline), horizontal gridlines
    only, no tick marks, units baked into tick labels ('50%', '5 h'), y starting at zero for bars.
    Ticks you set explicitly (ax.set_yticks) before calling tidy() are kept; otherwise 2–5 round ticks."""
    ax.grid(False)
    if grid in ("y", "both"):
        ax.grid(True, axis="y", color=GRID, linewidth=1)
    if grid in ("x", "both"):
        ax.grid(True, axis="x", color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_visible(left_spine)
    ax.spines["bottom"].set_visible(baseline)
    ax.spines["bottom"].set_color(BASELINE)
    ax.tick_params(length=0)
    if xlabel is not None:
        ax.set_xlabel(xlabel, color=INK_SOFT)
    if ylabel is not None:
        ax.set_ylabel(ylabel, color=INK_SOFT)
    if ypct:
        ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=100, decimals=0))
    elif yunit:
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}{yunit}"))
    if xpct:
        ax.xaxis.set_major_formatter(mticker.PercentFormatter(xmax=100, decimals=0))
    elif xunit:
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}{xunit}"))
    if ymin0 and ax.get_yscale() == "linear":
        lo, hi = ax.get_ylim()
        if lo >= 0 or hi <= 0:
            ax.set_ylim(0, hi * (1 + ymax_pad)) if hi > 0 else ax.set_ylim(lo * (1 + ymax_pad), 0)
    if nticks and isinstance(ax.yaxis.get_major_locator(), mticker.AutoLocator):
        ax.yaxis.set_major_locator(mticker.MaxNLocator(nbins=nticks, steps=[1, 2, 2.5, 5, 10]))
    return ax


def sparse_yticks(ax, ticks: list[float]):
    """Keep only the given y ticks/gridlines (e.g. [50, 100])."""
    ax.set_yticks(ticks)


def human(v: float) -> str:
    """10k / 300k / 1M style numbers (values below 1000 print as-is: 1, 2, 128)."""
    for div, suf in ((1e9, "B"), (1e6, "M"), (1e3, "k")):
        if abs(v) >= div:
            s = f"{v / div:.1f}".rstrip("0").rstrip(".")
            return f"{s}{suf}"
    return f"{v:g}"


def log_axis(ax, which: str = "x", ticks: list[float] | None = None, fmt=None):
    """Log scale with human tick labels (10k, 30k, 100k, …; small values print as integers) and no
    minor ticks. fmt: optional callable value -> label."""
    axis = ax.xaxis if which == "x" else ax.yaxis
    (ax.set_xscale if which == "x" else ax.set_yscale)("log")
    if ticks:
        axis.set_major_locator(mticker.FixedLocator(ticks))
    f = fmt or human
    axis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f(v)))
    axis.set_minor_locator(mticker.NullLocator())


def fmt_duration(hours: float, tick: bool = False) -> str:
    """'59m' below one hour; '1.8h' for annotations; '3h' for ticks."""
    m = round(hours * 60)
    if m < 60:
        return f"{m}m"
    return f"{hours:g}h" if tick else f"{hours:.1f}h"


def duration_axis(ax, which: str = "x"):
    """Tick labels like 0m, 1h, 3h, 6h on an hours-valued axis."""
    axis = ax.xaxis if which == "x" else ax.yaxis
    axis.set_major_formatter(mticker.FuncFormatter(lambda v, _: fmt_duration(v, tick=True)))


# --------------------------------------------------------------------------------------
# Marks with built-in direct labels
# --------------------------------------------------------------------------------------

def _per_item(v, n: int, default, name: str) -> list:
    """Broadcast a per-item argument (None, scalar, length-1 or length-n sequence) to n items."""
    if v is None:
        return [default] * n
    if isinstance(v, (str, bool, int, float)):
        return [v] * n
    v = list(v)
    if len(v) == 1:
        return v * n
    if len(v) != n:
        raise ValueError(f"{name}: expected {n} values (or 1), got {len(v)}")
    return v


def bars(ax, x, heights, *, colors=None, width: float = 0.62, labels: bool = True, fmt: str = "{:.0f}%",
         label_colors=None, hollow=None, errors=None, label_pad_px: int = 6, zero_line: bool = True,
         label_size: int | None = None, cap: int = 0, label_weight: str = "semibold"):
    """Vertical bars with value labels above (colored like the bar), optional hollow bars (outline only —
    a transformed variant of the same entity), optional symmetric or (lo, hi) whiskers (thin, dark, cap=0;
    use cap=2 when bars are dense), and zero values drawn as a thin colored strip so '0%' has an anchor.
    label_colors: use a darker tone for text on pale bars (e.g. ACCENT_MID for ACCENT_TINT bars).
    """
    x = np.asarray(x, dtype=float)
    heights = np.asarray(heights, dtype=float)
    n = len(heights)
    colors = _per_item(colors, n, SERIES[0], "colors")
    hollow = _per_item(hollow, n, False, "hollow")
    label_colors = _per_item(label_colors, n, None, "label_colors")
    label_colors = [lc or c for lc, c in zip(label_colors, colors)]
    bg = plt.rcParams["axes.facecolor"]
    rects = []
    for xi, h, c, hol in zip(x, heights, colors, hollow):
        if hol:
            r = ax.bar(xi, h, width=width, facecolor=bg, edgecolor=c, linewidth=2.2)
        else:
            r = ax.bar(xi, h, width=width, color=c, linewidth=0)
        rects.append(r[0])
        if zero_line and h == 0:
            ax.plot([xi - width / 2, xi + width / 2], [0, 0], color=c, linewidth=3, solid_capstyle="butt",
                    zorder=3, clip_on=False)
    if errors is not None:
        err = np.asarray(errors, dtype=float)
        ax.errorbar(x, heights, yerr=err, fmt="none", ecolor=WHISKER, elinewidth=1.4, capsize=cap, capthick=1.4,
                    zorder=4)
        hi = heights + (err[1] if err.ndim == 2 else err)
        lo = heights - (err[0] if err.ndim == 2 else err)
    else:
        hi = lo = heights
    if labels:
        for xi, h, top, bot, lc in zip(x, heights, hi, lo, label_colors):
            if h < 0:
                ax.annotate(fmt.format(h), xy=(xi, bot), xytext=(0, -px(label_pad_px)), textcoords="offset points",
                            ha="center", va="top", fontsize=px(label_size or T.value), fontweight=label_weight,
                            color=lc, annotation_clip=False)
            else:
                ax.annotate(fmt.format(h), xy=(xi, top), xytext=(0, px(label_pad_px)), textcoords="offset points",
                            ha="center", va="bottom", fontsize=px(label_size or T.value), fontweight=label_weight,
                            color=lc, annotation_clip=False)
    ax.margins(x=0.08)
    return rects


def category_labels(ax, x, labels, sublabels=None, *, rotation: int = 0, size: int | None = None, sub_x=None):
    """Category tick labels in INK with an optional gray second line per category (model size, date,
    condition). Pass None for categories without a qualifier; omit qualifiers that would only repeat
    the subtitle. sub_x: x positions for the sublabels when they differ from the tick positions
    (e.g. "as released" / "abliterated" under the two bars of a pair that shares one name)."""
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, color=INK, fontsize=px(size or T.axis), rotation=rotation,
                       ha="right" if rotation else "center", rotation_mode="anchor" if rotation else "default")
    for lab in ax.get_xticklabels():
        lab.set_color(INK)
    if sublabels is not None:
        xs = list(sub_x) if sub_x is not None else list(x)
        max_lines = max(str(lab).count("\n") + 1 for lab in labels)
        for i, (xi, sub) in enumerate(zip(xs, sublabels)):
            if not sub:
                continue
            nlines = (str(labels[i]).count("\n") + 1) if sub_x is None else max_lines
            drop = px(8 + (size or T.axis) * 1.25 * nlines + 4)  # pt below the baseline
            ax.annotate(sub, xy=(xi, 0), xycoords=("data", "axes fraction"), xytext=(0, -drop),
                        textcoords="offset points", ha="center", va="top", fontsize=px(T.sublabel), color=MUTED,
                        annotation_clip=False, linespacing=1.1)


def value_label(ax, x, y, text, *, color=ACCENT, dx: int = 0, dy: int = 6, ha="center", va="bottom",
                size: int | None = None, weight="semibold"):
    """A single colored value/endpoint label offset (dx, dy px) from a data point."""
    return ax.annotate(text, xy=(x, y), xytext=(px(dx), px(dy)), textcoords="offset points", ha=ha, va=va,
                       fontsize=px(size or T.value), fontweight=weight, color=color, annotation_clip=False)


def label_line(ax, line, text: str, *, where: str = "end", dx: int = 8, dy: int = 0, color=None,
               size: int | None = None, va: str = "center", weight="medium"):
    """Direct label for a line: at its end (right of the last point) or above/below its midpoint
    (where="mid", dy positive = above)."""
    xs, ys = line.get_xdata(), line.get_ydata()
    color = color or line.get_color()
    if where == "end":
        return ax.annotate(text, xy=(xs[-1], ys[-1]), xytext=(px(dx), px(dy)), textcoords="offset points",
                           ha="left", va=va, fontsize=px(size or T.label), fontweight=weight, color=color,
                           annotation_clip=False)
    i = len(xs) // 2
    dy = dy or 10
    return ax.annotate(text, xy=(xs[i], ys[i]), xytext=(px(dx), px(dy)), textcoords="offset points", ha="center",
                       va="bottom" if dy > 0 else "top", fontsize=px(size or T.label), fontweight=weight,
                       color=color, annotation_clip=False)


def right_labels(ax, items, *, x: float | None = None, min_gap_px: int | None = None, size: int | None = None,
                 name_color=None, weight="medium", pad_px: int = 12):
    """Leaderboard-style labels at the right edge: a right-aligned VALUE column and a NAME column, each
    row at its curve's final y, rows nudged apart so they never overlap (re-done after fit()).
    items = [(y, value_text, name, color), ...]. Reserve the gutter with fig.subplots_adjust(right=0.6)
    or let fit() shrink the axes; call after set_xlim.
    """
    fig = ax.figure
    renderer = _renderer(fig)
    fs = px(size or T.label)
    gap = (min_gap_px or int((size or T.label) * 1.55)) * fig.dpi / LAYOUT_DPI
    items = sorted(items, key=lambda it: it[0])
    if x is None:
        x = ax.get_xlim()[1]
    probe = ax.text(0, 0, "", fontsize=fs, fontweight="semibold")
    wmax = 0
    for _, val, _, _ in items:
        probe.set_text(str(val))
        wmax = max(wmax, probe.get_window_extent(renderer=renderer).width)
    probe.remove()
    wmax_pt = wmax * 72 / fig.dpi
    out = []
    for (y, val, name, color) in items:
        a = ax.annotate(str(val), xy=(x, y), xytext=(px(pad_px) + wmax_pt, 0), textcoords="offset points", ha="right",
                        va="center", fontsize=fs, fontweight="semibold", color=color, annotation_clip=False)
        b = ax.annotate(name, xy=(x, y), xytext=(px(pad_px) + wmax_pt + 9, 0), textcoords="offset points", ha="left",
                        va="center", fontsize=fs, fontweight=weight, color=name_color or color, annotation_clip=False)
        out.append((a, b))

    def _relayout():  # separate the rows in display space for the current axes size
        ys = np.array([ax.transData.transform((0, it[0]))[1] for it in items], dtype=float)
        for i in range(1, len(ys)):
            if ys[i] - ys[i - 1] < gap:
                ys[i] = ys[i - 1] + gap
        top = ax.transAxes.transform((0, 1))[1]
        if ys[-1] > top:
            ys -= ys[-1] - top
        for (a, b), yd in zip(out, ys):
            yy = ax.transData.inverted().transform((0, yd))[1]
            a.xy = (x, yy)
            b.xy = (x, yy)

    _relayout()
    _meta(fig).setdefault("relayout", []).append(_relayout)
    return out


def inline_legend(ax_or_fig, entries, *, y: float | None = 1.0, x: float = 0.0, size: int | None = None,
                  gap_px: int = 18, marker_px: int = 10, fig_coords: bool = False, align: str = "left"):
    """A frameless single-row legend: a small glyph then the label in the series color, placed above the
    axes (axes-fraction coords) or anywhere in figure coords (fig_coords=True).
    entries = [(label, color, kind)] or [(label, swatch_color, kind, text_color)] for pale swatches;
    kind in {'square','line','dot','x','whisker'}. align='center' centres the row on the host.
    For a shared legend under the headline of a panel figure, call headline() first and pass the
    figure with y=None: the row is placed just below the subtitle and fit() keeps the panels under it.
    Glyphs are drawn in points, so later layout changes do not distort them.
    """
    ax = ax_or_fig if hasattr(ax_or_fig, "transAxes") else None
    fig = ax.figure if ax else ax_or_fig
    use_fig = fig_coords or ax is None
    trans = fig.transFigure if use_fig else ax.transAxes
    host = fig if use_fig else ax
    renderer = _renderer(fig)
    Wpx = _fig_px(fig)[0] if use_fig else ax.get_window_extent(renderer=renderer).width
    fx = lambda p: p / Wpx  # px -> fraction of host width
    label_size = px(size or T.label)
    below = None
    if use_fig and y is None:
        meta = _meta(fig)
        H = _fig_px(fig)[1]
        row_px = (size or T.label) * 1.3
        y = meta.get("headline_bottom", 0.97) - (16 + row_px / 2) / H
        meta["headline_bottom"] = y - (row_px / 2 + 4) / H
        below = {"row_px": row_px, "artists": []}
        meta.setdefault("below_headline", []).append(below)
        if align == "left":
            x = 0.035
    elif y is None:
        y = 1.0
    made = []
    _orig_add_artist, _orig_text = host.add_artist, host.text

    def add_artist(a):
        made.append(a)
        return _orig_add_artist(a)

    def text(*a, **k):
        t = _orig_text(*a, **k)
        made.append(t)
        return t
    host.add_artist, host.text = add_artist, text
    entries = [e if len(e) == 4 else (e[0], e[1], e[2], None) for e in entries]

    def glyph_w(kind):
        return 2.2 * marker_px if kind == "line" else marker_px

    if align == "center":
        probe = host.text(0, 0, "", transform=trans, fontsize=label_size, fontweight="medium")
        total = 0.0
        for label, _, kind, _ in entries:
            probe.set_text(label)
            total += glyph_w(kind) + 7 + probe.get_window_extent(renderer=renderer).width + gap_px
        probe.remove()
        x = 0.5 - fx(total - gap_px) / 2
    xpos = x
    for label, color, kind, text_color in entries:
        cx = xpos + fx(glyph_w(kind) / 2)
        if kind == "square":
            host.add_artist(Line2D([cx], [y], transform=trans, marker="s", markersize=px(marker_px), color=color,
                                   linestyle="none", markeredgewidth=0, clip_on=False))
        elif kind == "line":
            host.add_artist(Line2D([xpos, xpos + fx(2.2 * marker_px)], [y, y], transform=trans, color=color,
                                   linewidth=px(3), clip_on=False))
        elif kind == "dot":
            host.add_artist(Line2D([cx], [y], transform=trans, marker="o", markersize=px(marker_px), color=color,
                                   linestyle="none", markeredgewidth=0, clip_on=False))
        elif kind == "x":
            host.add_artist(Line2D([cx], [y], transform=trans, marker="x", markersize=px(marker_px),
                                   markeredgewidth=px(2), color=color, linestyle="none", clip_on=False))
        else:  # whisker
            host.add_artist(Line2D([cx], [y], transform=trans, marker="|", markersize=px(marker_px * 1.6),
                                   markeredgewidth=px(1.6), color=WHISKER, linestyle="none", clip_on=False))
        xpos += fx(glyph_w(kind) + 7)
        t = host.text(xpos, y, label, transform=trans, ha="left", va="center", fontsize=label_size,
                      color=text_color or (INK_SOFT if kind == "whisker" else color), fontweight="medium",
                      clip_on=False)
        xpos += fx(t.get_window_extent(renderer=renderer).width + gap_px)
    del host.add_artist, host.text  # restore the class methods
    if below is not None:
        below["artists"] = made


def lollipop(ax, categories, values, *, sublabels=None, fmt: str = "{:.1f} h", color=ACCENT, stem=ACCENT_TINT,
             hollow=None, summary: tuple | None = None, summary_label: str = "Mean", summary_sub: str | None = None,
             xunit: str = " h", dot_px: int = 13, auto_xlim: bool = True):
    """Horizontal dot-and-stem chart (rows top-to-bottom in the order given) with a value at each dot and
    an optional summary row (mean with CI) under a hairline. summary = (mean, lo, hi, text, subtext).
    color/hollow may be per-item lists (gray or hollow dots de-emphasise caveated rows). Rows with a
    None/'' sublabel get a single centred label. For percentages use fmt="{:.0f}%", xunit="%".
    Row budget: ~45 px per row at 1x, ~60 with sublabels, plus ~90 px for the summary row.
    """
    n = len(values)
    colors = _per_item(color, n, ACCENT, "color")
    hollows = _per_item(hollow, n, False, "hollow")
    subs = _per_item(sublabels, n, None, "sublabels") if sublabels is not None else [None] * n
    ys = np.arange(n)[::-1] + (1.6 if summary else 0)
    bg = plt.rcParams["axes.facecolor"]
    labels_ = []
    for y, v, c, hol in zip(ys, values, colors, hollows):
        ax.plot([0, v], [y, y], color=stem, linewidth=px(5), solid_capstyle="butt", zorder=2, clip_on=False)
        if hol:
            ax.plot([v], [y], marker="o", markersize=px(dot_px), markerfacecolor=bg, markeredgecolor=c,
                    markeredgewidth=px(2), linestyle="none", zorder=3, clip_on=False)
        else:
            ax.plot([v], [y], marker="o", markersize=px(dot_px), color=c, linestyle="none", zorder=3, clip_on=False)
        labels_.append(ax.annotate(fmt.format(v), xy=(v, y), xytext=(px(12), 0), textcoords="offset points",
                                   ha="left", va="center", fontsize=px(T.value), fontweight="semibold", color=c,
                                   annotation_clip=False))
    ax.set_yticks(ys)
    ax.set_yticklabels([])
    for y, c_, s in zip(ys, categories, subs):
        if s:
            ax.annotate(c_, xy=(0, y), xycoords=("axes fraction", "data"), xytext=(-10, px(2)),
                        textcoords="offset points", ha="right", va="bottom", fontsize=px(T.axis), color=INK,
                        annotation_clip=False)
            ax.annotate(s, xy=(0, y), xycoords=("axes fraction", "data"), xytext=(-10, -px(2)),
                        textcoords="offset points", ha="right", va="top", fontsize=px(T.sublabel), color=MUTED,
                        annotation_clip=False)
        else:
            ax.annotate(c_, xy=(0, y), xycoords=("axes fraction", "data"), xytext=(-10, 0), textcoords="offset points",
                        ha="right", va="center", fontsize=px(T.axis), color=INK, annotation_clip=False)
    right_most = [max(values)]
    if summary:
        mean, lo, hi, text, subtext = summary
        ysum = 0.0
        ax.axhline(1.0, color=GRID, linewidth=1.2, zorder=1)
        ax.plot([lo, hi], [ysum, ysum], color=INK, linewidth=px(4), solid_capstyle="butt", zorder=3)
        ax.plot([mean], [ysum], marker="D", markersize=px(dot_px), color=INK, zorder=4)
        labels_.append(ax.annotate(text, xy=(hi, ysum), xytext=(px(14), px(2)), textcoords="offset points",
                                   ha="left", va="bottom", fontsize=px(T.value), fontweight="semibold", color=INK,
                                   annotation_clip=False))
        if subtext:
            labels_.append(ax.annotate(subtext, xy=(hi, ysum), xytext=(px(14), -px(2)), textcoords="offset points",
                                       ha="left", va="top", fontsize=px(T.sublabel), color=MUTED, annotation_clip=False))
        ax.annotate(summary_label, xy=(0, ysum), xycoords=("axes fraction", "data"), xytext=(-10, px(2) if summary_sub else 0),
                    textcoords="offset points", ha="right", va="bottom" if summary_sub else "center",
                    fontsize=px(T.axis), fontweight="semibold", color=INK, annotation_clip=False)
        if summary_sub:
            ax.annotate(summary_sub, xy=(0, ysum), xycoords=("axes fraction", "data"), xytext=(-10, -px(2)),
                        textcoords="offset points", ha="right", va="top", fontsize=px(T.sublabel), color=MUTED,
                        annotation_clip=False)
        right_most.append(hi)
    ax.set_ylim(-0.9, ys[0] + 0.8)
    ax.grid(False)
    ax.grid(True, axis="x", color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(BASELINE)
    ax.tick_params(length=0)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:g}{xunit}"))
    ax.set_xlim(left=0)
    if auto_xlim:
        # extend the x-range so the right-most value/summary text stays inside the axes box
        fig = ax.figure
        renderer = _renderer(fig)
        ax_bb = ax.get_window_extent(renderer=renderer)
        overflow = max((lab.get_window_extent(renderer=renderer).x1 for lab in labels_), default=ax_bb.x1) - ax_bb.x1
        if overflow > 0:
            x0, x1 = ax.get_xlim()
            ax.set_xlim(x0, x1 + (x1 - x0) * (overflow + 6) / ax_bb.width)


def curve(ax, x, y, *, color=ACCENT, lw: float | None = None, dots: bool = True, dot_px: int = 7, hero: bool = False):
    """A metric sampled at a few budgets/sizes (pass@k, scaling): straight segments with a dot at every
    measured point; hero=True draws it a step heavier. End dots are not clipped at the axes edge."""
    lw = lw or (2.6 if hero else 1.8)
    (line,) = ax.plot(x, y, color=color, linewidth=lw, marker="o" if dots else None, markersize=px(dot_px),
                      markeredgewidth=0, zorder=3 + hero, clip_on=False)
    return line


def step_curve(ax, x, y, *, color=ACCENT, end_dot: bool = True, lw: float | None = None, where: str = "post",
               hero: bool = False):
    """Step curve for event-count / survival data (share solved vs budget) with a dot at the final point."""
    lw = lw or (2.4 if hero else 1.8)
    (line,) = ax.step(x, y, where=where, color=color, linewidth=lw, zorder=3 + hero)
    if end_dot:
        ax.plot([x[-1]], [y[-1]], marker="o", markersize=px(7), color=color, zorder=4, clip_on=False)
    return line


def terminal_marker(ax, x, y, text: str, *, color=ACCENT, dx: int = 10, dy: int = 0, size: int | None = None):
    """Large 'X' at the last point of a run that stopped / was cut off, with a small label (its stop time)."""
    ax.plot([x], [y], marker="X", markersize=px(18), color=color, markeredgecolor=plt.rcParams["axes.facecolor"],
            markeredgewidth=1.2, linestyle="none", zorder=5, clip_on=False)
    return ax.annotate(text, xy=(x, y), xytext=(px(dx), px(dy)), textcoords="offset points", ha="left", va="center",
                       fontsize=px(size or T.sublabel), color=color, annotation_clip=False)


def whiskers(ax, x, y, lo, hi, *, color=WHISKER, lw: float = 1.4, cap: int = 0, horizontal: bool = False):
    """Thin dark error whiskers from lo to hi (absolute bounds, not offsets)."""
    x, y, lo, hi = map(np.asarray, (x, y, lo, hi))
    if horizontal:
        ax.errorbar(y, x, xerr=[y - lo, hi - y], fmt="none", ecolor=color, elinewidth=lw, capsize=cap, capthick=lw,
                    zorder=4)
    else:
        ax.errorbar(x, y, yerr=[y - lo, hi - y], fmt="none", ecolor=color, elinewidth=lw, capsize=cap, capthick=lw,
                    zorder=4)


def reference_line(ax, y: float, text: str | None = None, *, color=BASELINE, text_color=MUTED, side: str = "outside",
                   size: int | None = None):
    """Dashed horizontal reference (parity 50%, chance level, a target). The label sits just outside the
    axes on the right at the line's height (side="outside"; fit() makes room), or above the line at the
    left/right end inside the plot (side="left"/"right") when that corner is empty. Pass text=None and
    explain the line in the footnote when neither fits."""
    ax.axhline(y, color=color, linewidth=1.2, linestyle=(0, (5, 4)), zorder=1)
    if text:
        if side == "outside":
            return ax.annotate(text, xy=(1.0, y), xycoords=("axes fraction", "data"), xytext=(px(8), 0),
                               textcoords="offset points", ha="left", va="center", fontsize=px(size or T.sublabel),
                               color=text_color, annotation_clip=False)
        xa = 0.995 if side == "right" else 0.005
        return ax.annotate(text, xy=(xa, y), xycoords=("axes fraction", "data"), xytext=(0, px(4)),
                           textcoords="offset points", ha="right" if side == "right" else "left", va="bottom",
                           fontsize=px(size or T.sublabel), color=text_color, annotation_clip=False)


def gap_band(ax, x, y_hi, y_lo, text: str | None = None, *, color=ACCENT_PALE, text_color=ACCENT,
             size: int | None = None, at: str = "widest"):
    """Emphasise the difference between two series: fill the band between them in the hero tint and print
    the delta at its widest point (at='widest') or at the end (at='end')."""
    x, y_hi, y_lo = map(np.asarray, (x, y_hi, y_lo))
    ax.fill_between(x, y_lo, y_hi, color=color, linewidth=0, zorder=1)
    if text:
        i = int(np.argmax(y_hi - y_lo)) if at == "widest" else len(x) - 1
        return ax.annotate(text, xy=(x[i], (y_hi[i] + y_lo[i]) / 2), xytext=(-px(8), 0), textcoords="offset points",
                           ha="right", va="center", fontsize=px(size or T.label), fontweight="semibold",
                           color=text_color, annotation_clip=False)


def na_marker(ax, x, reason: str | None = None, *, size_px: int = 22, color: str = "#8F8F8F", reason_color: str = MUTED,
              label_lines: int = 1, label_size: int | None = None):
    """'Not applicable' at a category position: a gray padlock on the baseline (instead of a bar) and an
    optional gray reason under the tick label ("weights not released"). Set label_lines to the number
    of lines of the category label so the reason lands below it."""
    from matplotlib.offsetbox import DrawingArea, AnnotationBbox
    from matplotlib.patches import FancyBboxPatch, Arc, Circle, Rectangle
    s_ = px(size_px)
    da = DrawingArea(s_, s_, 0, 0)
    body_h = s_ * 0.5
    da.add_artist(FancyBboxPatch((s_ * 0.1, 0), s_ * 0.8, body_h, boxstyle=f"round,pad=0,rounding_size={s_ * 0.1}",
                                 facecolor=color, edgecolor="none"))
    da.add_artist(Arc((s_ / 2, body_h), s_ * 0.5, s_ * 0.75, theta1=0, theta2=180, color=color, linewidth=px(2.4)))
    bg = plt.rcParams["axes.facecolor"]
    da.add_artist(Circle((s_ / 2, body_h * 0.6), s_ * 0.075, facecolor=bg, edgecolor="none"))
    da.add_artist(Rectangle((s_ / 2 - s_ * 0.035, body_h * 0.22), s_ * 0.07, body_h * 0.38, facecolor=bg, edgecolor="none"))
    ab = AnnotationBbox(da, (x, 0), xybox=(0, 6), xycoords=("data", "axes fraction"), boxcoords="offset points",
                        box_alignment=(0.5, 0), frameon=False, annotation_clip=False)
    ax.add_artist(ab)
    if reason:
        drop = px(8 + (label_size or T.axis) * 1.25 * label_lines + 4)
        ax.annotate(reason, xy=(x, 0), xycoords=("data", "axes fraction"), xytext=(0, -drop),
                    textcoords="offset points", ha="center", va="top", fontsize=px(T.sublabel), color=reason_color,
                    annotation_clip=False, linespacing=1.1)
    return ab


def leader(ax, xy, text: str, xytext_px: tuple[int, int], *, color=MUTED, size: int | None = None, ha="left"):
    """Small annotation with a thin gray elbow leader line to a point (for coincident starts etc.)."""
    return ax.annotate(text, xy=xy, xytext=(px(xytext_px[0]), px(xytext_px[1])), textcoords="offset points", ha=ha,
                       va="center", fontsize=px(size or T.sublabel), color=color, annotation_clip=False,
                       arrowprops=dict(arrowstyle="-", color=BASELINE, linewidth=1, shrinkA=0, shrinkB=3,
                                       connectionstyle="angle,angleA=0,angleB=90"))


def legend(ax, loc: str = "best", colored_text: bool = True, **kw):
    """Frameless legend (use only when direct labels won't fit). colored_text=True colours each label like
    its handle; False keeps INK text with coloured handles (the matplotlib-native cream family)."""
    leg = ax.legend(loc=loc, frameon=False, **kw)
    if colored_text:
        for t, h in zip(leg.get_texts(), leg.legend_handles):
            try:
                t.set_color(h.get_color() if hasattr(h, "get_color") else h.get_facecolor())
            except Exception:
                pass
    return leg


# --------------------------------------------------------------------------------------
# Export
# --------------------------------------------------------------------------------------

def save(fig, stem, *, scale: int = 2, webp: bool = True, svg: bool = False, also_3x: bool = False,
         tight: bool = False, close: bool = True, margin_frac: float = 0.035) -> list[str]:
    """Run fit() and export `stem.png` at `scale` × the designed CSS size (+ `.webp`, optional `.svg`,
    optional `@3x.png`). The PNG is exactly the designed canvas (3.5 % margins); tight=True crops to the
    artists instead."""
    stem = re.sub(r"\.(png|webp|svg)$", "", str(stem))
    pathlib.Path(stem).parent.mkdir(parents=True, exist_ok=True)
    fit(fig, margin_frac=margin_frac)
    kw = dict(bbox_inches="tight", pad_inches=12 / LAYOUT_DPI) if tight else dict(bbox_inches=None, pad_inches=0)
    out = []
    png = f"{stem}.png"
    fig.savefig(png, dpi=LAYOUT_DPI * scale, facecolor=fig.get_facecolor(), **kw)
    out.append(png)
    if also_3x:
        fig.savefig(f"{stem}@3x.png", dpi=LAYOUT_DPI * 3, facecolor=fig.get_facecolor(), **kw)
        out.append(f"{stem}@3x.png")
    if svg:
        fig.savefig(f"{stem}.svg", facecolor=fig.get_facecolor(), **kw)
        out.append(f"{stem}.svg")
    if webp:
        try:
            from PIL import Image
            Image.open(png).save(f"{stem}.webp", quality=90, method=6)
            out.append(f"{stem}.webp")
        except Exception as e:  # pragma: no cover
            print(f"blogfig: webp skipped ({e})", file=sys.stderr)
    if close:
        plt.close(fig)
    return out


__all__ = [n for n in dir() if not n.startswith("_")]
