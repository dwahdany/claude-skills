---
name: blogpost-figure
description: Use when the user wants a finished figure for a published web page — a chart, plot, diagram, infographic or explainer graphic, quote card, heatmap table or dashboard of cards for a blog post, announcement, newsletter, README, docs page, Substack, or a social/og:image preview — including "make a nice chart of these results for the post" and redoing a paper figure for the web. Produces the research-blog house style — the title is the takeaway sentence, a gray subtitle names the measure, every mark carries its value, series are labelled directly instead of in a legend box, one terracotta hero color against steel blue and gray, horizontal gridlines only, retina PNG + WebP — via a bundled matplotlib helper module with rendered recipes and HTML/CSS templates rendered with headless Chrome. Not for LaTeX/PDF academic paper figures (paper-figure skill), exploratory notebook plots, or interactive/live dashboards (Plotly, Streamlit, Grafana).
---

# Blog-post figures

Figures for the web are read in a scrolling column, on phones, without a caption nearby. They must
carry their own headline, explain their own encoding, and survive being screenshotted. This skill
encodes the design language of a set of strong research-blog figures (catalogued in
`references/gallery.md`) and ships code that produces it.

Two routes, chosen by content:

| Content | Route | Tooling |
|---|---|---|
| Data charts: bars, lines, step/survival curves, lollipops, scatter, multi-panel grids | matplotlib | `scripts/blogfig.py` helpers |
| Process/flow diagrams, timelines, quote/transcript cards, heatmap tables, dashboards of cards | HTML + CSS | `assets/figure.css` + templates, `scripts/render_html.py` |

The skill root is the directory containing this file (e.g. `~/.claude/skills/blogpost-figure`;
`find ~ -name blogfig.py -path '*blogpost-figure*' 2>/dev/null` if unsure). Call scripts by absolute
path. Python scripts are `uv run` scripts with inline deps; for your own figure script use
`uv run --with matplotlib --with numpy python my_fig.py` or a PEP 723 header. For LaTeX/PDF paper
figures use the `paper-figure` skill instead.

## Procedure

1. **Write the takeaway as one sentence.** That sentence is the title (≈50 characters per line at
   1000 px, two lines max). If you cannot write it, the figure is not ready, or it is two figures.
   Then write the gray subtitle: what is measured, on what, with what n or benchmark. Diagrams may
   use a mechanism sentence instead ("How X works: step, step, step").
2. **Pick the form** from the table below (question → form). Default to the simplest form that
   shows the comparison in the title.
3. **Build it** with `blogfig` (chart) or an HTML template (diagram/card/table). The house rules
   below are the point of the skill; the helpers implement most of them by default.
4. **Export at 2x** (`bf.save` → `name.png` + `name.webp`), then **open the PNG with the Read tool
   and look at it.** Fix overlaps, clipped labels, three-line titles, labels not in their series
   color. Iterate until the checklist passes.
5. **Hand back** the PNG/WebP paths, the title sentence (it is the alt text) and the embed snippet
   from Export. If n or the CI was not given, say so in the hand-back; never invent it.

## Question → form → helper

