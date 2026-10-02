# Design rules, in full

Consolidated from a lens-by-lens analysis of the 13 reference figures (see `gallery.md`). SKILL.md
has the short version; come here when a case is not covered by a recipe. Measurements are given
relative to figure width W (the published pixel width) or in CSS px at 1x on a ~900 px canvas.

Contents: 1 Typography · 2 Color · 3 Axes and marks · 4 Labels and legends · 5 Uncertainty and
honesty · 6 Composition and sizing · 7 Diagrams, cards and tables · 8 Matplotlib implementation notes

## 1 Typography

- **Title is the finding.** A sentence with a verb, sentence case, no terminal period, no "Figure 1:".
  Hard-wrapped to ≤ 2 lines of 40–60 characters at a clause boundary. Cap height ≈ 1.65–2.3 % of W
  (font ≈ 2.6 % of W, clamped 20–28 px: 26 px at 1000 px). Bold or semibold; the only bold element besides optional section headers,
  summary rows and value labels. A pure topic label ("Engagement with harmful orders, by model and
  condition") is acceptable only for tables and explanatory diagrams.
- **Accent bar.** 44 px × 5 px terracotta bar flush-left above the title, ~one cap height above it.
  Two title families: *editorial* (bold + bar; fig1/fig2/fig7, the skill default) and *plain* (medium
  weight, no bar; the stacked/sectioned charts ab295, d4d48, a1b61 and the table a8b70). The cream
  matplotlib-native variant (db12e, 225433, b6e05) centres a regular-weight terracotta title with no bar
  and no subtitle: `headline(..., accent_bar=False, color=ACCENT_BRIGHT, weight="normal", ha="center")`.
- **Subtitle.** Gray, regular, ~0.6–0.75 × title size, directly under the title, left-aligned to it.
  Carries: the measure, the benchmark and its provenance ("Public benchmark."), n, the encoding
  ("Solid bars: model. Hollow bars: abliterated."), the safety caveat.
- **Hierarchy by size and gray, not by weight.** Section header (stacked figures) 0.75–0.85 × title,
  near-black, medium; its gray method line 0.6 ×. Panel header 0.65–0.7 × title, semibold, with a
  lowercase accent letter hanging to its left. Axis labels and ticks 0.5–0.6 ×; value labels 0.55–0.9 ×
  and always bigger than ticks; footnotes 0.45–0.55 ×. Smallest text ≥ 12 px at 1x.
- **Color in text binds it to data.** Value labels and direct series labels take their series color.
  Accent also colors the bar, panel letters and (optionally) the per-panel direction subtitle. Titles
  and category names stay near-black (`#1F1F1E`). Everything secondary is gray (`#8A8A86`/`#73726C`).
- **Case.** Sentence case everywhere. Uppercase only for letter-spaced micro-labels (TASK SANDBOX,
  MODEL THINKING · TURN 130) and gray row-group labels in tables.
- **Fonts.** A wide, low-contrast geometric grotesque (the originals resemble Styrene). Free
  stand-ins in order: DM Sans, Figtree, Inter, IBM Plex Sans; system fallback Helvetica Neue/Arial.
  Serif (Tiempos-like → Source Serif 4, Newsreader) only for editorial headlines and quoted prose in
  HTML figures, never for axis text. Never DejaVu Sans.
- **Leading.** Title ~1.15, body ~1.25–1.35. Never justify. Title block ≤ 75–80 % of W.
- **Two-tier labels.** Dark primary line + gray secondary line for categories (model / size or date or
  condition), summary rows (bold value / gray CI), and node titles (bold / regular body).

## 2 Color

- **One hero hue.** Terracotta `#B86046` (on white) or `#D97757` (on cream, brand) for the series the
  title is about. Baseline/"before" is steel blue `#40668C`. Context (proposals, rejected points,
  other labs' older models, 0 % series) is gray, never another hue. ≤ 3 hues unless family-coded.
- **Family coding for many systems.** One hue per vendor/group (Claude blues, GLM greens, Kimi ochre,
  DeepSeek purple, newest/own model terracotta) and a lightness ramp within a family for
  generations (lightest = oldest): `#70B0DC → #3788C0 → #08529D`; cream variant
  `#A7C7E0 → #5C9FE3 → #1B68B2 → #083262`.
- **Ordinal conditions = single-hue ramp**, 3–4 steps, mildest lightest: crimson
  `#EABBB1 → #BC5F67 → #992031 → #8E1025`. Never a rainbow or diverging colormap, never a colorbar;
  print the values in the cells instead.
- **Binary variant = fill style**, not hue: hollow bar (background fill, 2 px edge in the series
  color, same width) for a transformed version of the same entity.
- **Hues are dusty, never pure**: terracotta not orange, steel not royal blue, forest not lime.
- **Gray data near the baseline**: a context series drawn in `MUTED_LIGHT` that runs at 0–5 % looks like a
  misaligned second baseline; use `MUTED` for it (the baseline stays `#AFAFAB`).
- **Grays in tiers**: `INK #1F1F1E` titles and category labels; `INK_SOFT #5A5A57` axis titles and
  group headers; `MUTED #8A8A86` for all secondary text (subtitles, ticks, sublabels, footnotes — the
  references vary between `#73726C` and `#949491`); `MUTED_LIGHT #AAAAA7` for de-emphasized marks.
  Gridlines `#EAE9E5`; baseline a step darker (`#AFAFAB`); whiskers near-black `#2B2B2A`.
- **Backgrounds**: white default; cream `#FAF9F5` for in-page/editorial figures and the cream
  matplotlib variant (figure *and* axes face). Card/cell fill `#F1F0EC`. No gradients, no shadows, no
  alpha blending: de-emphasize with a lighter gray, not transparency.
- **Colorblind check**: every same-axis pair should differ in CIELab L* by ≥ 15 or carry a redundant
  channel (marker shape, hollow/solid, direct label, position). Terracotta vs steel blue passes;
  avoid blue vs purple or green vs terracotta without a lightness gap.
- **Line weights**: hero ~2.5 pt / 3.4 px, others ~1.8 pt; filled markers in the series color, no
  marker edge; X for terminal events, diamond for treatment vs circle baseline; summary rows black.

## 3 Axes and marks

- No top/right spines ever; left spine off by default (y values hang off the gridlines); the bottom
  baseline is the one line, slightly darker than the grid. Tick marks length 0.
- Gridlines in one direction only (horizontal for vertical bars and lines, vertical for horizontal
  lollipops), solid, ≥ 90 % lightness, beneath the marks, 2–5 lines (often just 50 %/100 %).
- Units live in tick labels: "50%", "5 h", "0m / 1h / 3h", "10k / 300k / 1M". When ticks and the
  subtitle already say what is measured, drop the axis title. Log axes: 1–3 pattern (10k, 30k, 100k…),
  "(log scale)" in the axis label, never 10^n. Score axes may start at the scale minimum and state the
  direction ("1–10, lower is safer"); bar axes always start at zero.
- Bars: standalone ~0.6 of the slot, grouped 0.9 within the group with ≥ 1 bar of air between groups;
  ≥ ~90 px per category at 1x; ~8 categories per row max. Zero = a 3 px colored strip on the baseline
  plus "0%". Lollipops: dot ≈ 1.3 % W, stem ≈ 0.4 % W in a 35 % tint of the dot color.
- Error bars: thin (~1.2–1.4 pt), near-black, cap-less by default (small caps when bars are dense, as
  in d4d48/a1b61 — consistent within one figure), drawn above the fill; on line charts, series-colored
  and dashed. Value labels sit above the whisker, semibold, ~1.3 × tick size.
- Step curves use `where="post"`; best-so-far lines are steps; time-to-k lines are straight segments
  with a dot per event and a large X where the run stopped.
- Extend the x-range a little past the data so end labels and the right label column have room.

## 4 Labels and legends

- Default: no legend. Label lines at their end or alongside their midpoint in their own color
  (above the upper line, below the lower). For ≤ ~7 curves use a right-hand column "VALUE  Name"
  aligned to each curve's end, sorted by final value, nudged apart ≥ 1.3 line heights, zero-valued
  series stacked at the bottom.
- Every bar and every endpoint carries its value in its series color, 1.2–1.5 × tick size, centered
  above the whisker. Format: integer % (one decimal only below 1 %), "2.8 h", "59m"/"1.8h", scores to
  two decimals; CI bounds at the estimate's precision.
- When a legend is unavoidable: frameless, inline row of colored text with small square/line swatches
  above the plot (left-aligned for one chart, centered for a panel row), including a "| 95% CI"
  whisker entry when whiskers are shown. Never a framed box, never `bbox_to_anchor` to the right.
- Group headers: dark text on a hairline that spans exactly the group's bars, above the value labels
  (leave ~15–20 % headroom in ylim). Two lines when a condition must be named ("Claude Opus 5" / gray
  "as deployed, with API safeguards").
- Encodings a legend cannot express go into the gray subtitle sentence ("Solid bars: model. Hollow
  bars: abliterated.").
- Direction of goodness: accent subtitle per panel ("Strike rate — higher is better") or in the axis
  label parenthetical; never in the title.
- Reference levels (parity 50 %, chance, a target): dashed in the baseline gray, labelled small and
  gray just outside the plot (or in the footnote), never as a colored series.
- To emphasise a difference between two series, fill the band between them in the hero tint and print
  the delta at its widest point or at the end; explain the band in the footnote.
- Leader lines only on collision: hairline gray, no arrowhead, label in the series color.
- N/A: gray padlock on the baseline + gray reason under the tick; †/‡ appended to labels, resolved
  bottom-left in gray.

## 5 Uncertainty and honesty

- Whiskers drawn ⇒ interval named in the image: subtitle suffix "; whiskers: 95% intervals",
  footnote "Whiskers: approximate 95% intervals.", legend "| 95% CI", or a summary row "95% CI 1.9 to
  10.9 h". Say "approximate" when the method is.
- n or the denominator appears in the image: subtitle ("198 questions × 4 samples", "50 simulated
  episodes per bar"), axis label ("% of 12 launches") or sublabel ("average over 6 runs"). Mark reduced
  sets "(subset)".
- Figures about attacks, harm or dangerous capability carry a one-sentence gray caveat ("All
  attempts ran in isolated sandboxes…; no real system was touched.") and/or "(simulated)".
- Zero is drawn and labelled; N/A is drawn differently (padlock + reason), never as 0, blank or a gap.
- Comparisons name the condition in the group header (safeguards disabled / as deployed / open
  weights); model comparisons print release dates under the labels.
- Show the population behind a max/mean (gray proposals behind the best-so-far line); keep
  zero-scoring series on the chart; put summary rows under the raw rows they summarize.
- A truncated or stopped run is marked with an X and its stop time so short lines are not misread.
- Quoted model text has provenance (model, condition, turn), gray `[...]` elisions, and editorial
  emphasis in bold, never color.
- Benchmark provenance and the data window go in the first words of the subtitle or title
  ("Public benchmark.", "18 CVEs patched in Firefox 147 to 149").

## 6 Composition and sizing

- Design in CSS px at 1x, export at 2x (and WebP). Column figure 700–1000 px wide, aspect ≈ 1.6–1.7;
  stacked sections 640–800 px wide, aspect ≈ 0.8; 2×2 grid ≈ 1.0; never wider than 2:1 (a 2.4:1 panel
  row is illegible at column width).
- One shared left margin (3.5 % W) for accent bar, title, subtitle, section headers, footnotes and
  the y tick-label / row-label column; `fit()` enforces it and keeps the right margin equal. Panel
  gutters are larger (6–9 % horizontally). `save()` exports the exact canvas, so figure widths stay
  consistent across a post (`tight=True` crops to content instead).
- Budget ~50–60 % of the canvas to the axes; the rest is for titles, direct labels and the right
  label column (reserve 35–40 % W for it on step-curve charts).
- Layout grammar: 2×2 grid with letters for four related findings; 1×N row with one legend for the
  same metric across tasks; vertical stack of sections (header + gray spec + group headers) for
  sub-analyses sharing a theme; give each section exactly the height it needs.
- Wrap category labels to 2–3 lines; do not rotate (if unavoidable: 30°, `ha="right"`,
  `rotation_mode="anchor"`). Keep ≤ ~8 x positions per row.
- Footnotes bottom-left; per-item caveats as gray sublabels under the item.

## 7 Diagrams, cards and tables (HTML route)

- Boxes: radius ≈ 3 % of box height (8–16 px); either a flat semantic tint with no border or white
  with a 1 px hairline (`#DEDDDD`), never both; no shadows or gradients.
- Tints are semantic: pale terracotta = the agent/model-generated content; pale blue = isolated,
  monitoring, evaluation; warm gray = neutral infrastructure or zero values. Box title in the
  saturated hue, body in ink.
- Arrows: accent solid = main flow, gray = inputs/side information, dashed = conditional/attempted/
  boundary-crossing; ~2.5 px stroke; small filled triangle heads; labelled alongside in their own
  color; no arrow legend. Return loops are rounded paths with a label under the shaft.
- Dashed outlines group or flag; caption just outside, bottom-left, in the stroke color.
- Numbered steps: outlined circles (2 px accent, white fill, accent numeral), joined by a 2 px spine.
- Icons: monochrome outline glyphs colored semantically; gray padlock + caption = not applicable.
- Quote blocks: pale tint, 8 px radius (bubble: 14 px + tail), serif body, line-height 1.5, bold for
  the key clause, gray elisions. Transcript cards: chip + bold colored speaker, thick light left rule.
- Heatmap tables: CSS grid with white gutters, no cell borders; white bold values on dark cells, gray
  on neutral/zero cells; column headers colored to their hue with a gray parenthetical; gray uppercase
  row-group labels; hairline divider between groups; N/A merged across rows, lighter fill, padlock.
- Card dashboards: equal white cards with hairline, bold title + gray qualifier, a baseline-only mini
  chart with values in bar color, a quote bubble; one accent for the subject, gray for the baseline.

## 8 Matplotlib implementation notes

`scripts/blogfig.py` encodes these; when working without it:

- `rcParams`: spines top/right/left off, `axes.edgecolor` baseline gray, `axes.grid=True`,
  `axes.grid.axis="y"`, `grid.color="#EAE9E5"`, `axes.axisbelow=True`, tick sizes 0, tick colors gray,
  `legend.frameon=False`, `lines.linewidth≈2.4`, `font.family=[sans, "Inter", "DejaVu Sans"]` (a list
  gives glyph fallback for †, ‡, →, ×), `savefig.dpi = 2 × figure.dpi`.
- Titles are `fig.text(...)`, not `ax.set_title`; accent bar is a `Line2D`/`Rectangle` in figure
  coords; measure text with `get_window_extent` and rescale axes positions so everything fits
  (`blogfig.fit`). Do not rely on `bbox_inches="tight"` alone for margins.
- Value labels: `ax.annotate(fmt, (x, top_of_whisker), xytext=(0, 6), textcoords="offset points",
  ha="center", va="bottom", color=series_color)`; one `bar_label` call per series if you use it.
- Hollow bars: `ax.bar(..., facecolor=bg, edgecolor=c, linewidth=2.2)`; zero sliver:
  `ax.plot([x-w/2, x+w/2], [0, 0], color=c, lw=3)`.
- Right label column: positions in display space, greedy push-apart, convert back to data; re-run
  after any layout change (axes resize changes the mapping).
- Log ticks: `FixedLocator([1e4,3e4,1e5,3e5,1e6,2e6])` + `FuncFormatter` → 10k/30k/…; `NullLocator`
  for minors. Durations: `f"{round(h*60)}m"` below 1 h, `f"{h:.1f}h"` for annotations, `f"{h:g}h"` ticks.
- Padlock: a `DrawingArea` with a rounded rectangle and an arc in an `AnnotationBbox` anchored at
  `(x, 0)` in `("data", "axes fraction")` coords.
- Export: lay the axes out inside the canvas (vertical and horizontal fit), then
  `fig.savefig(png, dpi=200, facecolor=fig.get_facecolor())` without `bbox_inches="tight"` so the PNG is
  exactly 2 × the designed CSS size; Pillow → WebP (quality 90). SVG with `svg.fonttype="none"` if the
  page can embed it.
