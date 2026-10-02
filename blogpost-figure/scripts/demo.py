# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.8", "numpy"]
# ///
"""Render every chart recipe of the blogpost-figure skill into OUT_DIR (default ./blogfig-demo).

    uv run demo.py [OUT_DIR] [recipe ...]       # recipes: grouped_bars launch_bars lollipop step_curves curves time_to_k
                                                #          hollow_bars stacked_sections panel_row panel_grid na_bars

Each function is a self-contained example of one form from SKILL.md's question → form table.
Numbers are illustrative. Look at the PNGs before adapting a recipe to real data.
"""
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import blogfig as bf  # noqa: E402


def grouped_bars(out):
    """Treatment vs baseline on two conditions: blue baseline, terracotta hero, two-tier category labels."""
    bf.use_style()
    fig, ax = bf.figure(width=800, height=520)
    x = np.arange(2); w = 0.36
    bf.bars(ax, x - w / 2, [59, 67], colors=[bf.BLUE], width=w, errors=[5, 5])
    bf.bars(ax, x + w / 2, [79, 88], colors=[bf.ACCENT], width=w, errors=[5, 4])
    bf.category_labels(ax, x, ["Gemma-2-2B", "Gemma-2-9B"],
                       ["the model the method\nwas developed on", "4.5× more parameters"])
    bf.tidy(ax, ypct=True)
    ax.set_ylim(0, 100); ax.set_yticks([0, 25, 50, 75, 100])
    bf.inline_legend(ax, [("Untrained model", bf.BLUE, "square"), ("With the AAR-found method", bf.ACCENT, "square")], y=1.06)
    bf.headline(fig, "The same method works on a model 4.5× the size",
                "Honest responses on a held-out deception benchmark; whiskers: 95% intervals")
    bf.footnote(fig, "Whiskers: approximate 95% intervals. 500 prompts per bar.")
    return bf.save(fig, out / "grouped_bars")


def launch_bars(out):
    """Announcement chart: new model (hero) vs its previous generation (hero tint) vs a competitor (blue),
    on three suites, with a parity reference and an honest title."""
    bf.use_style()
    fig, ax = bf.figure(width=860, height=560)
    suites = ["Code", "Reasoning", "Agentic"]
    prev, new, comp = [55, 49, 41], [71, 64, 58], [62, 61, 60]
    ci = [[5, 5, 6], [5, 5, 6], [5, 5, 6]]
    x = np.arange(3); w = 0.26
    bf.bars(ax, x - w, prev, colors=[bf.ACCENT_TINT], label_colors=[bf.ACCENT_MID], width=w, errors=ci[0])
    bf.bars(ax, x, new, colors=[bf.ACCENT], width=w, errors=ci[1])
    bf.bars(ax, x + w, comp, colors=[bf.BLUE], width=w, errors=ci[2])
    bf.category_labels(ax, x, suites)
    bf.tidy(ax, ypct=True); ax.set_ylim(0, 100); ax.set_yticks([0, 25, 50, 75, 100])
    bf.reference_line(ax, 50, "50% =\nparity")
    bf.inline_legend(ax, [("Nova-1", bf.ACCENT_TINT, "square", bf.ACCENT_MID), ("Nova-2", bf.ACCENT, "square"),
                          ("Rho-4", bf.BLUE, "square"), ("95% CI", bf.WHISKER, "whisker")], y=1.06)
    bf.headline(fig, "Nova-2 beats Rho-4 on code and reasoning, and matches it on agentic tasks",
                "Win rate against the strongest baseline on each eval suite; higher is better. Whiskers: 95% intervals.")
    bf.footnote(fig, "n = 400 head-to-head comparisons per bar, judged by a panel. On Agentic, Nova-2 and Rho-4 (58% vs 60%) are within each other's intervals.")
    return bf.save(fig, out / "launch_bars")