| Question | Form | Helper(s) / `demo.py` recipe |
|---|---|---|
| Does the treatment beat the baseline, on several conditions? | Grouped bars, baseline blue + hero terracotta, values above bars | `bars`, `category_labels`, `inline_legend` — `grouped_bars` |
| New model vs previous generation vs competitor (launch chart)? | Three bars per suite: previous = hero tint (labels in `ACCENT_MID`), new = hero, competitor = blue; parity line; honest title | `bars(label_colors=)`, `reference_line` — `launch_bars` |
| How does one quantity compare across ~5–10 named items? | Horizontal lollipop with a summary (mean + CI) row; gray/hollow dots for caveated items | `lollipop` — `lollipop` |
| How does success grow with budget/time (event counts)? | Step/survival curves (log-x if budgets), right-side value + name labels, no legend | `step_curve`, `log_axis`, `right_labels` — `step_curves` |
| Metric sampled at a few budgets or sizes (pass@k, scaling)? | Lines with a dot at every measured point, log-x, right-side labels; hero-tint gap band for the difference the post is about | `curve`, `gap_band`, `right_labels` — `curves` |
| How fast did each run progress; when did each stop? | Time-to-k-th-event lines, a large X at the stop labelled with the time | `terminal_marker`, `leader`, `duration_axis` — `time_to_k` |
| Before vs after a modification of the same entity? | Solid vs hollow bars of one color, explained in the subtitle; group headers on hairlines | `bars(hollow=)`, `group_header` — `hollow_bars` |
| Two or more sub-analyses sharing one theme (refusals *and* capability)? | Tall stacked sections: one plain headline, a section header + gray method line per axes, shared x-range, one footnote | `section_header(ax, …)`, `figure(nrows=)` — `stacked_sections` |
| Same metric on several tasks, several systems? | 1×N panel row, one centred legend row (incl. "95% CI"), per-panel accent subtitle "metric — higher is better" | `panel_title(sub=)`, `inline_legend(align="center")` — `panel_row` |
| Four related findings for one story? | 2×2 grid, accent lowercase letters a–d, each panel header its own takeaway | `panel_title(letter=)` — `panel_grid` |
| Some conditions impossible / not applicable? | Zero as a labelled sliver; N/A as a gray padlock + one-line reason, never a blank | `bars(zero_line=)`, `na_marker` — `na_bars` |
| Matrix of conditions × systems with a few numbers each? | Heatmap table: single-hue ramp cells with printed values, gray 0% cells, merged N/A cells | `assets/heatmap-table.html` |
| How does the system/process work? | Flow diagram: rounded boxes with semantic tints, colored arrows, dashed group with caption, return loop | `assets/flow-diagram.html` |
| What did the model actually say? | Quote/transcript card with provenance chip, gray `[...]` elisions, bold emphasis | `assets/quote-card.html` |
| Several small results each with a qualitative example? | Dashboard of cards: mini bar + value labels + quote bubble per card (render at `--width 1500`) | `assets/card-dashboard.html` |

`references/recipes.md` has the code for every row with its pitfalls; `scripts/demo.py` renders them
all (`uv run --with matplotlib --with numpy python scripts/demo.py OUT_DIR [recipe]`), so you can look
at a finished example before adapting it.

## House rules

**Text.** Title = takeaway sentence, sentence case, near-black, ≤ 2 lines, left-aligned on the shared
left margin. Two families: *editorial* (bold + 44 px terracotta accent bar; the default) and *plain*
(`headline(..., accent_bar=False, weight="medium")`; stacked/sectioned charts). The cream
matplotlib-native variant centres a regular-weight terracotta title with no bar
(`accent_bar=False, color=ACCENT_BRIGHT, weight="normal", ha="center"`). Gray subtitle under it names measure, benchmark, n and
encodings ("Solid bars: model. Hollow bars: abliterated."). Panel headers are semibold takeaways with an
accent lowercase letter; section headers are medium with a gray method line. Footnotes bottom-left,
gray, tied to items with †/‡. No "Figure 1:", no Title Case, no captions outside the image.

**Axes.** No top/right/left spines; a slightly darker bottom baseline; horizontal gridlines only
(vertical only for horizontal charts), 2–5 of them; tick marks off; gray tick labels with the unit
baked in ("50%", "5 h", "300k"); bars start at zero; log axes 10k/100k/1M, never 10^5. Drop the axis
title when ticks + subtitle already say what is measured.

**Labels, not legends.** Every bar and endpoint has a value label in its series color, above the
whisker, larger than the tick labels (pale bars get a darker text tone). Lines are labelled at their end
or alongside; several curves get a right-hand column "14%  Name" sorted by final value. A legend, when
unavoidable, is a frameless inline row of colored text with small swatches. Category labels are
two-tier only when the qualifier adds information (size, date, condition), not to repeat the subtitle.
Reference levels (parity, chance) are dashed with a small gray label outside the plot or in the footnote.

**Color.** One hero hue (terracotta `ACCENT`) for the series the title is about; steel `BLUE` for the
baseline; gray for context. ≤ 3 hues per chart; for many systems one hue family per vendor/group and a
lightness ramp within a family for generations or escalating conditions (`BLUE_RAMP`, `CRIMSON_RAMP`).
Hollow = a transformed variant of the same entity. A gray context series that runs near zero takes `MUTED`,
not `MUTED_LIGHT`, so it does not read as a second baseline. Never the default matplotlib cycle, rainbow
colormaps, or alpha for de-emphasis.

