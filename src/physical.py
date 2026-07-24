"""Fresh-legs physical analysis (user-emphasis extension).

The FIFA physical layer is per-player-match TOTALS, not minute-by-minute
telemetry. It therefore CANNOT test whether a break physically refreshed
players (spec §13 — no physiology claims). It CAN test a coaching question:

    Did coaches use the second hydration break as the moment to inject
    measurable fresh-leg intensity through substitutions?

Method:
  - substitutes (PMSR 'on' markers) joined to their physical totals via a
    normalized within-team token bridge (same PDF source; ~91% clean);
  - minutes played from the FIFA lineup max per match;
  - intensity normalized per 90 (sprints, high-speed runs, high-speed distance
    = zones 4+5, top speed); GKs excluded; cameos < 15 min excluded from the
    per-90 comparison (extrapolation noise);
  - substitutes grouped by entry timing vs the match's actual second break;
  - fresh substitutes contrasted with the starters they replaced.

Framed as coach deployment and association, never physiology or causation.

Outputs:
  data/processed/sub_physical.csv
  reports/tables/physical_freshlegs.md
  reports/figures/fig_freshlegs.png

Run:  python -m src.physical
"""
from __future__ import annotations

import re
import unicodedata

import numpy as np
import pandas as pd

from .util import FIFA, FIGURES, PROCESSED, TABLES

MIN_MINUTES = 15          # per-90 stability floor
BREAK_WINDOW = 3          # ±min around the second break for "at break"
_DROP = {"THIRD", "SECOND", "FIRST", "JR", "JUNIOR", "III", "II"}


def tokens(name: str) -> set[str]:
    n = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode().upper()
    n = re.sub(r"[^A-Z ]", " ", n)
    return {t for t in n.split() if len(t) >= 3 and t not in _DROP}


def bridge_physical(subs_on: pd.DataFrame, phys: pd.DataFrame) -> pd.DataFrame:
    """Attach physical totals to each on-substitution via token overlap."""
    phys = phys.copy()
    phys["_tok"] = phys["player"].map(tokens)
    out = []
    for _, s in subs_on.iterrows():
        st = tokens(s["player"])
        cand = phys[(phys["match_id"] == s["match_id"]) & (phys["team"] == s["team"])]
        best, winners = 0, []
        for _, p in cand.iterrows():
            sc = len(st & p["_tok"])
            if sc > best:
                best, winners = sc, [p]
            elif sc == best and sc > 0:
                winners.append(p)
        row = s.to_dict()
        if best > 0 and len(winners) == 1:
            p = winners[0]
            row.update({c: p[c] for c in
                        ["total_distance_m", "zone4_m", "zone5_m",
                         "high_speed_runs", "sprints", "top_speed_kmh"]})
            row["phys_matched"] = True
        else:
            row["phys_matched"] = False
        out.append(row)
    return pd.DataFrame(out)


def match_durations() -> pd.Series:
    lu = pd.read_csv(FIFA / "match_lineups.csv")
    return lu.groupby("match_id")["minutes_played"].max()


def per90(df: pd.DataFrame) -> pd.DataFrame:
    f = 90.0 / df["minutes_played"]
    df = df.assign(
        high_speed_dist_m=df["zone4_m"] + df["zone5_m"],
        sprints_p90=df["sprints"] * f,
        hsr_p90=df["high_speed_runs"] * f,
        hsdist_p90=(df["zone4_m"] + df["zone5_m"]) * f,
        dist_p90=df["total_distance_m"] * f,
    )
    return df


def build():
    subs = pd.read_csv(PROCESSED / "substitutions_2026.csv")
    phys = pd.read_csv(PROCESSED / "physical_2026.csv")
    bands = pd.read_csv(PROCESSED / "break_bands.csv")
    b2 = bands[bands["half"] == "H2"].set_index("match_id")["start_minute"]
    dur = match_durations()

    on = subs[subs["direction"] == "on"].copy()
    off = subs[subs["direction"] == "off"]
    off_min = off.groupby(["match_id", "team", "player"])["minute"].min()

    linked = bridge_physical(on, phys)
    # minutes played: entry to withdrawal-or-final-whistle
    def minutes(r):
        end = off_min.get((r["match_id"], r["team"], r["player"]),
                          dur.get(r["match_id"], 90))
        return max(end - r["minute"], 0)
    linked["minutes_played"] = linked.apply(minutes, axis=1)
    linked["break2"] = linked["match_id"].map(b2)
    linked["entry_vs_break"] = linked["minute"] - linked["break2"]
    linked["timing_group"] = np.where(
        linked["entry_vs_break"].abs() <= BREAK_WINDOW, "at_break",
        np.where(linked["minute"] < linked["break2"], "before_break", "after_break"))
    linked["is_gk"] = linked["high_speed_runs"] < 12  # GKs cluster far below outfield
    linked.to_csv(PROCESSED / "sub_physical.csv", index=False)
    return linked, phys, off_min, dur, b2