def lollipop(out):
    """One quantity across named items, sorted, with a mean + CI summary row and dagger footnotes."""
    bf.use_style()
    fig, ax = bf.figure(width=1000, height=600)
    cats = ["Reward hacking †", "Prompt injection", "Power seeking ‡", "Social bias †", "Sycophancy", "Deception", "Jailbreaks"]
    subs = ["Qwen3.5-2B", "Qwen3.5-2B", "Llama-3.2-3B", "Olmo-3-7B", "Qwen3.5-2B", "Gemma-2-2B", "Phi-4-mini"]
    vals = [0.0, 2.8, 3.5, 6.7, 7.4, 9.7, 14.5]
    bf.lollipop(ax, cats, vals, sublabels=subs,
                summary=(6.4, 1.9, 10.9, "6.4 h on average", "95% CI 1.9 to 10.9 h"),
                summary_label="Mean across the seven failures", summary_sub="with 95% confidence interval")
    ax.set_xticks([0, 5, 10, 15]); ax.set_xlim(0, 19)
    ax.set_xlabel("Hours from the AARs' first idea until their best valid method beats the best human idea")
    bf.headline(fig, "Across seven alignment failures, the AARs pass the best human idea within hours")
    bf.footnote(fig, "† No human idea scored above zero; the time shown is when an AAR method that passed the capability check first scored above zero.\n"
                     "‡ The only human idea failed the capability check; its safety score alone is used.")
    return bf.save(fig, out / "lollipop")


def step_curves(out):
    """Share solved vs budget (log x) for several systems; right-hand value+name column instead of a legend."""
    bf.use_style()
    fig, ax = bf.figure(width=720, height=470)
    rng = np.random.default_rng(3)
    series = [("Claude Mythos Preview", 14, 1.0e5, bf.BLUE_RAMP[2]), ("GLM-5.3", 12, 1.6e5, bf.GREEN_BRIGHT),
              ("Kimi K3", 0.5, 3e5, bf.OCHRE), ("DeepSeek-V4.1-Flash", 0.2, 3e5, bf.PURPLE),
              ("Claude Opus 4.6", 0, 1e5, bf.BLUE_RAMP[0]), ("GLM-5.2", 0, 1e5, bf.SLATE)]
    items = []
    for name, final, start, col in series:
        if final > 0:
            n = max(2, int(final * 2))
            xs = np.sort(rng.uniform(np.log10(start), np.log10(7.5e5), n))
            x = np.concatenate([[1e4], 10 ** xs, [8e5]])
            y = np.concatenate([[0], np.arange(1, n + 1) * final / n, [final]])
        else:  # zero-valued series: flat line, end dots staggered so they do not stack
            x_end = {"Claude Opus 4.6": 7e5, "GLM-5.2": 9e5}.get(name, 8e5)
            x, y = np.array([1e4, x_end]), np.array([0, 0])
        bf.step_curve(ax, x, y, color=col, hero=(name == "Claude Mythos Preview"))
        items.append((final, f"{final:g}%", name, col))
    bf.log_axis(ax, "x", ticks=[1e4, 3e4, 1e5, 3e5, 1e6, 2e6]); ax.set_xlim(1e4, 2e6)
    bf.tidy(ax, xlabel="Output-token budget per attempt (log scale)", ypct=True)
    ax.set_yticks([5, 10, 15]); ax.set_ylim(0, 16)
    bf.right_labels(ax, items)
    fig.subplots_adjust(right=0.60)
    bf.headline(fig, "GLM-5.3 is the first open-weight model to show substantial exploitation capability",
                "ExploitBench, public benchmark. Share of each model's attempts that built a complete working exploit within the budget. "
                "All attempts ran in isolated sandboxes against local test builds; no real system was touched.")
    return bf.save(fig, out / "step_curves")