**Uncertainty and honesty.** Whiskers thin, dark, cap-less (small caps only when dense; consistent
within a figure) and explained in the image: subtitle "whiskers: 95% intervals", footnote, or a "95% CI"
legend entry. State direction for scores ("1–10, lower is safer"; "Strike rate — higher is better").
Disclose n. Figures about attacks or harm carry a gray "(simulated)/sandboxed" caveat. Zero is drawn
and labelled; N/A gets a padlock and a reason; truncated runs get an X and the stop time. When the hero
does not win a cell, the title says so.

**Size.** Design in CSS px at 1x: 700–1000 px wide for a column figure (aspect ≈ 1.6), 640–800 px
wide and taller for stacks (≈ 0.8), ≈ 1.0 for a 2×2 grid, never wider than 2:1. Budget height for text:
a 2-line title ≈ 70 px, each subtitle line ≈ 22 px, each footnote line ≈ 18 px; lollipops need ~45 px per
row (60 with sublabels) plus 90 px for a summary row; bars need ≥ 90 px per category with two-tier or
14 px labels (≈ 60 px with single wrapped 12 px labels in panel rows, which may go to 1100 px wide);
stacked sections need ~100 px above each axes for the section header and ~60 px below for labels. Smallest text
≥ 12 px at 1x; for phone-first figures use `use_style(scale=1.2)` and ≤ 720 px width. `save()` exports
the exact canvas with 3.5 % margins, so widths stay consistent across a post.

## Palette

`ACCENT #B86046` hero (`ACCENT_BRIGHT #D97757` on cream; tints `ACCENT_MID #C7816C`, `ACCENT_TINT
#E0BAAF`, `ACCENT_PALE #F7E9E3`) · `BLUE #40668C` baseline (`BLUE_RAMP #70B0DC→#3788C0→#08529D`) ·
`GREEN #0E6B54` / `GREEN_BRIGHT #019E73` · `VIOLET`, `PURPLE`, `OCHRE`, `SLATE` for further families ·
`CRIMSON_RAMP #EABBB1→#8E1025` for severity · `INK #1F1F1E` titles and category labels, `INK_SOFT
#5A5A57` axis titles, `MUTED #8A8A86` subtitles/ticks/footnotes, `MUTED_LIGHT #AAAAA7` de-emphasized
marks · `GRID #EAE9E5`, `BASELINE #AFAFAB`, `WHISKER #2B2B2A` · backgrounds `PAPER #FFFFFF`, `CREAM
#FAF9F5`, cards/cells `PANEL #F1F0EC`. All are constants at the top of `scripts/blogfig.py`
(`bf.SERIES` is the default order: hero, blue, green, …).

## Quickstart

```python
import sys; sys.path.insert(0, "/ABS/PATH/blogpost-figure/scripts")
import numpy as np, blogfig as bf

bf.use_style()                                     # or theme="cream", scale=1.2 for phones
fig, ax = bf.figure(width=800, height=520)         # CSS px at 1x
x = np.arange(2); w = 0.36
bf.bars(ax, x - w/2, [59, 67], colors=[bf.BLUE],   width=w, errors=[5, 5])
bf.bars(ax, x + w/2, [79, 88], colors=[bf.ACCENT], width=w, errors=[5, 4])
bf.category_labels(ax, x, ["Gemma-2-2B", "Gemma-2-9B"],
                   ["the model the method\nwas developed on", "4.5× more parameters"])
bf.tidy(ax, ypct=True); ax.set_yticks([0, 25, 50, 75, 100])
bf.inline_legend(ax, [("Untrained model", bf.BLUE, "square"), ("With the new method", bf.ACCENT, "square")], y=1.06)
bf.headline(fig, "The same method works on a model 4.5× the size",
            "Honest responses on a held-out deception benchmark; whiskers: 95% intervals")
bf.footnote(fig, "Whiskers: approximate 95% intervals. 500 prompts per bar.")
bf.save(fig, "/ABS/OUT/figures/method_generalizes")  # -> .png (2x) + .webp; runs bf.fit() first
```

`headline`/`footnote` measure their text; `save()` calls `fit()`, which lays the axes out between them,
aligns title, tick labels and footnote on one left margin, and grows the figure if the text would
leave less than 30 % of the height for the plot. If something still overlaps, give the figure more
height or shorten the text; do not shrink fonts below 12 px.

