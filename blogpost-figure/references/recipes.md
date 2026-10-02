# Recipes

One recipe per row of the question → form table in SKILL.md. Full, runnable code for every recipe is
in `scripts/demo.py` (`uv run --with matplotlib --with numpy python scripts/demo.py OUT_DIR [recipe]`);
render it and look at the PNG before adapting. Snippets below show the shape and the pitfalls.

Common prologue:

```python
import sys; sys.path.insert(0, "/ABS/PATH/blogpost-figure/scripts")
import numpy as np, blogfig as bf
bf.use_style()                          # theme="cream" for the warm in-page variant; scale=1.2 for phones
fig, ax = bf.figure(width=W, height=H)  # CSS px at 1x; nrows/ncols for panels
...                                     # plot with the helpers
bf.headline(fig, TITLE_SENTENCE, GRAY_SUBTITLE)
bf.footnote(fig, "Whiskers: 95% intervals. n = …")   # optional
bf.save(fig, "/ABS/OUT/name")           # fit() + name.png (2x) + name.webp, exact canvas size
```

Order: plot → `headline`/`footnote` → `save` (which calls `fit`: axes between title and footnote,
one shared left margin, figure grows if text leaves < 30 % height for the plot). Use absolute output
paths; the harness may reset the working directory between calls.

Height budget at 1x: 2-line title ≈ 70 px, subtitle ≈ 22 px/line, footnote ≈ 18 px/line, legend row
≈ 30 px; the plot should keep ≥ 55 % of the height. A 2-line title + 2-line subtitle + footnote wants
≥ 560 px for an 800 px-wide chart.

## Grouped bars — treatment vs baseline (`grouped_bars`)

```python
x = np.arange(len(cats)); w = 0.36
bf.bars(ax, x - w/2, baseline, colors=[bf.BLUE],   width=w, errors=base_err)
bf.bars(ax, x + w/2, treated,  colors=[bf.ACCENT], width=w, errors=treat_err)
bf.category_labels(ax, x, cats, qualifiers)          # qualifiers: None where there is nothing to add
bf.tidy(ax, ypct=True); ax.set_yticks([0, 25, 50, 75, 100])   # units in ticks, no duplicate y title
bf.inline_legend(ax, [("Baseline", bf.BLUE, "square"), ("With method", bf.ACCENT, "square")], y=1.06)
```
Pitfalls: ≥ 90 px per category at 1x (two-tier or 14 px labels) or they collide; `errors` as a (2, n)
array for asymmetric CIs; value labels land above the whisker automatically; `bars(..., cap=2)` for
dense bars.

## Launch chart — new vs previous generation vs competitor (`launch_bars`)

```python
x = np.arange(3); w = 0.26                             # order: previous, new, competitor
bf.bars(ax, x - w, prev, colors=[bf.ACCENT_TINT], label_colors=[bf.ACCENT_MID], width=w, errors=ci_prev)
bf.bars(ax, x,     new,  colors=[bf.ACCENT], width=w, errors=ci_new)
bf.bars(ax, x + w, comp, colors=[bf.BLUE],   width=w, errors=ci_comp)
bf.reference_line(ax, 50, "50% =\nparity")             # label sits outside the plot on the right
bf.inline_legend(ax, [("Nova-1", bf.ACCENT_TINT, "square", bf.ACCENT_MID), ("Nova-2", bf.ACCENT, "square"),
                      ("Rho-4", bf.BLUE, "square"), ("95% CI", bf.WHISKER, "whisker")], y=1.06)
```
Pitfalls: the previous generation is the hero *tint*, with text in `ACCENT_MID` (4-tuple legend
entries set the text color separately from the swatch); when the new model does not win a suite, the
title says "matches" and the footnote names the overlap; put parity/chance in the footnote if the
right gutter is needed for something else.

## Lollipop with summary row (`lollipop`)

```python
bf.lollipop(ax, names, hours, sublabels=models, fmt="{:.1f} h", xunit=" h",
            summary=(mean, lo, hi, f"{mean:.1f} h on average", f"95% CI {lo:.1f} to {hi:.1f} h"),
            summary_label="Mean across the seven failures", summary_sub="with 95% confidence interval")
ax.set_xticks([0, 5, 10, 15]); ax.set_xlabel("Hours from … until …")
# percentages: fmt="{:.0f}%", xunit="%"; caveated rows: color=[...] / hollow=[...] per item
```
Pitfalls: pass items already sorted (top row first); rows with a `None` sublabel get a single centred
label; the x-range extends automatically so value texts stay inside; keep `summary_label` short (the
left gutter is as wide as the longest label); height ≈ 45 px per row (60 with sublabels) + 90 px.

## Step/survival curves with a right-hand label column (`step_curves`)