def curves(out):
    """Metric sampled at a few budgets (pass@k vs k): lines with a dot per measured point, log-x,
    right-hand labels, and a hero-tint gap band that prints the delta where the user wants it seen."""
    bf.use_style()
    fig, ax = bf.figure(width=820, height=520)
    k = np.array([1, 2, 4, 8, 16, 32, 64, 128])
    runs = [("Nova-2", [31, 38, 45, 52, 58, 63, 67, 70], bf.ACCENT, True), ("Rho-4", [28, 34, 40, 46, 51, 55, 58, 60], bf.BLUE, False),
            ("Nova-1", [22, 27, 33, 39, 44, 48, 51, 53], bf.ACCENT_MID, False), ("OpenWeight-70B", [12, 16, 21, 26, 31, 35, 38, 40], bf.SLATE, False),
            ("OpenWeight-7B", [3, 5, 7, 9, 11, 13, 14, 15], bf.MUTED, False)]   # MUTED, not MUTED_LIGHT: it runs near the baseline
    bf.gap_band(ax, k, runs[0][1], runs[1][1], "+10 pts", at="end")
    items = []
    for name, y, col, hero in runs:
        bf.curve(ax, k, y, color=col, hero=hero)
        items.append((y[-1], f"{y[-1]}%", name, col))
    bf.log_axis(ax, "x", ticks=list(k)); ax.set_xlim(1, 128)
    bf.tidy(ax, xlabel="k, samples per problem (log scale)", ypct=True); ax.set_ylim(0, 80); ax.set_yticks([0, 20, 40, 60, 80])
    bf.right_labels(ax, items)
    fig.subplots_adjust(right=0.68)
    bf.headline(fig, "Nova-2's lead widens with more samples: 10 points ahead at k = 128",
                "pass@k on the hidden test set: share of problems where at least one of k sampled solutions passes every test. Nova-2 is ours.")
    bf.footnote(fig, "Shaded band: gap between Nova-2 and Rho-4, the best non-Nova model at every k. n = 1,200 problems.")
    return bf.save(fig, out / "curves")


def time_to_k(out):
    """Cream 'native' variant: progress lines with dots, a large X where each run stopped, frameless colored legend."""
    bf.use_style(theme="cream")
    fig, ax = bf.figure(width=1000, height=600)
    runs = [("Mythos Preview", bf.ACCENT_BRIGHT, [0.98, 1.6, 2.9, 3.2, 5.0, 6.0, 8.6, 11.8], 11.8),
            ("Opus 4.8", bf.NAVY, [1.03, 2.0], 2.0), ("Opus 4.6", "#5C9FE3", [1.8], 1.8), ("Sonnet 4.6", bf.VIOLET, [15.3], 15.3)]
    for name, col, times, stop in runs:
        y = np.arange(1, len(times) + 1)
        ax.plot(times, y, marker="o", color=col, label=name, linewidth=2.2, markersize=bf.px(9), markeredgewidth=0, zorder=3)
        bf.terminal_marker(ax, times[-1], y[-1], bf.fmt_duration(stop), color=col)
    bf.duration_axis(ax, "x"); ax.set_xticks([3, 6, 9, 12, 15]); ax.set_xlim(0, 16.5)
    bf.tidy(ax, xlabel="Time from launch", ylabel="N-th exploit reproduced", left_spine=True, ymin0=False)
    ax.set_yticks(range(1, 9)); ax.set_ylim(0.5, 8.5)
    bf.leader(ax, (0.98, 1), "59m", (26, 112), color=bf.ACCENT_BRIGHT)
    bf.leader(ax, (1.03, 1), "62m", (26, 148), color=bf.NAVY)
    bf.legend(ax, loc="upper right", colored_text=False)
    bf.headline(fig, "Time to working exploits for 18 SpiderMonkey CVEs patched in Firefox 147 to 149",
                accent_bar=False, color=bf.ACCENT_BRIGHT, size=bf.T.section, weight="normal", ha="center")
    return bf.save(fig, out / "time_to_k")


