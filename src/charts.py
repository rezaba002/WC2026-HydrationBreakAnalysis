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
    """Two reference lines: FIFA's former MANDATORY trigger (>=32C) and
    FIFPRO's guidance level (>=28C). They are different policies and the
    report must not conflate them."""
    wbgt = breaks["wbgt"].dropna()
    n32 = int((wbgt >= 32).sum())
    n28 = int((wbgt >= 28).sum())
    fig, ax = plt.subplots(figsize=(9.5, 4.4))
    bins = [b / 2 for b in range(34, 78)]  # 17.0 .. 38.5 in 0.5 steps
    counts, _, _ = ax.hist(wbgt, bins=bins, color=BLUE, edgecolor=SURFACE, linewidth=0.8)
    top = counts.max()
    ax.set_ylim(0, top * 1.42)

    ax.axvline(28, color=MUTED, linewidth=1.4, linestyle=(0, (4, 3)))
    ax.text(27.7, top * 1.36, f"FIFPRO guidance 28°C\n{n28} of {len(wbgt)} breaks at/above",
            color=INK2, fontsize=9, va="top", ha="right")

    ax.axvline(32, color=CRITICAL, linewidth=1.8)
    ax.text(32.3, top * 1.36,
            f"FIFA's former MANDATORY trigger 32°C\nonly {n32} of {len(wbgt)} breaks at/above",
            color=CRITICAL, fontsize=9, va="top")

    ax.set_xlabel("estimated WBGT at break (°C)")
    ax.set_ylabel("breaks")
    ax.grid(axis="x", visible=False)
    ax.tick_params(length=0)
    ax.set_title("Four in five breaks happened below FIFA's own former mandatory threshold",
                 color=INK, fontsize=13, fontweight="bold", loc="left", pad=24)
    ax.text(0, 1.045, "Estimated wet-bulb globe temperature at each of the 203 breaks. "
            f"Median {wbgt.median():.1f}°C. FIFA and FIFPRO thresholds differ — see report §2.",
            transform=ax.transAxes, fontsize=9.5, color=INK2)
    fig.tight_layout()
    fig.savefig(FIGURES / "fig_wbgt.png", dpi=200)
    plt.close(fig)


def fig_placebo():
    """The central chart: real breaks vs 10,000 randomized pseudo-break draws."""
    draws = pd.read_csv(PROCESSED / "placebo_null_draws.csv")

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6))

    # Left: primary metric — balance disruption, break-adjusted clock
    d = draws[(draws["clock"] == "adjusted") & (draws["outcome"] == "balance_disruption")]
    obs = d["observed_mean"].iloc[0]
    ax = axes[0]
    ax.hist(d["null_mean"], bins=40, color="#9ec5f4", edgecolor=SURFACE, linewidth=0.4)
    ax.axvline(obs, color=BLUE, linewidth=2.2)
    ax.text(obs - 0.008, ax.get_ylim()[1] * 0.97, "real breaks", color=BLUE,
            fontsize=10, ha="right", va="top", fontweight="bold")
    ax.set_title("Breaks did not scramble the game\nmore than ordinary minutes",
                 color=INK, fontsize=12, fontweight="bold", loc="left")
    ax.set_xlabel("mean |Δ shot balance|, 8-min windows")
    ax.set_ylabel("pseudo-break draws")

    # Right: the naive illusion — next-shot probability on both clocks
    d2 = draws[(draws["clock"] == "display") & (draws["outcome"] == "next_shot_within_w")]
    d2a = draws[(draws["clock"] == "adjusted") & (draws["outcome"] == "next_shot_within_w")]
    ax = axes[1]
    ax.hist(d2["null_mean"], bins=40, color="#9ec5f4", edgecolor=SURFACE, linewidth=0.4)
    naive, corrected = d2["observed_mean"].iloc[0], d2a["observed_mean"].iloc[0]
    ax.axvline(naive, color=CRITICAL, linewidth=2.2, linestyle=(0, (4, 2)))
    ax.axvline(corrected, color=BLUE, linewidth=2.2)
    ymax = ax.get_ylim()[1]
    ax.text(naive - 0.004, ymax * 0.97, "naive clock:\n\"breaks kill momentum\"",
            color=CRITICAL, fontsize=9.5, ha="right", va="top")
    ax.text(corrected + 0.004, ymax * 0.63, "dead time removed:\nback inside the null",
            color=BLUE, fontsize=9.5, ha="left", va="top", fontweight="bold")
    ax.set_title("The \"momentum kill\" is three minutes\nof stopped clock",
                 color=INK, fontsize=12, fontweight="bold", loc="left")
    ax.set_xlabel("P(any shot within 8 min after restart)")

    for ax in axes:
        ax.grid(axis="x", visible=False)
        ax.tick_params(length=0)
    fig.suptitle("Real hydration breaks vs 10,000 moments where nobody stopped the game",
                 x=0.055, y=1.0, ha="left", fontsize=14, fontweight="bold", color=INK)
    fig.text(0.055, 0.925,
             "196 breaks, pseudo-breaks matched on half, score state and stage; "
             "windows exclude the hydration stoppage (break-adjusted clock).",
             fontsize=10, color=INK2)
    fig.tight_layout(rect=(0, 0, 1, 0.87))
    fig.savefig(FIGURES / "fig_placebo.png", dpi=200)
    plt.close(fig)


def main():
    FIGURES.mkdir(parents=True, exist_ok=True)
    breaks = pd.read_csv(PROCESSED / "breaks.csv")
    fig_break_timing(breaks)
    fig_wbgt(breaks)
    fig_placebo()
    print(f"wrote {FIGURES / 'fig_break_timing.png'}")
    print(f"wrote {FIGURES / 'fig_wbgt.png'}")
    print(f"wrote {FIGURES / 'fig_placebo.png'}")


if __name__ == "__main__":
    main()
