"""Article figures — generated FROM reports/facts.json, never hand-drawn.

These are presentation charts for the published article. They add no analysis:
every value is read from facts.json, which src/facts.py regenerates from the
analysis tables. If a number changes upstream, these figures change with it, so
a chart cannot go stale the way the prose used to.

Outputs (reports/figures/):
  art_clock.png          the display-vs-adjusted clock artifact
  art_test_a_forest.png  primary estimate + control-support sensitivity
  art_test_b_forest.png  directional test by window
  art_regression.png     real vs matched swing — regression to the mean
  art_perception.png     the denominator, not the hit rate
  art_goals_trap.png     the false positive that goals would have produced

Run:  python -m src.article_figures   (after python -m src.facts)
"""
from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np

from .charts import BLUE, CRITICAL, GRID, GREEN, INK, INK2, MUTED, SURFACE  # noqa: F401
from .util import FIGURES, REPORTS

W_IN, H_IN, DPI = 9.2, 5.0, 200


def _facts() -> dict:
    return json.loads((REPORTS / "facts.json").read_text(encoding="utf-8"))


def _finish(fig, ax, title: str, subtitle: str, source: str = "") -> None:
    ax.tick_params(length=0)
    fig.suptitle(title, x=0.045, y=0.975, ha="left", fontsize=13.5,
                 fontweight="bold", color=INK)
    fig.text(0.045, 0.90, subtitle, ha="left", va="top", fontsize=9.6, color=INK2)
    if source:
        fig.text(0.045, 0.028, source, ha="left", fontsize=8.2, color=MUTED)


def _forest(ax, labels, est, lo, hi, colors, xlabel):
    y = np.arange(len(labels))[::-1]
    ax.axvline(0, color=INK, linewidth=1.3, zorder=1)
    for yi, e, l, h, c in zip(y, est, lo, hi, colors):
        ax.plot([l, h], [yi, yi], color=c, linewidth=2.4, solid_capstyle="round", zorder=2)
        ax.plot([l, l], [yi - .12, yi + .12], color=c, linewidth=2.0, zorder=2)
        ax.plot([h, h], [yi - .12, yi + .12], color=c, linewidth=2.0, zorder=2)
        ax.scatter([e], [yi], s=74, color=c, zorder=3, edgecolor=SURFACE, linewidth=1.4)
        ax.annotate(f"{e:+.3f}  [{l:+.3f}, {h:+.3f}]", xy=(h, yi), xytext=(9, 0),
                    textcoords="offset points", va="center", fontsize=9, color=INK2)
    ax.set_yticks(y, labels, fontsize=10, color=INK)
    ax.set_xlabel(xlabel)
    ax.grid(axis="y", visible=False)
    span = max(hi) - min(lo)
    ax.set_xlim(min(lo) - span * .08, max(hi) + span * .62)


# ---------------------------------------------------------------- 1. the clock
def fig_clock(f):
    c = f["clock"]
    fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=DPI)
    ws = [5, 8, 10]
    x = np.arange(len(ws))
    disp = [c[f"display_w{w}"]["observed"] for w in ws]
    adj = [c[f"adjusted_w{w}"]["observed"] for w in ws]
    null = [c[f"display_w{w}"]["null"] for w in ws]

    ax.bar(x - 0.21, disp, width=0.40, color=CRITICAL, edgecolor=SURFACE,
           linewidth=1.6, label="display clock (window contains the stoppage)")
    ax.bar(x + 0.21, adj, width=0.40, color=BLUE, edgecolor=SURFACE,
           linewidth=1.6, label="break-adjusted clock (dead time removed)")
    for xi, n in zip(x, null):
        ax.plot([xi - .45, xi + .45], [n, n], color=INK, linewidth=2.0,
                linestyle=(0, (5, 2.5)), zorder=5)
    ax.plot([], [], color=INK, linewidth=2.0, linestyle=(0, (5, 2.5)),
            label="matched ordinary minutes (null)")

    # Labels sit INSIDE the bars: the null rules cross the tops and would collide.
    for xi, d, a in zip(x, disp, adj):
        ax.text(xi - .21, d - .028, f"{d:.3f}", ha="center", va="top",
                fontsize=10.5, fontweight="bold", color="white")
        ax.text(xi + .21, a - .028, f"{a:.3f}", ha="center", va="top",
                fontsize=10.5, fontweight="bold", color="white")
    ax.set_xticks(x, [f"{w}-minute window" for w in ws], fontsize=10)
    ax.set_ylabel("P(at least one shot)")
    ax.set_ylim(0, 1.02)
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, fontsize=9, ncols=3, loc="lower left",
              bbox_to_anchor=(0, 1.01), handlelength=1.8, columnspacing=1.4)
    _finish(fig, ax,
            "The post-break shot drought is mostly stopped time counted as football",
            "Measured from the break call, the window contains ~3 minutes in which no shot is "
            "possible. Remove only\nthe hydration dead time and the probability sits at or "
            "above the matched-control benchmark at every window.",
            "Source: reports/tables/placebo_results.md · matched pseudo-break design, "
            "10,000 draws")
    fig.tight_layout(rect=(0, 0.04, 1, 0.83))
    fig.savefig(FIGURES / "art_clock.png")
    plt.close(fig)