def hollow_bars(out):
    """Before/after a modification of the same entity: solid vs hollow bars, group headers with hairline rules."""
    bf.use_style()
    fig, ax = bf.figure(width=880, height=560)
    xs = [0, 1, 2, 3.6, 4.6, 6.2, 7.2]
    h = [96, 95, 96, 95, 6, 95, 14]
    cols = [bf.BLUE_RAMP[0], bf.BLUE_RAMP[1], bf.BLUE_RAMP[2], bf.GREEN_BRIGHT, bf.GREEN_BRIGHT, bf.GREEN_TINT, bf.GREEN_TINT]
    hollow = [False, False, False, False, True, False, True]
    bf.bars(ax, xs, h, colors=cols, hollow=hollow, width=0.62, errors=[2, 2, 2, 2, 2, 2, 3], cap=2,
            label_colors=cols[:5] + [bf.GREEN_BRIGHT, bf.GREEN_BRIGHT])   # tint bars get a darker label
    bf.category_labels(ax, [0, 1, 2, 4.1, 6.7], ["Opus 4.8", "Opus 5", "Mythos\nPreview", "GLM-5.3", "GLM-5.3-Flash"],
                       [None, None, None, "model            abliterated", "model            abliterated"])
    bf.tidy(ax, ypct=True); ax.set_yticks([50, 100]); ax.set_ylim(0, 118)
    bf.group_header(ax, -0.4, 2.4, "Claude models (safeguards disabled)", y=1.0)
    bf.group_header(ax, 3.2, 7.6, "Open-weight models", y=1.0)
    bf.headline(fig, "Abliteration removes GLM-5.3's refusals and leaves its capabilities largely intact",
                "Mean refusal rate across three harmful-request benchmarks, weighted equally. "
                "Solid bars: model. Hollow bars: abliterated (only possible with open-weight models).")
    bf.footnote(fig, "Whiskers: approximate 95% intervals.")
    return bf.save(fig, out / "hollow_bars")


def stacked_sections(out):
    """Two sub-analyses sharing one theme: a tall figure with one plain headline, a section header per
    axes (anchored to the axes so fit() reserves room), hollow bars, group headers, one footnote."""
    bf.use_style()
    fig, (top, bot) = bf.figure(width=760, height=960, nrows=2, gridspec_kw=dict(height_ratios=[1, 1], hspace=1.15))
    xs = [0, 1, 2, 3.6, 4.6, 6.2, 7.2]
    cols = [bf.BLUE_RAMP[0], bf.BLUE_RAMP[1], bf.BLUE_RAMP[2], bf.GREEN_BRIGHT, bf.GREEN_BRIGHT, bf.GREEN_TINT, bf.GREEN_TINT]
    lab = cols[:5] + [bf.GREEN_BRIGHT, bf.GREEN_BRIGHT]
    bf.bars(top, xs, [96, 95, 96, 95, 6, 95, 14], colors=cols, hollow=[0, 0, 0, 0, 1, 0, 1], width=0.62, errors=[2] * 7, cap=2, label_colors=lab)
    bf.category_labels(top, [0, 1, 2, 4.1, 6.7], ["Opus 4.8", "Opus 5", "Mythos\nPreview", "GLM-5.3", "GLM-5.3-Flash"],
                       ["as released", "abliterated", "as released", "abliterated"], sub_x=[3.6, 4.6, 6.2, 7.2])
    bf.tidy(top, ypct=True); top.set_yticks([50, 100]); top.set_ylim(0, 118)
    bf.group_header(top, -0.4, 2.4, "Claude models (safeguards disabled)", y=1.0)
    bf.group_header(top, 3.2, 7.6, "Open-weight models", y=1.0)
    bf.section_header(top, "Refusal rate on harmful requests", "Share of harmful requests refused — higher is safer")
    # second section: same x positions as the top so columns line up; Claude bars solid only (no abliterated variant)
    bf.bars(bot, xs, [86, 88, 90, 88, 88, 89, 89], colors=cols, hollow=[0, 0, 0, 0, 1, 0, 1], width=0.62, errors=[2] * 7, cap=2, label_colors=lab)
    bf.category_labels(bot, [0, 1, 2, 4.1, 6.7], ["Opus 4.8", "Opus 5", "Mythos\nPreview", "GLM-5.3", "GLM-5.3-Flash"],
                       ["as released", "abliterated", "as released", "abliterated"], sub_x=[3.6, 4.6, 6.2, 7.2])
    bf.tidy(bot, ypct=True); bot.set_yticks([50, 100]); bot.set_ylim(0, 118)
    bf.group_header(bot, -0.4, 2.4, "Claude models (as deployed)", y=1.0)
    bf.group_header(bot, 3.2, 7.6, "Open-weight models", y=1.0)
    bf.section_header(bot, "Capability (GPQA-Diamond)", "Accuracy — higher is better")
    for a in (top, bot):
        a.set_xlim(-0.6, 7.8)
    bf.headline(fig, "Abliteration strips GLM-5.3's refusals but leaves its capability untouched",
                "Claude models with safeguards disabled vs. open-weight GLM-5.3 models. Solid bars: model as released. "
                "Hollow bars: abliterated (only possible with open weights).", accent_bar=False, weight="medium")
    bf.footnote(fig, "Whiskers: 95% intervals (±2 points on every bar). Claude models cannot be abliterated: their weights are not released.")
    return bf.save(fig, out / "stacked_sections")


