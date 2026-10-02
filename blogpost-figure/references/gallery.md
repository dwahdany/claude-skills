# Gallery: the reference figures and what to copy from each

Thirteen figures from research blog posts (local copies were in `examplesw/` when this skill was
written). Each entry: the question the figure answers, the form chosen, and the details worth
copying. Dimensions are the published raster size; most are 2x exports of a 640–1000 px column.

## Charts

**AAR 2×2 grid** (fig1.png, 1440×1507). *Does automated alignment research reduce deception, and does
it generalize?* Headline sentence with a terracotta accent bar; four panels with lowercase accent
letters a–d, each panel header its own claim. (a) progress-over-iterations: gray dots = proposals, gray
× = rejected, terracotta best-so-far step with a big "82%" at the end, inline legend row above the
axes. (b) two lines with dashed series-colored whiskers, labelled *on the lines*. (c) grouped bars
blue vs terracotta, values above whiskers, two-tier x labels ("Gemma-2-2B" / gray "the model the
method was developed on"). (d) two bars with asymmetric whiskers. Y-axis has no spine, 5 gridlines,
ticks off. → `demo.py panel_grid`.

**Lollipop with summary row** (fig7.png, 1999×1169). *How long until the automated researchers beat
the best human idea, per failure?* Seven rows sorted by value, pale stems, terracotta dots, value
"2.8 h" right of each dot, two-tier row labels (failure / gray model), three light vertical gridlines,
a hairline rule, then a black diamond with CI bar and "6.4 h on average" + gray "95% CI 1.9 to 10.9 h".
†/‡ on labels resolved in gray footnotes. → `demo.py lollipop`.

**Step curves with right-hand labels** (ab295…, 1280×1588). *Which open-weight model shows real
exploitation capability?* Two stacked sections (ExploitBench, internal benchmark), each a section header
+ gray provenance line ("Public benchmark. Share of…"). Survival-style step curves on a log-x budget
axis (10k…2M), end dots, and a right column "14%  Claude Mythos Preview" sorted by final value,
colored per series, 0% entries stacked at the bottom. Gray safety caveat under the title. → `demo.py step_curves`.

**Solid vs hollow bars** (d4d48…, 1280×1531). *Does abliteration remove refusals while keeping
capability?* Two sections; group headers with a hairline spanning the group ("Claude models (safeguards
disabled)" / "Open-weight models"); Claude generations as a blue lightness ramp; GLM as green; hollow
bars (outline only) for the abliterated variant, explained in the gray subtitle, not a legend. Only
50%/100% gridlines. Footnote "Whiskers: approximate 95% intervals." → `demo.py hollow_bars`.

**Zero slivers and padlocks** (a1b61…, 1280×1576). *Can the model build exploits, and are its
safeguards bypassable?* Top: bars per model colored by vendor family with release dates as gray
sublabels; 0% drawn as a thin colored strip with a "0%" label. Bottom: escalating bypass conditions as
a crimson ramp; impossible conditions shown as a gray padlock on the baseline with a two-line gray
reason ("prefill not offered"). → `demo.py na_bars`.

**Three-panel bar row** (b6e05…, 2823×1198; matplotlib-made). *Which model flies drones best on
three tasks?* One legend row across the top with colored squares and a "| 95% CI" entry; per-panel
dark title + terracotta subtitle "Strike rate — higher is better"; bars colored per model; values above
whiskers. Weak points to avoid: centered title, rotated tick labels, 2.4:1 aspect. → `demo.py panel_row`.

**Time-to-k-th-event lines** (db12e…, 225433…, 1999×1186; matplotlib-made, cream background).
*How fast did each model reproduce exploits, and when did it stop?* Terracotta hero line with dots,
blue ramp for older generations, purple for another family; a large × at each run's end labelled
"11.8h"; frameless legend in the empty corner; coincident starts disambiguated with thin leader lines
("62m", "59m"). Tick labels "3h", "6h". → `demo.py time_to_k`.

## Non-chart figures (HTML route)

**Flow diagram** (fig2.png, 1999×1125). Headline + accent bar; a left column of outlined input boxes
with gray arrows; the main loop as tinted rounded boxes (pale terracotta = the agent, pale blue =
monitor/evaluator, warm gray = infrastructure) joined by terracotta arrows; a dashed blue frame around
the evaluator with its caption outside ("Isolated: held-out data stays hidden"); a return arrow
labelled "Next iteration, in a fresh session"; one gray footnote line. → `assets/flow-diagram.html`.

**Heatmap table** (a8b70…, 1280×1257). Grid of cells with white gutters; column headers colored by
condition with a gray parenthetical; uppercase gray row-group labels; 0% cells light gray with dark
text; crimson ramp cells with white bold values; a cell split by a hairline for a caveat ("0% / 4% with
safeguards disabled"); N/A cells merged across rows with a padlock and "Not applicable — reason".
→ `assets/heatmap-table.html`.

**Quote card** (273d6…, 1444×906). White card, hairline border, header with a gray "Reasoning" chip
and the model name in green bold, body with a thick light-gray left rule, gray "[...]" elisions.
→ `assets/quote-card.html`.

**Card dashboard** (Screenshot …16-41-05, 3360×2168, cream page). Serif italic headline, four white
cards each with a bold title, gray qualifier, a two-bar mini chart (gray baseline vs terracotta, values
in bar color, baseline only) and a pale-peach quote bubble in serif with bold emphasis; a second wide
card for the null results. → `assets/card-dashboard.html`.

**Numbered timeline** (Screenshot …16-41-18, 2200×2190). Serif headline with a terracotta serif
variant label and gray caveat; four top cards with uppercase letter-spaced container labels, numbered
accent circles and gray "TURNS 151 → 157" stamps; dashed accent arrows with small icons between them; a
two-column list of step cards below, each with a "MODEL THINKING · TURN 130" micro-label and a pale
quote block. Build from `.card`, `.step`, `.spine`, `.caps-label`, `.quote` in `assets/figure.css`.

## What they never do

Centered suptitles, framed legends, default color cycles, vertical+horizontal grids, tick marks,
full axes boxes, rotated labels (one exception), rainbow colormaps, black value labels on colored bars,
unexplained whiskers, missing zeros, blank N/A, titles that name the variable instead of the finding.