# ------------------------------------------------------------- 2. Test A forest
def fig_test_a(f):
    t = f["test_a"]
    keys = [("primary", "PRIMARY — all breaks\nwith a clean control"),
            ("min3", "≥3 control minutes"),
            ("min5", "≥5 control minutes"),
            ("min10", "≥10 control minutes")]
    labels = [f"{lbl}\n{t[k]['breaks']} breaks · {t[k]['matches']} matches" for k, lbl in keys]
    est = [t[k]["effect"] for k, _ in keys]
    lo = [t[k]["ci"][0] for k, _ in keys]
    hi = [t[k]["ci"][1] for k, _ in keys]
    colors = [CRITICAL if t[k]["excludes_zero"] else BLUE for k, _ in keys]

    fig, ax = plt.subplots(figsize=(W_IN, H_IN + 0.5), dpi=DPI)
    _forest(ax, labels, est, lo, hi, colors,
            "effect on shot-balance disruption (shots) — negative = less disruption than controls")
    _finish(fig, ax,
            "No detectable average effect — but not stable under the strictest control filter",
            "Each break is compared with its own matched ordinary minutes; intervals are "
            "clustered by match.\nDemanding deeper control support drives the estimate away "
            "from zero, on a small and heavily selected sample.",
            "Source: reports/tables/robustness.md · red = interval excludes zero")
    fig.tight_layout(rect=(0, 0.04, 1, 0.84))
    fig.savefig(FIGURES / "art_test_a_forest.png")
    plt.close(fig)


# ------------------------------------------------------------- 3. Test B forest
def fig_test_b(f):
    t = f["test_b"]
    ws = [5, 8, 10]
    labels = [f"{w}-minute window\n{t[f'w{w}']['breaks']} breaks · "
              f"{t[f'w{w}']['matches']} matches" for w in ws]
    est = [t[f"w{w}"]["D"] for w in ws]
    lo = [t[f"w{w}"]["ci"][0] for w in ws]
    hi = [t[f"w{w}"]["ci"][1] for w in ws]
    colors = [CRITICAL if t[f"w{w}"]["excludes_zero"] else BLUE for w in ws]

    fig, ax = plt.subplots(figsize=(W_IN, H_IN - 0.4), dpi=DPI)
    _forest(ax, labels, est, lo, hi, colors,
            "extra advantage lost after a break, vs comparable uninterrupted spells (shots)")
    _finish(fig, ax,
            "The attacking team did lose its edge — but no more than usual",
            "The side leading the pre-break window is fixed from pre-break information only, "
            "then matched to ordinary\nspells with the same starting advantage. Every interval "
            "spans zero.",
            "Source: reports/tables/test_b.md · coverage falls sharply at the widest window")
    fig.tight_layout(rect=(0, 0.05, 1, 0.83))
    fig.savefig(FIGURES / "art_test_b_forest.png")
    plt.close(fig)


# --------------------------------------------------- 4. regression to the mean
def fig_regression(f):
    t = f["test_b"]
    ws = [5, 8, 10]
    x = np.arange(len(ws))
    real = [t[f"w{w}"]["swing_real"] for w in ws]
    ctrl = [t[f"w{w}"]["swing_control"] for w in ws]

    fig, ax = plt.subplots(figsize=(W_IN, H_IN), dpi=DPI)
    ax.axhline(0, color=INK, linewidth=1.3)
    ax.bar(x - 0.21, real, width=0.40, color=CRITICAL, edgecolor=SURFACE,
           linewidth=1.6, label="after a real hydration break")
    ax.bar(x + 0.21, ctrl, width=0.40, color=MUTED, edgecolor=SURFACE,
           linewidth=1.6, label="after a comparable uninterrupted spell")
    for xi, r, c in zip(x, real, ctrl):
        ax.text(xi - .21, r - .06, f"{r:+.2f}", ha="center", va="top",
                fontsize=9.6, color=INK)
        ax.text(xi + .21, c - .06, f"{c:+.2f}", ha="center", va="top",
                fontsize=9.6, color=INK)
    ax.set_xticks(x, [f"{w}-minute window" for w in ws], fontsize=10)
    ax.set_ylabel("change in the attacking side's shot advantage")
    ax.set_ylim(min(min(real), min(ctrl)) * 1.35, 0.22)
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, fontsize=9.4, loc="lower left")
    _finish(fig, ax,
            "Dominant teams give the advantage back whether or not you stop the game",
            "This is regression to the mean, and it is what an unmatched analysis mistakes for "
            "a break effect.\nThe collapse supporters remember is real — it also happens when "
            "nobody blows the whistle.",
            "Source: reports/tables/test_b.md")
    fig.tight_layout(rect=(0, 0.04, 1, 0.86))
    fig.savefig(FIGURES / "art_regression.png")
    plt.close(fig)