```python
for name, x, y, col in series:
    bf.step_curve(ax, x, y, color=col, hero=(name == ours))   # end dot included, not clipped
    items.append((y[-1], f"{y[-1]:g}%", name, col))
bf.log_axis(ax, "x", ticks=[1e4, 3e4, 1e5, 3e5, 1e6, 2e6]); ax.set_xlim(1e4, 2e6)
bf.tidy(ax, xlabel="Output-token budget per attempt (log scale)", ypct=True)
bf.right_labels(ax, items)                             # value column + name column, de-overlapped after fit()
fig.subplots_adjust(right=0.60)                        # reserve the gutter
```
Pitfalls: call `right_labels` after `set_xlim` (its x anchor is the right limit); zero-valued series
still get a dot and a "0%" row — stagger their end x so the dots do not stack; steps are for event
counts/survival data, not for metrics sampled at a few budgets (next recipe).

## Metric vs budget curves with a gap band (`curves`)

```python
bf.gap_band(ax, k, ours, best_other, "+10 pts", at="end")      # hero-tint band + delta label
for name, y, col, hero in runs:
    bf.curve(ax, k, y, color=col, hero=hero)                   # straight segments, dot per measured point
    items.append((y[-1], f"{y[-1]}%", name, col))
bf.log_axis(ax, "x", ticks=list(k)); ax.set_xlim(k[0], k[-1])  # small ints print as 1, 2, 4 …
bf.tidy(ax, xlabel="k, samples per problem (log scale)", ypct=True)
bf.right_labels(ax, items); fig.subplots_adjust(right=0.68)
```
Pitfalls: explain the band in the footnote; the hero is a step heavier (`hero=True`); context series in
gray, but a series that runs near zero needs `MUTED` (not `MUTED_LIGHT`) or it merges with the baseline;
disclose n for the test set.

## Time-to-k-th-event lines with terminal X (`time_to_k`, cream)

```python
bf.use_style(theme="cream")
ax.plot(times, np.arange(1, n+1), marker="o", color=col, label=name, linewidth=2.2, markersize=bf.px(9), markeredgewidth=0)
bf.terminal_marker(ax, times[-1], n, bf.fmt_duration(stop), color=col)
bf.duration_axis(ax, "x"); bf.tidy(ax, xlabel="Time from launch", ylabel="N-th exploit reproduced", left_spine=True, ymin0=False)
bf.leader(ax, (x0, 1), "59m", (26, 112), color=col)    # disambiguate coincident starts
bf.legend(ax, loc="upper right", colored_text=False)    # this family: INK text, colored handles
bf.headline(fig, title, accent_bar=False, color=bf.ACCENT_BRIGHT, size=bf.T.section, weight="normal", ha="center")
```
Pitfalls: this is the matplotlib-native family — centred regular terracotta title, no subtitle, no
accent bar; label every stop with its time so short lines are not read as fast.

## Solid vs hollow bars with group headers (`hollow_bars`)

```python
bf.bars(ax, xs, vals, colors=cols, hollow=[False, True, ...], width=0.62, errors=err, cap=2,
        label_colors=[... darker tone for tint bars ...])
bf.category_labels(ax, centers, names, ["as released", "abliterated", ...], sub_x=bar_xs)   # one gray word under each bar
bf.tidy(ax, ypct=True); ax.set_yticks([50, 100]); ax.set_ylim(0, 118)   # ~15 % headroom for the headers
bf.group_header(ax, x0, x1, "Claude models (safeguards disabled)", y=1.0)
```
Pitfalls: explain hollow vs solid in the subtitle, not a legend; one hue per family and a ramp for
generations; pale tint bars take a darker label color; the header rule sits just above the tallest
value label.

## Stacked sections (`stacked_sections`)

```python
fig, (top, bot) = bf.figure(width=760, height=960, nrows=2, gridspec_kw=dict(height_ratios=[1, 1], hspace=1.15))
...                                                     # bars / category_labels / tidy / group_header per axes
bf.section_header(top, "Refusal rate on harmful requests", "Share of harmful requests refused — higher is safer")
bf.section_header(bot, "Capability (GPQA-Diamond)", "Accuracy — higher is better")
for a in (top, bot): a.set_xlim(-0.6, 7.8)              # same x positions and range → columns line up across sections
bf.headline(fig, title, subtitle, accent_bar=False, weight="medium")   # the plain family for stacks
bf.footnote(fig, "Whiskers: 95% intervals. n = …")
```
Section headers are anchored to their axes (title ~96 px above the axes top, gray line under it), so
`fit()` reserves the room; group headers at `y=1.0` sit underneath. Budget ~100 px above each axes and
~60 px below (name + sublabel); `hspace` ≈ that gap divided by the axes height. Aspect ≈ 0.8.

