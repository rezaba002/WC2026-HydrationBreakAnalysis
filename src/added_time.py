"""Core Output 6 — added time and match duration, 2018 / 2022 / 2026.

The handoff's question: the ~6 mandated break minutes sit INSIDE the 2026
match clock, so did the boards grow BEYOND that (breaks stacked on other
stoppages), or were breaks absorbed into the stoppage environment 2022 already
reached?

Data reality (documented, not worked around):
  - 2018 / 2022: EXACT half-end minutes from StatsBomb "Half End" events
    (historical_match_times.csv). Added time = half_end − nominal.
  - 2026: no exact board minutes exist in our auditable sources, and the FIFA
    event feed strips stoppage (+X) notation (only 7/104 matches keep it). The
    reliable signal is PMSR shot minutes, giving a LOWER BOUND on how deep into
    stoppage play reached (last shot ≤ final whistle). 2026 duration is
    therefore reported as a floor and never as an exact board figure.
  - Goals at minute ≥ 90 (final-minute-and-stoppage) use base goal minutes,
    comparable across all three.

Outputs:
  reports/tables/added_time.md
  reports/figures/fig_added_time.png

Run:  python -m src.added_time
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from .util import FIFA, FIGURES, PROCESSED, TABLES


def base_minute(m) -> int:
    return int(re.match(r"(\d+)", str(m)).group(1))


def historical_added():
    t = pd.read_csv(PROCESSED / "historical_match_times.csv")
    t = t.copy()
    t["h1_added"] = t["h1_end_minute"] - 45
    t["h2_added"] = t["h2_end_minute"] - 90
    return t


def goals_ge90_share():
    """Share of regulation goals scored at minute >= 90, per tournament."""
    out = {}
    hist = pd.read_csv(PROCESSED / "historical_goals.csv")
    hist = hist[hist["period"] <= 2]
    for t, g in hist.groupby("tournament"):
        out[t] = (g["minute"] >= 90).mean()
    ev = pd.read_csv(FIFA / "match_events.csv", encoding="utf-8-sig")
    goals = ev[ev["event_type"] == "Goal"].copy()
    goals["b"] = goals["minute"].map(base_minute)
    goals = goals[goals["b"] <= 120]
    reg = goals[goals["b"] <= 100]  # exclude extra-time goals from the rate
    out["WC2026"] = (reg["b"] >= 90).mean()
    return out


def wc2026_duration_floor():
    """Per-match lower bound on H2 end = max regulation shot minute."""
    s = pd.read_csv(PROCESSED / "shots_2026.csv")
    reg = s[s["minute"] <= 100]  # drop extra-time shots
    return reg.groupby("match_id")["minute"].max()


def main():
    hist = historical_added()
    reg = hist[~hist["went_to_extra_time"]]  # compare regulation matches
    floor26 = wc2026_duration_floor()
    ge90 = goals_ge90_share()

    rows = []
    for t in ("WC2018", "WC2022"):
        g = reg[reg["tournament"] == t]
        rows.append({"tournament": t, "kind": "exact half-end",
                     "n": len(g),
                     "h1_added": g["h1_added"].mean(),
                     "h2_added": g["h2_added"].mean(),
                     "h2_end": g["h2_end_minute"].mean()})
    rows.append({"tournament": "WC2026", "kind": "shot-minute floor (lower bound)",
                 "n": int(floor26.shape[0]),
                 "h1_added": np.nan,
                 "h2_added": floor26.median() - 90,
                 "h2_end": floor26.mean()})
    tab = pd.DataFrame(rows)

    lines = [
        "# Added time and match duration — Core Output 6",
        "",
        "## Second-half length",
        "",
        "| tournament | source | matches | mean H1 added | mean H2 added | mean H2 end |",
        "|---|---|---|---|---|---|",
    ]
    for _, r in tab.iterrows():
        h1 = "n/a" if pd.isna(r["h1_added"]) else f"{r['h1_added']:+.1f}'"
        lines.append(f"| {r['tournament']} | {r['kind']} | {int(r['n'])} | {h1} | "
                     f"{r['h2_added']:+.1f}' | {r['h2_end']:.1f}' |")

    e18, e22 = tab.loc[0, "h2_end"], tab.loc[1, "h2_end"]
    floor_end = tab.loc[2, "h2_end"]
    lines += [
        "",
        "## Reading",
        f"- The rigorous comparison is 2018 vs 2022 (both exact): Qatar 2022 was the",
        f"  added-time anomaly the handoff flagged — second halves ran to **{e22:.1f}'**",
        f"  on average (+{e22-90:.1f}), vs **{e18:.1f}'** (+{e18-90:.1f}) in 2018.",
        "- 2026 adds ~3 min per half **by rule** for the two breaks (they sit inside the",
        "  clock), so 2026 matches are structurally longer than a no-break tournament.",
        f"- We CANNOT determine whether 2026's boards exceeded the anomalous 2022",
        f"  environment: exact 2026 board minutes are absent from every auditable source",
        "  (the FIFA feed strips +X notation, 7/104 matches). The last-shot floor shows",
        f"  2026 second halves ran to **at least {floor_end:.1f}'** on average — the true",
        "  whistle is later still — which only confirms they ran deep into stoppage, not",
        "  whether they beat 2022. Reported as a floor, never as a board figure.",
        "",
        "## Late scoring (goals at minute ≥ 90, regulation)",
        "",
        "| tournament | share of goals at ≥90' |",
        "|---|---|",
    ]
    for t in ("WC2018", "WC2022", "WC2026"):
        lines.append(f"| {t} | {ge90[t]:.1%} |")
    lines += [
        "",
        f"No monotonic trend: 2018 {ge90['WC2018']:.1%}, 2022 {ge90['WC2022']:.1%} "
        f"(lowest, despite the longest added time), 2026 {ge90['WC2026']:.1%} (highest).",
        "The differences are small and confounded (added time, 5-sub legs, finishing);",
        "there is no clean 'breaks produced more late goals' signal.",
    ]

    (TABLES / "added_time.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    chart(tab, floor26, reg)
    print("\n".join(lines))
    print(f"\nwrote {FIGURES / 'fig_added_time.png'}")


def chart(tab, floor26, reg):
    import matplotlib.pyplot as plt
    from .charts import BLUE, INK, INK2, MUTED, SURFACE

    colors = {"WC2018": MUTED, "WC2022": "#008300", "WC2026": BLUE}
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.6), width_ratios=[2, 3])

    # Left: the rigorous exact comparison, 2018 vs 2022 only.
    exact = ["WC2018", "WC2022"]
    ends = [tab.loc[tab.tournament == t, "h2_end"].iloc[0] for t in exact]
    ax1.bar(range(2), [e - 90 for e in ends],
            color=[colors[t] for t in exact], edgecolor=SURFACE, linewidth=1.5)
    ax1.axhline(0, color="#c3c2b7", linewidth=1)
    ax1.set_xticks(range(2))
    ax1.set_xticklabels(["WC 2018", "WC 2022"])
    for i, e in enumerate(ends):
        ax1.text(i, e - 90 + 0.15, f"+{e-90:.1f}'", ha="center", color=INK2, fontsize=10)
    ax1.axhline(6, color=BLUE, linestyle=(0, (4, 2)), linewidth=1.6)
    ax1.text(-0.35, 6.2, "2026: +~6' mandated by rule\n(exact board total unmeasurable)",
             color=BLUE, fontsize=8.5, ha="left", va="bottom")
    ax1.set_ylim(0, 8.4)
    ax1.set_ylabel("mean second-half added time (min)")
    ax1.set_title("2022 already stretched the clock",
                  color=INK, fontsize=12, fontweight="bold", loc="left")

    # distribution of 2026 H2-end floor vs 2018/2022 exact ends
    ax2.hist(reg[reg.tournament == "WC2018"]["h2_end_minute"], bins=range(90, 106),
             color=MUTED, alpha=0.7, label="WC 2018 exact", edgecolor=SURFACE)
    ax2.hist(reg[reg.tournament == "WC2022"]["h2_end_minute"], bins=range(90, 106),
             color="#008300", alpha=0.6, label="WC 2022 exact", edgecolor=SURFACE)
    ax2.hist(floor26, bins=range(90, 106), color=BLUE, alpha=0.55,
             label="WC 2026 floor (last shot)", edgecolor=SURFACE)
    ax2.set_xlabel("second-half end minute")
    ax2.set_ylabel("matches")
    ax2.legend(frameon=False, fontsize=8.5, loc="upper right")
    ax2.set_title("How late the second half ran",
                  color=INK, fontsize=12, fontweight="bold", loc="left")

    for ax in (ax1, ax2):
        ax.grid(axis="x", visible=False)
        ax.tick_params(length=0)
    fig.suptitle("Did hydration breaks make matches even longer?",
                 x=0.055, y=1.0, ha="left", fontsize=14, fontweight="bold", color=INK)
    fig.text(0.055, 0.925,
             "2018/2022 exact half-ends (StatsBomb); 2026 is a last-shot lower bound "
             "(exact board minutes unavailable).", fontsize=10, color=INK2)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(FIGURES / "fig_added_time.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