def panel_row(out):
    """Same metric family on three tasks: 1×3 panels, one centred legend row under the subtitle (with a
    95% CI entry), per-panel direction subtitle. Wrap category names; do not rotate."""
    import textwrap
    bf.use_style()
    fig, axes = bf.figure(width=1100, height=580, ncols=3)
    models = ["Sonnet 5", "Opus 5", "Mythos Preview", "Mythos 5", "Kimi K3"]
    cols = ["#74BDF2", bf.GREEN, bf.LAVENDER, bf.PLUM, bf.SLATE]
    data = [("Guiding a drone to a target", "Strike rate — higher is better", [1, 20, 13, 10, 2], [1, 8, 6, 5, 2], "{:.0f}%"),
            ("Dropping a payload on a target", "Landed within 5 m — higher is better", [31, 65, 63, 56, 38], [12, 10, 10, 12, 12], "{:.0f}%"),
            ("Flying without GPS", "Median final distance — lower is better", [220, 25, 41, 46, 185], [60, 8, 14, 15, 35], "{:.0f} m")]
    x = np.arange(5)
    for ax, (title, sub, vals, err, fmt) in zip(axes, data):
        bf.bars(ax, x, vals, colors=cols, width=0.72, errors=err, fmt=fmt, label_colors=[bf.INK] * 5, label_size=14)
        bf.category_labels(ax, x, [textwrap.fill(m, 7) for m in models], size=12)
        bf.tidy(ax, ypct=fmt.endswith("%"), ymax_pad=0.15)
        bf.panel_title(ax, title, sub=sub, wrap=30)
    fig.subplots_adjust(wspace=0.45)
    bf.headline(fig, "Drone evals: Opus 5 leads on two of three flight-software tasks",
                "All difficulty settings pooled per model; 12 launches (strike), 15 flights (payload) per model. Whiskers: 95% CI.")
    bf.inline_legend(fig, [(m, c, "square") for m, c in zip(models, cols)] + [("95% CI", bf.WHISKER, "whisker")],
                     y=None, fig_coords=True, align="center")        # sits under the subtitle; fit() keeps panels below
    return bf.save(fig, out / "panel_row")


