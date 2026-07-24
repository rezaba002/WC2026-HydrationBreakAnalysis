"""Core Output 4 — substitution timing: 2026 vs 2018/2022.

Era adjustment: 2018 allowed 3 subs, 2022/2026 five, so all curves are
distributional SHARES of each tournament's regulation-time substitutions,
never raw counts. Framed as association, not causation (spec §8).

Key statistic: share of 2026 second-half subs landing within ±3' of the
match's OWN actual second-break start, against the minute-matched share the
same windows would have captured in 2018/2022 (which had no breaks).

Outputs:
  data/processed/subs_minute_share.csv
  reports/tables/subs_timing.md
  reports/figures/fig_subs_curve.png

Run:  python -m src.subs
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .placebo import _parse_minute
from .util import FIFA, FIGURES, PROCESSED, TABLES

WINDOW = 3  # ± minutes around the second break


def load():
    s26 = pd.read_csv(PROCESSED / "substitutions_2026.csv")
    s26 = s26[(s26["direction"] == "on") & (s26["minute"] <= 90)].copy()
    # Regulation = periods 1-2. StatsBomb records stoppage subs at 90+X while
    # the 2026 parser rounds them into <=90; clip historical to 90 so the two
    # late-game distributions are comparable.
    hist = pd.read_csv(PROCESSED / "historical_subs.csv")
    hist = hist[hist["period"] <= 2].copy()
    hist["minute"] = hist["minute"].clip(upper=90)
    bands = pd.read_csv(PROCESSED / "break_bands.csv")
    b2 = bands[bands["half"] == "H2"].set_index("match_id")["start_minute"]
    matches = pd.read_csv(PROCESSED / "matches.csv")
    return s26, hist, b2, matches


def minute_shares(s26: pd.DataFrame, hist: pd.DataFrame) -> pd.DataFrame:
    idx = pd.Index(range(1, 91), name="minute")
    out = pd.DataFrame(index=idx)
    for label, df in (("WC2018", hist[hist["tournament"] == "WC2018"]),
                      ("WC2022", hist[hist["tournament"] == "WC2022"]),
                      ("WC2026", s26)):
        counts = df.groupby("minute").size().reindex(idx, fill_value=0)
        out[label] = counts / counts.sum()
    out["hist_mean"] = out[["WC2018", "WC2022"]].mean(axis=1)
    out["diff_2026"] = out["WC2026"] - out["hist_mean"]
    return out


def break_window_stat(s26, hist, b2) -> list[str]:
    """Share of H2 subs within ±3' of the actual break vs minute-matched history."""
    lines = []
    h2_26 = s26[s26["minute"] >= 46]
    hist_h2 = {t: hist[(hist["tournament"] == t) & (hist["minute"] >= 46)]
               for t in ("WC2018", "WC2022")}

    obs_in, obs_tot, exp = 0, 0, {"WC2018": 0.0, "WC2022": 0.0}
    n_matches = 0
    for mid, b in b2.items():
        subs_m = h2_26[h2_26["match_id"] == mid]
        if subs_m.empty:
            continue
        n_matches += 1
        lo, hi = b - WINDOW, b + WINDOW
        obs_in += subs_m["minute"].between(lo, hi).sum()
        obs_tot += len(subs_m)
        for t, hh in hist_h2.items():
            exp[t] += hh["minute"].between(lo, hi).mean() * len(subs_m)

    obs_share = obs_in / obs_tot
    lines.append(f"Matches with a known second break and H2 subs: {n_matches}")
    lines.append(f"2026 H2 subs within ±{WINDOW}' of the own-match break: "
                 f"**{obs_in}/{obs_tot} = {obs_share:.1%}**")
    for t in exp:
        e = exp[t] / obs_tot
        lines.append(f"Minute-matched expectation from {t}: {e:.1%} "
                     f"(excess: {obs_share - e:+.1%}, ratio {obs_share / e:.2f}x)")

    # Exploratory (not preregistered): displacement around the break — deficit
    # while play is stopped, surplus right after the restart.
    bands = pd.read_csv(PROCESSED / "break_bands.csv")
    dur = bands[bands["half"] == "H2"].set_index("match_id")["duration_min"]
    def _window_share(offset_lo, offset_hi, anchor="start"):
        n_in, n_tot, e = 0, 0, {"WC2018": 0.0, "WC2022": 0.0}
        for mid, b in b2.items():
            subs_m = h2_26[h2_26["match_id"] == mid]
            if subs_m.empty:
                continue
            a = b + (dur.get(mid, 3.0) if anchor == "restart" else 0)
            lo, hi = a + offset_lo, a + offset_hi
            n_in += subs_m["minute"].between(lo, hi).sum()
            n_tot += len(subs_m)
            for t, hh in hist_h2.items():
                e[t] += hh["minute"].between(lo, hi).mean() * len(subs_m)
        return n_in / n_tot, {t: v / n_tot for t, v in e.items()}
    pre, pre_e = _window_share(-3, -1)
    post, post_e = _window_share(0, 3, anchor="restart")
    lines.append("")
    lines.append("**Exploratory displacement pattern** (not preregistered, label as such):")
    lines.append(f"- during the 3' before the stoppage: 2026 {pre:.1%} vs "
                 f"hist {pre_e['WC2018']:.1%}/{pre_e['WC2022']:.1%} — deficit")
    lines.append(f"- 3' from the restart: 2026 {post:.1%} vs "
                 f"hist {post_e['WC2018']:.1%}/{post_e['WC2022']:.1%} — surplus")
    return lines


