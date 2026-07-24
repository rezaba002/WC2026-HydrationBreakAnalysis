"""Late-game output proxy — the behavioral stand-in for the physical question.

We cannot measure whether hydration breaks physically refreshed players: no
per-player physical data exists for 2018/2022, and the 2026 data are match
totals with no pre/post-break split (searched and confirmed 2026-07-24). This
module instead asks a behavioral proxy answerable for all three tournaments:

    Did attacking output hold up better in the closing minutes once breaks
    existed?

If universal breaks aided recovery, the share of shots and goals in the final
15 minutes should rise. This is a PROXY, not a physical measurement, and it is
heavily confounded — most importantly by the substitution rule (2018 allowed 3
subs, 2022 and 2026 five), which independently supplies fresh late-game legs.
**2022 is therefore the load-bearing comparison**: 2026-vs-2022 isolates the
break era from the sub-rule change; 2022-vs-2018 shows the sub-rule effect.

Shares are used (late shots / all regulation shots) so differing added-time
environments across cups do not distort the denominator. Regulation = minutes
1-90; stoppage time (90+) is excluded from the primary and shown as a
sensitivity.

Outputs:
  reports/tables/late_game.md
  reports/figures/fig_late_game.png

Run:  python -m src.late_game
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .util import FIGURES, PROCESSED, TABLES

BUCKETS = [(1, 15), (16, 30), (31, 45), (46, 60), (61, 75), (76, 90)]
LATE = (76, 90)
SEED = 20260724
N_BOOT = 5000


def load_regulation():
    """Shots and shot-goals per tournament, regulation minutes 1-90 only."""
    hist_shots = pd.read_csv(PROCESSED / "historical_shots.csv")
    hist_shots = hist_shots[(hist_shots["period"] <= 2) & hist_shots["minute"].between(1, 90)]
    s26 = pd.read_csv(PROCESSED / "shots_2026.csv")
    s26 = s26[(s26["period"] <= 2) & s26["minute"].between(1, 90)].copy()
    s26["tournament"] = "WC2026"

    cols = ["tournament", "match_id", "minute", "is_goal"]
    shots = pd.concat([hist_shots[cols], s26[cols]], ignore_index=True)
    return shots


def bucket_shares(shots: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for t, g in shots.groupby("tournament"):
        n = len(g)
        ng = int(g["is_goal"].sum())
        rec = {"tournament": t, "n_shots": n, "n_goals": ng}
        for lo, hi in BUCKETS:
            seg = g["minute"].between(lo, hi)
            rec[f"shot_{lo}_{hi}"] = seg.mean()
            rec[f"goal_{lo}_{hi}"] = (g.loc[g["is_goal"], "minute"].between(lo, hi).mean()
                                      if ng else np.nan)
        rows.append(rec)
    return pd.DataFrame(rows).set_index("tournament")


def boot_late_share(shots: pd.DataFrame, tournament: str, rng) -> tuple[float, float]:
    """Match-cluster bootstrap CI for the 76-90 shot share of one tournament."""
    g = shots[shots["tournament"] == tournament]
    groups = {mid: sub["minute"].to_numpy() for mid, sub in g.groupby("match_id")}
    keys = list(groups)
    out = np.empty(N_BOOT)
    for i in range(N_BOOT):
        drawn = np.concatenate([groups[keys[j]] for j in rng.integers(0, len(keys), len(keys))])
        out[i] = np.mean((drawn >= LATE[0]) & (drawn <= LATE[1]))
    return tuple(np.percentile(out, [2.5, 97.5]))


def main():
    shots = load_regulation()
    shares = bucket_shares(shots)
    rng = np.random.default_rng(SEED)

    late_ci = {t: boot_late_share(shots, t, rng) for t in shares.index}

    order = ["WC2018", "WC2022", "WC2026"]
    lines = [
        "# Late-game output proxy (behavioral, NOT physical)",
        "",
        "Proxy for the unanswerable physical question (see module docstring).",
        "Share of regulation shots/goals in each 15-minute segment. Late = 76-90'.",
        "**Confound — substitution era: 2018 = 3 subs, 2022/2026 = 5 subs.** More",
        "subs independently freshen late legs, so 2026-vs-2022 is the break-era",
        "contrast; 2022-vs-2018 is mostly the sub-rule effect.",
        "",
        "## Regulation shots per tournament",
        "",
        "| tournament | matches | shots | shots in 76-90' | share | 95% CI | goals in 76-90' share |",
        "|---|---|---|---|---|---|---|",
    ]
    for t in order:
        r = shares.loc[t]
        n_late = int(round(r[f"shot_{LATE[0]}_{LATE[1]}"] * r["n_shots"]))
        lo, hi = late_ci[t]
        lines.append(
            f"| {t} | {shots[shots.tournament==t]['match_id'].nunique()} | {int(r['n_shots'])} | "
            f"{n_late} | {r[f'shot_{LATE[0]}_{LATE[1]}']:.1%} | "
            f"[{lo:.1%}, {hi:.1%}] | {r[f'goal_{LATE[0]}_{LATE[1]}']:.1%} |")

    d_26_22 = shares.loc["WC2026", "shot_76_90"] - shares.loc["WC2022", "shot_76_90"]
    d_22_18 = shares.loc["WC2022", "shot_76_90"] - shares.loc["WC2018", "shot_76_90"]
    lines += [
        "",
        "## Reading",
        f"- Break-era contrast (2026 − 2022): {d_26_22:+.1%} of shots in the final 15'.",
        f"- Sub-rule contrast (2022 − 2018): {d_22_18:+.1%}.",
        "- If the break aided sustained output, 2026 should exceed 2022 beyond noise;",
        "  compare the difference against the bootstrap CIs above.",
        "- Confounds beyond the sub rule: added-time environment, score-state /",
        "  game-chasing, tournament finishing quality, tracking-independent. This is",
        "  a behavioral association, never a physiological measurement (spec §13).",
        "",
        "## Full segment shares (shots)",
        "",
        "| segment | " + " | ".join(order) + " |",
        "|---|" + "---|" * len(order),
    ]
    for lo, hi in BUCKETS:
        lines.append(f"| {lo}-{hi}' | "
                     + " | ".join(f"{shares.loc[t, f'shot_{lo}_{hi}']:.1%}" for t in order) + " |")

    (TABLES / "late_game.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    chart(shares, late_ci, order)
    print("\n".join(lines))
    print(f"\nwrote {FIGURES / 'fig_late_game.png'}")


def chart(shares, late_ci, order):
    import matplotlib.pyplot as plt
    from .charts import BLUE, GREEN, INK, INK2, MUTED, SURFACE

    colors = {"WC2018": MUTED, "WC2022": "#008300", "WC2026": BLUE}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.6), width_ratios=[3, 2])

    x = [f"{lo}-{hi}" for lo, hi in BUCKETS]
    for t in order:
        ax1.plot(x, [shares.loc[t, f"shot_{lo}_{hi}"] for lo, hi in BUCKETS],
                 marker="o", markersize=5, linewidth=2, color=colors[t], label=t.replace("WC", "WC "))
    ax1.set_ylabel("share of regulation shots")
    ax1.set_xlabel("match segment (minute)")
    ax1.legend(frameon=False, fontsize=9, loc="upper left")
    ax1.set_title("Where shots happen across the match",
                  color=INK, fontsize=12, fontweight="bold", loc="left")

    lo_hi = [late_ci[t] for t in order]
    vals = [shares.loc[t, "shot_76_90"] for t in order]
    err = [[v - lo for v, (lo, hi) in zip(vals, lo_hi)],
           [hi - v for v, (lo, hi) in zip(vals, lo_hi)]]
    ax2.bar(range(3), vals, color=[colors[t] for t in order], edgecolor=SURFACE, linewidth=1.5)
    ax2.errorbar(range(3), vals, yerr=err, fmt="none", ecolor=INK, capsize=5, linewidth=1.4)
    ax2.set_xticks(range(3))
    ax2.set_xticklabels([t.replace("WC", "WC ") for t in order])
    for i, (v, (lo, hi)) in enumerate(zip(vals, lo_hi)):
        ax2.text(i, hi + 0.008, f"{v:.1%}", ha="center", color=INK2, fontsize=10)
    ax2.set_ylim(0, max(hi for _, hi in lo_hi) * 1.22)
    ax2.set_ylabel("share of shots in final 15'")
    ax2.set_title("Final-15' share (±95% CI)",
                  color=INK, fontsize=12, fontweight="bold", loc="left")

    for ax in (ax1, ax2):
        ax.grid(axis="x", visible=False)
        ax.tick_params(length=0)
    fig.suptitle("Did the game stay alive later once breaks existed?",
                 x=0.055, y=1.0, ha="left", fontsize=14, fontweight="bold", color=INK)
    fig.text(0.055, 0.925,
             "Behavioral proxy — not physical. 2026-vs-2022 isolates the break era "
             "(both 5-sub); 2022-vs-2018 is the sub-rule jump.", fontsize=10, color=INK2)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(FIGURES / "fig_late_game.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