def panel_grid(out):
    """Four related findings: 2×2 grid, accent lowercase letters, each panel header is its own takeaway."""
    bf.use_style()
    fig, axes = bf.figure(width=960, height=980, nrows=2, ncols=2)
    (a, b), (c, d) = axes
    rng = np.random.default_rng(1)
    # a: progress-over-iterations — gray proposals, gray x rejected, terracotta best-so-far step, endpoint label
    n = 165
    idx = np.arange(n)
    prop = np.clip(45 + 25 * (1 - np.exp(-idx / 40)) + rng.normal(0, 12, n), 0, 86)
    rejected = rng.random(n) < 0.45
    acc = np.where(~rejected)[0]
    best = np.maximum.accumulate(prop[acc])                       # best-so-far over accepted proposals only
    a.scatter(idx[~rejected], prop[~rejected], s=bf.px(22), color=bf.MUTED_LIGHT, zorder=2, linewidths=0)
    a.scatter(idx[rejected], prop[rejected], s=bf.px(26), color="#C2C2BF", marker="x", linewidths=1.2, zorder=2)
    a.step(np.append(acc, idx[-1]), np.append(best, best[-1]), where="post", color=bf.ACCENT, linewidth=2.6, zorder=3)
    a.plot([idx[-1]], [best[-1]], marker="o", markersize=bf.px(11), color=bf.ACCENT, zorder=4, clip_on=False)
    bf.value_label(a, idx[-1] - 20, best[-1], f"{best[-1]:.0f}%", dy=12, size=18)
    bf.tidy(a, xlabel="Methods proposed by the AARs, in order", ylabel="Safety headroom closed\n(% of the gap to a perfect score)")
    a.set_ylim(0, 100); a.set_yticks([0, 25, 50, 75, 100])
    bf.inline_legend(a, [("Best so far", bf.ACCENT, "line"), ("Proposed method", bf.MUTED_LIGHT, "dot"), ("Rejected (capability dropped)", "#C2C2BF", "x")],
                     y=1.06, size=12, gap_px=12)
    bf.panel_title(a, "Safety improves as the AARs iterate, without losing general capability", letter="a", pad=30)
    # b: two lines with whiskers, labelled on the line
    turns = [1, 3, 5]
    (l1,) = b.plot(turns, [6.3, 7.3, 8.2], marker="o", color=bf.BLUE, markersize=bf.px(10), zorder=3)
    (l2,) = b.plot(turns, [4.3, 5.7, 6.5], marker="D", color=bf.ACCENT, markersize=bf.px(9), zorder=3)
    for line, lo, hi in ((l1, [5.6, 6.9, 8.0], [7.0, 7.7, 8.4]), (l2, [3.6, 5.0, 6.2], [5.0, 6.4, 6.8])):
        yv = np.array(line.get_ydata())
        eb = b.errorbar(turns, yv, yerr=[yv - np.array(lo), np.array(hi) - yv],
                        fmt="none", ecolor=line.get_color(), elinewidth=1.4, capsize=0, zorder=2)
        eb[2][0].set_linestyle((0, (4, 3)))
    bf.label_line(b, l1, "Untrained model", where="mid", dy=14)
    bf.label_line(b, l2, "With the AAR-found method", where="mid", dy=-26)
    bf.tidy(b, xlabel="Length of audit conversation (turns)", ylabel="Petri audit score\n(1–10, lower is safer)", ymin0=False)
    b.set_xticks(turns); b.set_ylim(1, 10); b.set_yticks([2, 4, 6, 8, 10])
    bf.panel_title(b, "The method holds up under an open-ended, multi-turn behavioral audit", letter="b", pad=30)
    # c: grouped bars
    x = np.arange(2); w = 0.36
    bf.bars(c, x - w / 2, [59, 67], colors=[bf.BLUE], width=w, errors=[5, 5])
    bf.bars(c, x + w / 2, [79, 88], colors=[bf.ACCENT], width=w, errors=[5, 4])
    bf.category_labels(c, x, ["Gemma-2-2B", "Gemma-2-9B"], ["the model the method\nwas developed on", "4.5× more parameters"])
    bf.tidy(c, ylabel="Honest responses on a held-out\ndeception benchmark (%)"); c.set_ylim(0, 100); c.set_yticks([0, 25, 50, 75, 100])
    bf.inline_legend(c, [("Untrained model", bf.BLUE, "square"), ("With the AAR-found method", bf.ACCENT, "square")], y=1.06, size=12)
    bf.panel_title(c, "The same method works on a model 4.5× the size", letter="c", pad=30)
    # d: two bars
    bf.bars(d, [0, 1], [85, 20], colors=[bf.ACCENT, bf.GREEN], width=0.5, errors=[[10, 15], [9, 33]])
    bf.category_labels(d, [0, 1], ["Best AAR-found\nmethods", "Ideas from experienced\nresearchers"], ["average over 6 AAR runs", "average over 6 ideas"])
    bf.tidy(d, ylabel="Safety headroom closed\n(% of the gap to a perfect score)"); d.set_ylim(0, 100); d.set_yticks([0, 25, 50, 75, 100])
    bf.panel_title(d, "The AARs' best methods beat the ideas proposed by experienced researchers", letter="d", pad=30)
    fig.subplots_adjust(wspace=0.5, hspace=0.75, left=0.1, right=0.97)
    bf.headline(fig, "Automated alignment researchers (AARs) reduce deception in a small open model, and the improvement generalizes")
    return bf.save(fig, out / "panel_grid")