# ------------------------------------------------------------- 5. perception
def fig_perception(f):
    p = f["perception"]
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(W_IN, H_IN - 0.2), dpi=DPI,
                                   gridspec_kw={"width_ratios": [1.15, 1]})

    # left: the denominator
    n, k = p["sweep_n"], p["sweep_with_claims"]
    cols = 8
    for i in range(n):
        r, c = divmod(i, cols)
        ax1.add_patch(plt.Rectangle((c, -r), 0.82, 0.82,
                                    color=CRITICAL if i < k else GRID,
                                    ec=SURFACE, lw=1.1))
    ax1.set_xlim(-0.4, cols + 0.4)
    ax1.set_ylim(-(n // cols) - 0.5, 1.5)
    ax1.set_aspect("equal")
    ax1.axis("off")
    ax1.set_title(f"Breaks that attracted any public claim\n"
                  f"{k} of {n} randomly sampled ({p['sweep_pct']}%)",
                  fontsize=10.5, color=INK, loc="left", pad=8)

    # right: the hit rate
    sup, tot = p["unique_supported"], p["unique_total"]
    ax2.barh([1], [sup], color=GREEN, edgecolor=SURFACE, lw=1.5, height=.30)
    ax2.barh([1], [tot - sup], left=[sup], color=GRID, edgecolor=SURFACE, lw=1.5, height=.30)
    ax2.text(sup / 2, 1, f"{sup} supported", ha="center", va="center",
             color="white", fontsize=10, fontweight="bold")
    ax2.text(sup + (tot - sup) / 2, 1, f"{tot - sup} not", ha="center", va="center",
             color=INK2, fontsize=10)
    ax2.set_xlim(0, tot)
    ax2.set_ylim(0.4, 1.6)
    ax2.axis("off")
    ax2.set_title(f"When a claim WAS made, was it right?\n"
                  f"{sup} of {tot} unique claimed breaks supported "
                  f"({p['unique_pct']}%)",
                  fontsize=10.5, color=INK, loc="left", pad=8)

    fig.suptitle("The public argument was a sampling problem, not a perception problem",
                 x=0.045, y=0.975, ha="left", fontsize=13.5, fontweight="bold", color=INK)
    fig.text(0.045, 0.885,
             "Pundits were right about half the time. They were also describing roughly one "
             "break in twelve.",
             ha="left", va="top", fontsize=9.6, color=INK2)
    fig.text(0.045, 0.028,
             f"Source: reports/tables/perception.md · sweep 95% CI "
             f"{p['sweep_ci'][0]}–{p['sweep_ci'][1]}%", fontsize=8.2, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 0.85))
    fig.savefig(FIGURES / "art_perception.png")
    plt.close(fig)


# ------------------------------------------------------------- 6. the goal trap
def fig_goals_trap(f):
    c = f["cards"]
    fig, ax = plt.subplots(figsize=(W_IN - 1.2, H_IN - 0.6), dpi=DPI)
    vals = [c["goals_real_w8"], c["goals_control_w8"]]
    ax.bar([0, 1], vals, width=0.5, color=[CRITICAL, GRID],
           edgecolor=SURFACE, linewidth=1.6)
    for xi, v in zip([0, 1], vals):
        ax.text(xi, v + .006, f"{v:.3f}", ha="center", fontsize=11,
                fontweight="bold", color=INK)
    ax.set_xticks([0, 1], ["real break windows", "matched control windows"], fontsize=10)
    ax.set_ylabel("goals per 8-minute window")
    ax.set_ylim(0, max(vals) * 1.25)
    ax.grid(axis="x", visible=False)
    ax.annotate(f"{vals[0] / vals[1]:.1f}× — and entirely an artifact",
                xy=(0.5, max(vals) * 1.06), ha="center", fontsize=10.5,
                color=CRITICAL, fontweight="bold")
    _finish(fig, ax,
            "The false positive we nearly published",
            "Control minutes are screened to sit away from goals BY DESIGN, so a goal-based "
            "outcome compares\nbreak windows against deliberately goal-free controls. The gap "
            "is the screen, not the breaks.",
            "Source: reports/tables/cards.md")
    fig.tight_layout(rect=(0, 0.04, 1, 0.85))
    fig.savefig(FIGURES / "art_goals_trap.png")
    plt.close(fig)


def main():
    f = _facts()
    for fn in (fig_clock, fig_test_a, fig_test_b, fig_regression,
               fig_perception, fig_goals_trap):
        fn(f)
        print(f"wrote {fn.__name__}")
    print(f"6 article figures -> {FIGURES}")


if __name__ == "__main__":
    main()