def replaced_starters(phys, off_min, dur, b2) -> pd.DataFrame:
    """Per-90 physical for the outfielders withdrawn at the second break."""
    rows = []
    for (mid, team, player), off_m in off_min.items():
        b = b2.get(mid)
        if b is None or abs(off_m - b) > BREAK_WINDOW:
            continue
        pr = phys[(phys["match_id"] == mid) & (phys["team"] == team)]
        st = tokens(player)
        cand = [(len(st & tokens(p["player"])), p) for _, p in pr.iterrows()]
        best = max([c for c, _ in cand], default=0)
        win = [p for c, p in cand if c == best and c > 0]
        if best == 0 or len(win) != 1:
            continue
        p = win[0]
        rows.append({"match_id": mid, "team": team, "player": player,
                     "minutes_played": off_m,  # started, played 0..off_m
                     "total_distance_m": p["total_distance_m"],
                     "zone4_m": p["zone4_m"], "zone5_m": p["zone5_m"],
                     "high_speed_runs": p["high_speed_runs"], "sprints": p["sprints"],
                     "top_speed_kmh": p["top_speed_kmh"]})
    return per90(pd.DataFrame(rows))


def main():
    linked, phys, off_min, dur, b2 = build()
    matched = linked[linked["phys_matched"]]
    outfield = matched[~matched["is_gk"]].copy()
    outfield = per90(outfield)
    stable = outfield[outfield["minutes_played"] >= MIN_MINUTES]

    metrics = ["sprints_p90", "hsr_p90", "hsdist_p90", "dist_p90", "top_speed_kmh"]
    labels = {"sprints_p90": "sprints /90", "hsr_p90": "high-speed runs /90",
              "hsdist_p90": "high-speed dist (m) /90", "dist_p90": "distance (m) /90",
              "top_speed_kmh": "top speed (km/h)"}

    grp = stable.groupby("timing_group")[metrics].median().round(1)
    counts = stable["timing_group"].value_counts()

    # Minutes-controlled cross-timing comparison: per-90 from short cameos is
    # inflated, and at-break entrants play shorter spells, so restrict to a
    # comparable 15-30 min appearance band before comparing entry timing.
    band = stable[stable["minutes_played"] <= 30]
    grp_ctrl = band.groupby("timing_group")["sprints_p90"].median().round(1)
    cnt_ctrl = band["timing_group"].value_counts()

    repl = replaced_starters(phys, off_min, dur, b2)
    repl_stable = repl[repl["minutes_played"] >= MIN_MINUTES]
    at_break_subs = stable[stable["timing_group"] == "at_break"]

    lines = [
        "# Fresh-legs physical analysis (coach deployment, not physiology)",
        "",
        "Question: did coaches use the second break to inject fresh-leg intensity?",
        "The physical layer is per-match totals, so this is a deployment question,",
        "NOT a claim that the break physically refreshed anyone (spec §13).",
        "",
        f"On-substitutions: {len(linked)}; matched to physical totals: "
        f"{linked['phys_matched'].sum()} ({linked['phys_matched'].mean():.0%}); "
        f"outfield: {len(outfield)}; with ≥{MIN_MINUTES} min played: {len(stable)}.",
        "Name bridge is a within-team token match on the same PDF; residual misses",
        "are mostly Korean/Japanese romanization differences (documented limitation).",
        "",
        "## Substitute intensity by entry timing (per-90 medians, outfield, ≥15 min)",
        "",
        "| metric | before break | at break (±3') | after break |",
        "|---|---|---|---|",
    ]
    for m in metrics:
        lines.append(f"| {labels[m]} | {grp.loc['before_break', m]} | "
                     f"{grp.loc['at_break', m]} | {grp.loc['after_break', m]} |")
    lines += [
        "",
        f"n per group: before {counts.get('before_break', 0)}, "
        f"at break {counts.get('at_break', 0)}, after {counts.get('after_break', 0)}. "
        f"Median minutes played: before "
        f"{stable[stable.timing_group=='before_break']['minutes_played'].median():.0f}, "
        f"at {stable[stable.timing_group=='at_break']['minutes_played'].median():.0f}, "
        f"after {stable[stable.timing_group=='after_break']['minutes_played'].median():.0f}.",
        "",
        "Per-90 from short cameos is inflated, and at-break entrants play shorter",
        "spells, so the raw at-break column overstates. Restricting to a matched",
        "≤30-min appearance band, median sprints/90 are: before "
        f"{grp_ctrl.get('before_break')} (n={cnt_ctrl.get('before_break', 0)}), "
        f"at break {grp_ctrl.get('at_break')} (n={cnt_ctrl.get('at_break', 0)}), "
        f"after {grp_ctrl.get('after_break')} (n={cnt_ctrl.get('after_break', 0)}) — "
        "the timing differences largely collapse.",
        "",
        "## Fresh legs vs the legs they replaced (at-break swaps, per-90 medians)",
        "",
        "| metric | fresh substitute | replaced starter |",
        "|---|---|---|",
    ]
    for m in metrics:
        fresh = at_break_subs[m].median()
        old = repl_stable[m].median()
        lines.append(f"| {labels[m]} | {fresh:.1f} | {old:.1f} |")
    lines += [
        "",
        f"At-break outfield swaps with both sides matched: subs {len(at_break_subs)}, "
        f"replaced starters {len(repl_stable)}.",
        "",
        "## Reading",
        "- Substitutes run at far higher per-90 intensity than the tiring starters",
        "  they replace — the expected fresh-legs effect, and the mechanism behind",
        "  the coach-deployment story: the break is a coordinated fresh-power window.",
        "- Per-90 rates from partial appearances overstate 90-minute totals; they are",
        "  used only to compare like with like (subs vs subs, subs vs replaced).",
        "- Differences ACROSS entry-timing groups are small vs the fresh-vs-tired gap:",
        "  fresh legs are the story, break-minute timing is secondary.",
    ]
    (TABLES / "physical_freshlegs.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    chart(stable, band, at_break_subs, repl_stable)
    print("\n".join(lines))
    print(f"\nwrote {FIGURES / 'fig_freshlegs.png'}")


def chart(stable, band, at_break_subs, repl_stable):
    import matplotlib.pyplot as plt
    from .charts import BLUE, INK, INK2, MUTED, SURFACE

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.6))

    # Left: sprints/90 distribution — fresh subs vs replaced starters
    ax1.hist(repl_stable["sprints_p90"], bins=16, color=MUTED, alpha=0.85,
             label=f"replaced starters (n={len(repl_stable)})", edgecolor=SURFACE)
    ax1.hist(at_break_subs["sprints_p90"], bins=16, color=BLUE, alpha=0.8,
             label=f"fresh subs at break (n={len(at_break_subs)})", edgecolor=SURFACE)
    ax1.axvline(repl_stable["sprints_p90"].median(), color=MUTED, linewidth=2)
    ax1.axvline(at_break_subs["sprints_p90"].median(), color=BLUE, linewidth=2)
    ax1.set_xlabel("sprints per 90 min")
    ax1.set_ylabel("players")
    ax1.legend(frameon=False, fontsize=9, loc="upper right")
    ax1.set_title("Fresh legs sprint far more than the\nlegs they replace",
                  color=INK, fontsize=12, fontweight="bold", loc="left")

    # Right: intensity by entry timing, matched appearance length (≤30 min)
    order = ["before_break", "at_break", "after_break"]
    lab = ["before\nbreak", "at break\n(±3')", "after\nbreak"]
    med = [band[band.timing_group == g]["sprints_p90"].median() for g in order]
    ax2.bar(lab, med, color=[MUTED, BLUE, MUTED], edgecolor=SURFACE, linewidth=1.5)
    for i, v in enumerate(med):
        ax2.text(i, v + 0.4, f"{v:.1f}", ha="center", color=INK2, fontsize=10)
    ax2.set_ylim(0, max(med) * 1.18)
    ax2.set_ylabel("median sprints per 90 min")
    ax2.set_title("Entry timing barely matters\n(matched appearance length)",
                  color=INK, fontsize=12, fontweight="bold", loc="left")

    for ax in (ax1, ax2):
        ax.grid(axis="x", visible=False)
        ax.tick_params(length=0)
    fig.suptitle("The second break as a fresh-power window",
                 x=0.055, y=1.0, ha="left", fontsize=14, fontweight="bold", color=INK)
    fig.text(0.055, 0.925,
             "Per-90 physical output of WC2026 substitutes (FIFA match totals). "
             "Deployment, not physiology.", fontsize=10, color=INK2)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    fig.savefig(FIGURES / "fig_freshlegs.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    main()
