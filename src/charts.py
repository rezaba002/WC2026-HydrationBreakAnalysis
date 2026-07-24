"""Milestone-1 charts: break-timing distribution and WBGT overview.

Outputs (reports/figures/):
  fig_break_timing.png
  fig_wbgt.png

Run:  python -m src.charts
"""
from __future__ import annotations

from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd

from .util import FIGURES, PROCESSED

# palette (light surface)
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BLUE = "#2a78d6"    # H1 series
GREEN = "#008300"   # H2 series
CRITICAL = "#d03b3b"

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "font.family": "Segoe UI",
        "text.color": INK,
        "axes.edgecolor": "#c3c2b7",
        "axes.labelcolor": INK2,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "axes.axisbelow": True,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
    }
)


def _bars(ax, counts: Counter, color: str, nominal: int, label: str):
    minutes = sorted(counts)
    vals = [counts[m] for m in minutes]
    ax.bar(minutes, vals, width=0.82, color=color, edgecolor=SURFACE, linewidth=1.5)
    ax.set_ylim(0, max(vals) * 1.24)
    ax.axvline(nominal - 0.5, color=MUTED, linestyle=(0, (4, 3)), linewidth=1.2)
    ax.text(nominal - 0.72, max(vals) * 0.72, f"nominal {nominal}'",
            color=MUTED, fontsize=9, ha="center", va="center", rotation=90)
    for m, v in zip(minutes, vals):
        ax.text(m, v + 0.6, str(v), ha="center", va="bottom", color=INK2, fontsize=9)
    ax.set_title(label, color=INK, fontsize=11, loc="left", pad=10)
    ax.set_xlabel("break start minute (match clock)")
    ax.grid(axis="x", visible=False)
    ax.tick_params(length=0)


def fig_break_timing(breaks: pd.DataFrame):
    h1 = Counter(breaks.loc[breaks["half"] == "H1", "start_minute"])
    h2 = Counter(breaks.loc[breaks["half"] == "H2", "start_minute"])
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2), sharey=True)
    _bars(axes[0], h1, BLUE, 22, f"First half — {sum(h1.values())} breaks")
    _bars(axes[1], h2, GREEN, 67, f"Second half — {sum(h2.values())} breaks")
    axes[0].set_ylabel("matches")
    fig.suptitle("Hydration breaks started later than the nominal minute",
                 x=0.065, ha="left", fontsize=14, fontweight="bold", color=INK)
    fig.text(0.065, 0.895,
             "Actual start minutes of the 203 recorded breaks, WC2026 (102 matches). "
             "Modal starts: 23' and 68'.",
             fontsize=10, color=INK2)
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    fig.savefig(FIGURES / "fig_break_timing.png", dpi=200)
    plt.close(fig)


def fig_wbgt(breaks: pd.DataFrame):
    wbgt = breaks["wbgt"].dropna()
    n_above = int((wbgt > 28).sum())
    fig, ax = plt.subplots(figsize=(9, 4.2))
    bins = [b / 2 for b in range(34, 78)]  # 17.0 .. 38.5 in 0.5 steps
    counts, _, _ = ax.hist(wbgt, bins=bins, color=BLUE, edgecolor=SURFACE, linewidth=0.8)
    ax.set_ylim(0, counts.max() * 1.32)
    ax.axvline(28, color=CRITICAL, linewidth=1.6)
    ax.text(28.2, counts.max() * 1.27,
            f"FIFPRO 28°C threshold — {n_above} of {len(wbgt)} breaks above",
            color=CRITICAL, fontsize=9.5, va="top")
    ax.set_xlabel("estimated WBGT at break (°C)")
    ax.set_ylabel("breaks")
    ax.grid(axis="x", visible=False)
    ax.tick_params(length=0)
    ax.set_title("Under the old heat-triggered rule, most 2026 breaks would not have happened",
                 color=INK, fontsize=13, fontweight="bold", loc="left", pad=24)
    ax.text(0, 1.045, "Estimated wet-bulb globe temperature at each of the 203 breaks. "
            f"Median {wbgt.median():.1f}°C.",
            transform=ax.transAxes, fontsize=10, color=INK2)
    fig.tight_layout()
    fig.savefig(FIGURES / "fig_wbgt.png", dpi=200)
    plt.close(fig)


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    breaks = pd.read_csv(PROCESSED / "breaks.csv")
    fig_break_timing(breaks)
    fig_wbgt(breaks)
    print(f"wrote {FIGURES / 'fig_break_timing.png'}")
    print(f"wrote {FIGURES / 'fig_wbgt.png'}")


if __name__ == "__main__":
    main()