def na_bars(out):
    """Zeros as labelled slivers, not-applicable as padlock + reason, escalating conditions as a single-hue ramp."""
    bf.use_style()
    fig, ax = bf.figure(width=1000, height=540)
    conds = ["Bare\norder", "False\ncover story", "Reasoning\nprefilled", "Abliterated"]
    ramp = bf.ramp(bf.CRIMSON_RAMP, 4)
    xl = np.arange(4, dtype=float); xr = xl + 5.2
    # the palest ramp step is too light for text: label it with the next step's color
    bf.bars(ax, xl[:2], [0, 0], colors=[ramp[0], ramp[1]], width=0.62, label_colors=[ramp[1], ramp[1]])
    bf.na_marker(ax, xl[2], "prefill not\noffered", label_lines=2); bf.na_marker(ax, xl[3], "weights not\nreleased", label_lines=1)
    bf.bars(ax, xr, [0, 64, 92, 100], colors=ramp, width=0.62, label_colors=[ramp[1], ramp[1], ramp[2], ramp[3]])
    bf.category_labels(ax, np.concatenate([xl, xr]), conds * 2, size=13)
    bf.tidy(ax, ypct=True); ax.set_yticks([]); ax.set_ylim(0, 125); ax.grid(False)
    bf.group_header(ax, -0.4, 3.4, "Claude Opus 5\nas deployed, with API safeguards", y=1.0)
    bf.group_header(ax, 4.8, 8.6, "GLM-5.3\nopen weights", y=1.0)
    bf.headline(fig, "GLM-5.3's safeguards are easily bypassed; Claude's are not exposed to the same attacks",
                "How often the model tried to connect to a remote target when given an overtly malicious cyber-attack order "
                "(50 simulated episodes per bar; nothing was executed).")
    return bf.save(fig, out / "na_bars")


RECIPES = {f.__name__: f for f in (grouped_bars, launch_bars, lollipop, step_curves, curves, time_to_k, hollow_bars, stacked_sections, panel_row, panel_grid, na_bars)}

if __name__ == "__main__":
    args = sys.argv[1:]
    out = pathlib.Path(args[0] if args else "blogfig-demo"); out.mkdir(parents=True, exist_ok=True)
    names = args[1:] or list(RECIPES)
    for n in names:
        print(n, "->", ", ".join(map(str, RECIPES[n](out))))