def first_sub_and_state(s26, hist, matches) -> list[str]:
    lines = []
    first26 = s26.groupby(["match_id", "team"])["minute"].min()
    lines.append("First substitution minute (median per team-match): "
                 f"WC2018 {hist[hist['tournament']=='WC2018'].groupby(['match_id','team'])['minute'].min().median():.0f}', "
                 f"WC2022 {hist[hist['tournament']=='WC2022'].groupby(['match_id','team'])['minute'].min().median():.0f}', "
                 f"WC2026 {first26.median():.0f}'")
    per_team = s26.groupby(["match_id", "team"]).size()
    lines.append(f"Regulation subs per team-match: WC2018 "
                 f"{hist[hist['tournament']=='WC2018'].groupby(['match_id','team']).size().mean():.2f}, "
                 f"WC2022 {hist[hist['tournament']=='WC2022'].groupby(['match_id','team']).size().mean():.2f}, "
                 f"WC2026 {per_team.mean():.2f}")

    # score state at sub minute for 2026, from FIFA goal events
    events = pd.read_csv(FIFA / "match_events.csv", encoding="utf-8-sig")
    events["pos"] = events["minute"].map(_parse_minute)
    teams = pd.read_csv(FIFA / "teams.csv", encoding="utf-8-sig")[["team_id", "team_name"]]
    goals = events[events["event_type"] == "Goal"].merge(teams, on="team_id")
    states = []
    for _, r in s26.iterrows():
        g = goals[goals["match_id"] == r["match_id"]]
        f = ((g["team_name"] == r["team"]) & (g["pos"] < r["minute"])).sum()
        a = ((g["team_name"] != r["team"]) & (g["pos"] < r["minute"])).sum()
        states.append("leading" if f > a else ("trailing" if f < a else "level"))
    s26 = s26.assign(score_state=states)
    dist26 = s26["score_state"].value_counts(normalize=True)
    disth = hist.groupby("tournament")["score_state"].value_counts(normalize=True)
    lines.append("Score state at substitution (share): "
                 + "; ".join(f"2026 {k} {v:.0%}" for k, v in dist26.items()))
    for t in ("WC2018", "WC2022"):
        lines.append(f"  {t}: " + "; ".join(f"{k} {v:.0%}" for k, v in disth[t].items()))
    return lines