**Fonts.** `fonts/` is git-ignored: run `uv run --with matplotlib scripts/fetch_fonts.py` once per
machine. It downloads DM Sans, Inter and Source Serif 4 (OFL) into `<skill>/fonts/`, which both
`use_style()` and `assets/figure.css` read (`--user` puts them in `~/.local/share/blogfig-fonts`,
matplotlib-only). Without them the stack falls back to Helvetica Neue/Arial. `use_style(font="Inter")`
switches family.

## HTML route (diagrams, cards, tables)

Copy a template from `assets/` next to your work and edit the content. Keep its `<link
rel="stylesheet" href="figure.css">` and `<script src="measure.js">` tags: `render_html.py` rewrites
them to the skill's copies when they are not next to the file, and `measure.js` reports the page
height (after fonts load) so the screenshot is sized to the content. Then:

```sh
uv run /ABS/PATH/blogpost-figure/scripts/render_html.py my_diagram.html /ABS/OUT/my_diagram.png --width 1000
```

The page is laid out at `--width` CSS px (column figures 1000; card dashboards 1500) and exported at 2x
plus WebP. Needs Google Chrome/Chromium; without one, `uv run --with playwright python -m playwright
install chromium` and run the script with `--with playwright`.

`assets/figure.css` documents the primitives: `.fig-title` (sentence headline + accent bar; `--serif`,
`--plain` variants), `.card`, `.node` with `.tint-accent/.tint-blue/.tint-gray/.outline`, `.arrow`
(SVG; accent = main flow, gray = inputs, dashed = conditional; label inherits the arrow color),
`.dashed-group` + caption, `.step` circles and `.spine`, `.quote` / `.quote--bubble`, `.transcript`,
`.chip`, `.caps-label`, `.heatmap` grid with `.cell--zero/--na`, `.minibar`. The flow template's return
loop and up-arrow are positioned by a small script from element ids (`data-loop-from/to`). Rules carried
over from the charts: white cards with a 1 px hairline *or* a flat tint fill, never both; radius ≤ 16 px;
no shadows or gradients; captions colored by meaning; serif only for editorial headlines and quotes.

## Export and embedding

`save()` writes `name.png` at 2 × the CSS width and `name.webp`. Embed at the CSS width so the 2x image
renders sharp, and reuse the title sentence as alt text:

```html
<picture>
  <source srcset="figures/name.webp" type="image/webp">
  <img src="figures/name.png" width="800" alt="The same method works on a model 4.5× the size">
</picture>
<!-- or: <img src="figures/name.png" srcset="figures/name.png 2x" width="800" alt="…"> -->
```

Markdown that cannot set a width (`![alt](figures/name.png)`) shows the image at 2x size; prefer the
HTML snippet or export with `scale=1` for such hosts. `also_3x=True` adds `name@3x.png`; `svg=True` adds
a vector copy with live text.

## Checklist (look at the exported PNG)

- [ ] Title is a sentence stating the finding, ≤ 2 lines; gray subtitle names measure, benchmark, n
- [ ] No legend box; every series labelled in its own color; every bar/endpoint carries its value
- [ ] Only horizontal (or only vertical) light gridlines; no top/right/left spines; ticks off; units in tick labels
- [ ] Hero terracotta, baseline blue, context gray; ramps single-hue; ≤ 3 hues unless family-coded
- [ ] Whiskers thin and dark, explained in the image; direction of goodness stated for scores
- [ ] Zeros drawn and labelled; N/A padlock + reason; truncated runs marked; reference levels labelled
- [ ] Caveats (simulated, sandboxed, subset, missing n) present as gray subtitle/footnote; †/‡ resolved
- [ ] Nothing overlaps or is clipped; smallest text ≥ 12 px at 1x; exported at 2x PNG + WebP; alt text = title

## References

- `references/recipes.md` — code for each row of the form table, with the pitfalls of each. Read before building.
- `references/design-rules.md` — the full rule set with measurements (typography, color, axes, labels, uncertainty, composition, diagrams, matplotlib notes). Read when a figure type is not covered by a recipe or when working without `blogfig`.
- `references/gallery.md` — the 13 reference figures: what each answers, which form it uses, what to copy. Read when you want to see the original before adapting a form, or when the user shares a figure to match.
