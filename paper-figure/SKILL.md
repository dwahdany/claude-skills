---
name: paper-figure
description: Publication-ready figure styling for ML papers (ICML format). Use when creating, editing, or reviewing plots/figures for an academic paper — matplotlib/seaborn setup, vector PDF output, column sizing, despined axes, colorblind-safe palettes, separate legend export, and LaTeX integration.
---

# Figure Style Guide

Target venue: **ICML** (A* top-tier ML conference). All figures must be publication-ready.

## Core Principle

**Each figure answers exactly ONE question.** Before creating a figure, write down the question it answers. If you can't state the question in one sentence, split the figure.

Examples:
- "How does attack performance scale with shadow count?" → ablation plot
- "Does LiRA outperform the baseline in the low-FPR regime?" → ROC comparison (log-log)
- "Are member and non-member signal distributions separable?" → distribution histogram

## Mandatory Rules

| Rule | Requirement |
|------|-------------|
| **Purpose** | Each figure answers exactly ONE question |
| **Format** | PDF only (vector graphics) |
| **Size** | 2.5" × 2.5" (single column) or 5.3" × 2.5" (double column) |
| **Spines** | Despine — remove top and right spines |
| **Title** | None — titles go in LaTeX `\caption{}`, not on the figure |
| **Font** | 8–10pt, matching paper font |
| **Colors** | Colorblind-safe palette |
| **Background** | White background |
| **Grid** | Light gray gridlines |
| **Error Bars** | Error bars should be visible |
| **Scale** | Axes should be scaled to match data range (e.g., log scale) |
| **Styles** | Use different line and marker styles to support colorblind readability |
| **Labels** | All axes labeled with units |
| **Legend** | Export to separate PDF file (`*_legend.pdf`) |

## Code Template

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Call once at script start
def setup_style():
    sns.set_theme(style="ticks", font_scale=1.0)
    plt.rcParams.update({
        "figure.figsize": (2.5, 2.5),
        "font.size": 9,
        "axes.labelsize": 9,
        "axes.titlesize": 0,       # No title on figure
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "savefig.format": "pdf",
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.02,
        "pdf.fonttype": 42,        # TrueType fonts (editable in Illustrator)
        "ps.fonttype": 42,
    })

# Call before saving each figure
def save_figure(fig, path):
    """Save figure with ICML styling applied. Extracts and exports legend separately."""
    # Extract legend handles/labels before removing
    handles, labels = [], []
    for ax in fig.axes:
        ax.set_title("")  # Ensure no title
        h, l = ax.get_legend_handles_labels()
        if h:
            handles.extend(h)
            labels.extend(l)
        if ax.get_legend():
            ax.get_legend().remove()  # Remove legend from figure

    sns.despine(fig=fig)  # Remove top/right spines
    fig.savefig(path)

    # Export legend variants to separate files
    if handles and labels:
        save_legend_variants(handles, labels, path.replace(".pdf", ""))

    plt.close(fig)

def save_legend_variants(handles, labels, path_stem):
    """Export legend in multiple layouts (different ncols) for flexible LaTeX placement.

    Creates:
      {path_stem}_legend_1col.pdf  - vertical (1 column)
      {path_stem}_legend_2col.pdf  - 2 columns
      {path_stem}_legend_Ncol.pdf  - horizontal (N columns, where N = len(labels))
    """
    n = len(labels)
    ncol_variants = sorted(set([1, 2, min(3, n), n]))  # 1, 2, 3 (if applicable), all

    for ncol in ncol_variants:
        nrow = (n + ncol - 1) // ncol
        fig_leg = plt.figure(figsize=(1.2 * ncol, 0.3 * nrow))
        fig_leg.legend(handles, labels, loc="center", frameon=False, ncol=ncol)
        fig_leg.savefig(f"{path_stem}_legend_{ncol}col.pdf", bbox_inches="tight", pad_inches=0.02)
        plt.close(fig_leg)
```

## Usage

```python
setup_style()

fig, ax = plt.subplots()
ax.plot(fpr, tpr_lira, label="LiRA")
ax.plot(fpr, tpr_baseline, label="Baseline")
ax.set_xlabel("False Positive Rate")
ax.set_ylabel("True Positive Rate")

# Extracts legend automatically, removes from figure, saves variants
save_figure(fig, "figures/fig_roc_linear.pdf")
# Creates:
#   fig_roc_linear.pdf              (no legend)
#   fig_roc_linear_legend_1col.pdf  (vertical)
#   fig_roc_linear_legend_2col.pdf  (horizontal)
```

## Colorblind-Safe Palette

```python
# Okabe-Ito palette (recommended)
COLORS = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "green": "#009E73",
    "pink": "#CC79A7",
    "yellow": "#F0E442",
    "cyan": "#56B4E9",
    "red": "#D55E00",
    "black": "#000000",
}

# Or use seaborn's colorblind palette
sns.set_palette("colorblind")
```

## Double-Column Figures

```python
fig, axes = plt.subplots(1, 2, figsize=(5.3, 2.5))
# ... plot on axes[0] and axes[1]
save_figure(fig, "figures/fig_comparison.pdf")
```

## LaTeX Integration

Legend variants let you choose the best layout:
- `*_legend_1col.pdf` — vertical, good for side placement
- `*_legend_2col.pdf` — compact horizontal
- `*_legend_Ncol.pdf` — single row, all items horizontal

```latex
\begin{figure}[t]
  \centering
  \includegraphics[width=\linewidth]{figures/fig_roc_linear.pdf}
  \includegraphics[width=0.6\linewidth]{figures/fig_roc_linear_legend_2col.pdf}
  \caption{\textbf{Takeaway in bold.} Details explaining the figure.}
  \label{fig:roc}
\end{figure}
```

Share one legend across subfigures:

```latex
\begin{figure}[t]
  \centering
  \begin{subfigure}[b]{0.48\linewidth}
    \includegraphics[width=\linewidth]{figures/fig_roc_linear.pdf}
    \caption{Linear scale}
  \end{subfigure}
  \hfill
  \begin{subfigure}[b]{0.48\linewidth}
    \includegraphics[width=\linewidth]{figures/fig_roc_loglog.pdf}
    \caption{Log-log scale}
  \end{subfigure}
  \\[0.5em]
  \includegraphics[width=0.6\linewidth]{figures/fig_roc_linear_legend_2col.pdf}
  \caption{\textbf{ROC curves for LiRA attack.} (a) Full ROC curve. (b) Low-FPR regime.}
  \label{fig:roc}
\end{figure}
```

## Checklist

Before committing any figure:

- [ ] Answers exactly ONE question (can you state it in one sentence?)
- [ ] Saved as `.pdf`
- [ ] No title on figure (title is in LaTeX caption)
- [ ] Top and right spines removed
- [ ] Legend exported to separate files (`*_legend_{1,2,N}col.pdf`)
- [ ] Axes labeled with units
- [ ] Font readable at 50% zoom
- [ ] Colorblind-safe colors