## Panel row with shared legend (`panel_row`)

```python
import textwrap
fig, axes = bf.figure(width=1100, height=580, ncols=3)
for ax, (title, sub, vals, err, fmt) in zip(axes, panels):
    bf.bars(ax, x, vals, colors=cols, width=0.72, errors=err, fmt=fmt, label_colors=[bf.INK]*n, label_size=14)
    bf.category_labels(ax, x, [textwrap.fill(m, 7) for m in models], size=12)
    bf.tidy(ax, ypct=fmt.endswith("%"), ymax_pad=0.15)
    bf.panel_title(ax, title, sub=sub, wrap=30)         # accent "metric — higher is better"
fig.subplots_adjust(wspace=0.45)
bf.headline(fig, title, subtitle)                        # headline FIRST, then the shared legend …
bf.inline_legend(fig, [(m, c, "square") for m, c in zip(models, cols)] + [("95% CI", bf.WHISKER, "whisker")],
                 y=None, fig_coords=True, align="center")  # … y=None puts it under the subtitle; fit() keeps panels below
```
Pitfalls: keep the canvas ≤ 2:1 (1×N rows may go to 1100 px wide); wrap names to two lines, never
rotate; ≈ 60 px per category is the minimum with single wrapped 12 px labels; when color means "model"
across panels the value labels may be INK (as in the original), otherwise series-colored.

## 2×2 grid with panel letters (`panel_grid`)

```python
fig, axes = bf.figure(width=960, height=980, nrows=2, ncols=2)
...                                                     # plot each panel
bf.panel_title(ax, "Claim sentence for this panel", letter="a", pad=30)   # same pad for panels in a row
fig.subplots_adjust(wspace=0.5, hspace=0.75, left=0.1, right=0.97)
bf.headline(fig, "Overall claim for the whole figure")
```
Panel a (progress-over-iterations): gray dots for proposals, gray × for rejected, best-so-far over the
*accepted* proposals as an `ACCENT` step, a bigger dot + `value_label` at the end. Panel b (lines with
CI): `ax.errorbar(..., fmt="none", ecolor=line.get_color())` then `eb[2][0].set_linestyle((0, (4, 3)))`
for dashed series-colored whiskers; `label_line(ax, line, text, where="mid", dy=±)` instead of a legend.

## Zeros and not-applicable (`na_bars`)

```python
ramp = bf.ramp(bf.CRIMSON_RAMP, 4)
bf.bars(ax, x, vals, colors=ramp, width=0.62, label_colors=[ramp[1], ramp[1], ramp[2], ramp[3]])  # palest step → darker text
bf.na_marker(ax, x_na, "weights not\nreleased", label_lines=1)   # padlock on the baseline + gray reason
bf.group_header(ax, x0, x1, "GLM-5.3\nopen weights", y=1.0)
ax.set_yticks([]); ax.grid(False)                        # values are on the bars; no axis needed
```
Pitfalls: `bars` draws a 3 px strip for a zero so the "0%" label has an anchor; tell `na_marker` how
many lines the category label has so the reason lands below it.

## HTML figures

Copy a template from `assets/` next to your work and edit the content. Keep the `figure.css` and
`measure.js` tags as they are: `render_html.py` points them at the skill's copies when they are not
beside the HTML, and `measure.js` reports the content height after fonts load. Then

```sh
uv run /ABS/PATH/blogpost-figure/scripts/render_html.py my.html /ABS/OUT/my.png --width 1000   # 1500 for dashboards
```

- `flow-diagram.html`: `.node.tint-accent/.tint-blue/.tint-gray/.outline`, `.arrow--accent/--gray`
  SVG connectors (`.arrow--labelled` for a captioned arrow), `.dashed-group` + caption, and connectors
  drawn by the inline script: `.loop[data-loop-from][data-loop-to]` (return loop under the row) and
  `.up-arrow[data-from][data-to]` (to a floating node). To wrap two nodes in a dashed group give it
  `flex: 2 1 0` and put the arrow between them inside the group.
- `heatmap-table.html`: `.heatmap` grid; `.cell` + ramp class, `.cell--zero`, `.cell--light` for the
  palest step, `.cell--na` with the padlock SVG and `grid-row: span N` to merge rows, `.cell__split`.
- `quote-card.html`: `.transcript` with `.chip`, `.transcript__speaker`, `.elide`.
- `card-dashboard.html`: `.fig--cream`, serif headline with `<em>`, `.grid-4` of `.card`, `.minibar`
  with `.minibar__rect--zero`, `.quote--bubble`; render at `--width 1500`.

Pitfalls: Chrome (or Playwright) must be available; fonts come from `<skill>/fonts` via `@font-face`
(run `fetch_fonts.py` once); a page without `measure.js` falls back to a tall window cropped to content.