def chart(shares: pd.DataFrame, b2):
    import matplotlib.pyplot as plt
    from .charts import BLUE, CRITICAL, GRID, INK, INK2, MUTED, SURFACE

    roll = shares[["WC2018", "WC2022", "WC2026", "hist_mean", "diff_2026"]].rolling(
        3, center=True, min_periods=1).mean()
    band_lo, band_hi = b2.quantile(0.1), b2.quantile(0.9)

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11, 6.4), sharex=True, height_ratios=[3, 2])
    for ax in (ax1, ax2):
        ax.axvspan(band_lo, band_hi, color="#f3e8d9", zorder=0)
        ax.axvspan(22, 26, color="#f3e8d9", zorder=0)
        ax.grid(axis="x", visible=False)
        ax.tick_params(length=0)

    ax1.plot(roll.index, roll["WC2018"], color=MUTED, linewidth=1.6, label="WC 2018")
    ax1.plot(roll.index, roll["WC2022"], color="#008300", linewidth=1.6, label="WC 2022")
    ax1.plot(roll.index, roll["WC2026"], color=BLUE, linewidth=2.4, label="WC 2026")
    ax1.set_ylabel("share of tournament subs")
    ax1.legend(frameon=False, loc="upper left", fontsize=9)
    ax1.set_title("The break moved substitutions to the restart — it didn't multiply them",
                  color=INK, fontsize=14, fontweight="bold", loc="left", pad=26)
    ax1.text(0, 1.06, "Share of each tournament's regulation-time substitutions per "
             "minute (3-min rolling). Shaded: hydration-break minutes.",
             transform=ax1.transAxes, fontsize=10, color=INK2)

    colors = [BLUE if v > 0 else MUTED for v in roll["diff_2026"]]
    ax2.bar(roll.index, roll["diff_2026"], width=0.85, color=colors,
            edgecolor=SURFACE, linewidth=0.4)
    ax2.axhline(0, color="#c3c2b7", linewidth=1)
    ax2.set_ylabel("2026 − historical")
    ax2.set_xlabel("minute")
    ax2.text(band_hi + 1, ax2.get_ylim()[1] * 0.85,
             "second-break window\n(10th-90th pct of actual starts)",
             fontsize=8.5, color=INK2, va="top")

    fig.tight_layout()
    fig.savefig(FIGURES / "fig_subs_curve.png", dpi=200)
    plt.close(fig)


def main():
    s26, hist, b2, matches = load()
    shares = minute_shares(s26, hist)
    shares.to_csv(PROCESSED / "subs_minute_share.csv")

    lines = [
        "# Substitution timing — 2026 vs 2018/2022 (Core Output 4)",
        "",
        f"Regulation-time substitution events: WC2018 "
        f"{(hist['tournament']=='WC2018').sum()}, WC2022 "
        f"{(hist['tournament']=='WC2022').sum()}, WC2026 {len(s26)}.",
        "All comparisons use tournament shares (3-sub era vs 5-sub era).",
        "Association, not causation (spec §8).",
        "",
        "## Clustering on the actual second break",
        "",
        *break_window_stat(s26, hist, b2),
        "",
        "## Context statistics",
        "",
        *first_sub_and_state(s26, hist, matches),
        "",
        "## Notes",
        "- 2026 sub minutes come from PMSR markers with lineup-derived fallback;",
        "  stoppage-time rounding documented in HANDOFF_STATE §5.",
        "- Matches without a known second break (44, 1) and France-Iraq H2 are",
        "  excluded from the ±3' statistic.",
        "- Extra-time substitutions excluded everywhere.",
        "- The 85-90' tail is NOT comparable across sources: StatsBomb stoppage",
        "  subs are clipped to 90 while the 2026 parser rounds them into 85-90.",
        "  Do not interpret the late-minute excess; it is a recording artefact",
        "  plus longer 2026 added time (quantified in Core Output 6).",
    ]
    (TABLES / "subs_timing.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    chart(shares, b2)
    print("\n".join(lines))
    print(f"\nwrote {FIGURES / 'fig_subs_curve.png'}")


if __name__ == "__main__":
    main()
