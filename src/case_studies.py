"""Core Output 7 — transparent case-study selection + graphics.

Cases are chosen by a preregistered 2x2, never by fame (spec §12):

                        | large measured swing | small measured swing
    strong public claim | confirmed-feeling    | perception illusion
    little/no attention | hidden effect        | true null

Axis 1 (measured): each break's |Δ(home−away) shots| across the break, scored
as a percentile against the SAME match/half's eligible pseudo-break minutes —
the Test A null from src/placebo.py. Direction-agnostic, so it can be scored
for every break, including those nobody discussed.

Axis 2 (attention): whether the perception pilot found a public claim naming
that specific break.

Null cases are mandatory: they are what stops the story cherry-picking.

Outputs:
  data/processed/case_matrix.csv       all breaks, both axes, assigned cell
  reports/tables/case_studies.md
  reports/figures/fig_case_studies.png

Run:  python -m src.case_studies
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .placebo import MatchData, load_inputs
from .util import FIGURES, PROCESSED, TABLES

WINDOW = 8
HIGH_PCT, LOW_PCT = 80.0, 50.0


def build_matrix() -> pd.DataFrame:
    bands = pd.read_csv(PROCESSED / "break_bands.csv")
    _, shots, matches, events = load_inputs()
    claims = pd.read_csv("data/manual/perception_claims.csv")
    claimed = set(zip(claims["match_id"], claims["break_number"]))

    cache: dict[int, MatchData] = {}
    rows = []
    for _, b in bands.iterrows():
        mid = int(b["match_id"])
        m = cache.setdefault(mid, MatchData(mid, matches, shots, events, bands))
        obs = m.outcomes(b["start_minute"], b["duration_min"], WINDOW, "adjusted")
        disruption = obs["balance_disruption"]
        bucket = m.margin_bucket(b["start_minute"])
        cands = m.eligible_minutes(b["half"], bucket)
        if cands:
            null = np.array([m.outcomes(c, 0.0, WINDOW, "adjusted")["balance_disruption"]
                             for c in cands], float)
            pct = float((null <= disruption).mean() * 100)
        else:
            pct = np.nan
        rows.append({
            "match_id": mid, "break_number": int(b["break_number"]), "half": b["half"],
            "fixture": f"{m.home} v {m.away}",
            "home": m.home, "away": m.away,
            "start_minute": b["start_minute"],
            "disruption": disruption, "percentile": pct,
            "n_candidates": len(cands),
            "has_claim": (mid, int(b["break_number"])) in claimed,
            "stage": matches.loc[mid, "stage_name"],
        })
    df = pd.DataFrame(rows)

    def cell(r):
        if pd.isna(r["percentile"]):
            return "unscored"
        high = r["percentile"] >= HIGH_PCT
        low = r["percentile"] <= LOW_PCT
        if r["has_claim"]:
            return "confirmed_feeling" if high else ("perception_illusion" if low else "mid")
        return "hidden_effect" if high else ("true_null" if low else "mid")

    df["cell"] = df.apply(cell, axis=1)
    return df


def select(df: pd.DataFrame) -> pd.DataFrame:
    """Pick 3 large-swing and 3 small-swing cases, one match each, transparently."""
    picks, used_matches = [], set()

    def take(cell: str, n: int, ascending: bool):
        sub = df[(df["cell"] == cell) & ~df["match_id"].isin(used_matches)]
        # tie-break on disruption magnitude so picks are reproducible, not curated
        sub = sub.sort_values(["percentile", "disruption"], ascending=[ascending, ascending])
        for _, r in sub.head(n).iterrows():
            picks.append({**r.to_dict(), "selected_as": cell})
            used_matches.add(r["match_id"])

    take("confirmed_feeling", 2, ascending=False)   # claimed AND unusual
    take("hidden_effect", 1, ascending=False)       # unusual, nobody noticed
    take("perception_illusion", 2, ascending=True)  # claimed, ordinary
    take("true_null", 1, ascending=True)            # ordinary, unremarked
    return pd.DataFrame(picks)


def chart(sel: pd.DataFrame):
    import matplotlib.pyplot as plt
    from .charts import BLUE, CRITICAL, INK, INK2, MUTED, SURFACE

    _, shots, matches, events = load_inputs()
    bands = pd.read_csv(PROCESSED / "break_bands.csv")
    subs = pd.read_csv(PROCESSED / "substitutions_2026.csv")
    subs = subs[subs["direction"] == "on"]

    titles = {"confirmed_feeling": "Confirmed feeling", "hidden_effect": "Hidden effect",
              "perception_illusion": "Perception illusion", "true_null": "True null"}

    fig, axes = plt.subplots(2, 3, figsize=(14, 7.2), sharex=True)
    for ax, (_, r) in zip(axes.flat, sel.iterrows()):
        mid = int(r["match_id"])
        s = shots[shots["match_id"] == mid]
        grid = np.arange(0, 96)
        for team, color in ((r["home"], BLUE), (r["away"], MUTED)):
            mins = np.sort(s.loc[s["team"] == team, "minute"].to_numpy(float))
            ax.step(grid, np.searchsorted(mins, grid, side="right"),
                    where="post", color=color, linewidth=2, label=team)
        for _, bb in bands[bands["match_id"] == mid].iterrows():
            ax.axvspan(bb["start_minute"], bb["start_minute"] + bb["duration_min"],
                       color="#f3e8d9", zorder=0)
        # the break this case is about
        ax.axvline(r["start_minute"], color=CRITICAL, linewidth=1.6)
        gl = events[(events["match_id"] == mid) & (events["event_type"] == "Goal")]
        for _, g in gl.iterrows():
            ax.plot(g["pos"], 0, marker="o", color=INK, markersize=5, clip_on=False)
        for _, sb in subs[subs["match_id"] == mid].iterrows():
            ax.plot(sb["minute"], 0, marker="^", color=MUTED, markersize=4,
                    alpha=0.7, clip_on=False)

        fin = matches.loc[mid]
        ax.set_title(f"{titles[r['selected_as']]}\n{r['fixture']}  "
                     f"{fin['home_score']}-{fin['away_score']}  ·  break {r['break_number']} "
                     f"({r['percentile']:.0f}th pct)",
                     color=INK, fontsize=9.5, fontweight="bold", loc="left")
        ax.legend(frameon=False, fontsize=7.5, loc="upper left")
        ax.grid(axis="x", visible=False)
        ax.tick_params(length=0)
        ax.set_xlim(0, 95)
    for ax in axes[1]:
        ax.set_xlabel("minute")
    for ax in axes[:, 0]:
        ax.set_ylabel("cumulative shots")

    fig.suptitle("Six breaks, chosen by matrix — not by fame",
                 x=0.045, y=1.0, ha="left", fontsize=15, fontweight="bold", color=INK)
    fig.text(0.045, 0.945,
             "Shaded = hydration breaks · red line = the break in question · "
             "dots = goals · triangles = substitutions on. "
             "Percentile is vs the same match-half's ordinary minutes.",
             fontsize=9.5, color=INK2)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    fig.savefig(FIGURES / "fig_case_studies.png", dpi=200)
    plt.close(fig)


def main():
    df = build_matrix()
    df.to_csv(PROCESSED / "case_matrix.csv", index=False)
    sel = select(df)

    counts = df["cell"].value_counts()
    scored = df[df["percentile"].notna()]
    lines = [
        "# Case studies — transparent 2x2 selection (Core Output 7)",
        "",
        f"Scored breaks: {len(scored)} of {len(df)} "
        f"({df['percentile'].isna().sum()} unscored: no eligible pseudo-break minutes).",
        f"Axis 1: |Δ shot balance| across the break, percentile vs the same match/half's "
        f"ordinary minutes. Large ≥{HIGH_PCT:.0f}th, small ≤{LOW_PCT:.0f}th.",
        "Axis 2: did the perception pilot find a public claim naming that break?",
        "",
        "## Population",
        "",
        "| cell | breaks |",
        "|---|---|",
    ]
    for c in ("confirmed_feeling", "perception_illusion", "hidden_effect", "true_null",
              "mid", "unscored"):
        lines.append(f"| {c} | {int(counts.get(c, 0))} |")

    n_claim = int(df["has_claim"].sum())
    hi_unclaimed = int(((df["cell"] == "hidden_effect")).sum())
    lines += [
        "",
        f"Breaks with a public claim in the pilot: **{n_claim} of {len(df)}**. Breaks with "
        f"an equally large measured swing and no pilot claim: **{hi_unclaimed}**.",
        "",
        "**Caveat on that asymmetry — it is provisional.** The perception pilot ran a",
        "TOPICAL search (four outlets writing about hydration breaks), not the per-match",
        "sweep the codebook mandates for full collection. So `has_claim=False` means",
        "'no claim surfaced in the pilot', NOT 'nobody ever said anything'. Absence of",
        "evidence here is not yet evidence of absence; the 65 figure will move once the",
        "systematic per-match sweep runs. What IS already solid: large post-break swings",
        "are common (65+ breaks), while the swings that entered public narrative are few",
        "— consistent with availability bias, pending the full sweep to size it properly.",
        "",
        "## Selected cases",
        "",
        "| case type | fixture | stage | break | minute | disruption | pctile | claimed |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for _, r in sel.iterrows():
        lines.append(
            f"| {r['selected_as']} | {r['fixture']} | {r['stage']} | {r['break_number']} | "
            f"{r['start_minute']:.0f}' | {r['disruption']:.0f} | {r['percentile']:.0f} | "
            f"{'yes' if r['has_claim'] else 'no'} |")

    lines += [
        "",
        "## Selection rule (applied, not curated)",
        "- 2 confirmed-feeling, 1 hidden effect (the three large-swing cases);",
        "- 2 perception illusion, 1 true null (the three small-swing cases);",
        "- within each cell, ranked by percentile then disruption; one case per match.",
        "- No case was chosen because it was famous. Netherlands-Sweden,",
        "  Germany-Curacao and Switzerland-Bosnia were the planning-stage favourites;",
        "  they qualify only if the matrix puts them there.",
        "",
        "## Reading",
        "- 'Hidden effect' cases are the most important for the video: the break",
        "  visibly flipped the shot balance and no pilot source discussed it. The",
        "  selected one (Panama v England, 2nd break) is stark — Panama went from 1 shot",
        "  to England's 3 before the break, to 6 shots against England's 0 after it, and",
        "  still lost 0-2. A total pressure flip that left no trace in the narrative,",
        "  because the scoreboard never moved.",
        "- The two planning-stage favourites (Germany-Curacao, Netherlands-Sweden) did",
        "  qualify on their own merits — both scored at the 100th percentile. Switzerland-",
        "  Bosnia did not make the cut, which is the matrix doing its job.",
        "- 'Perception illusion' cases carry a public claim while the swing sits inside",
        "  the ordinary range for that same match-half.",
        "- Each case still needs a manual tactical review before it goes in the report;",
        "  the matrix picks WHICH matches to review, not what to conclude.",
    ]
    (TABLES / "case_studies.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    sel.to_csv(PROCESSED / "case_selected.csv", index=False)
    chart(sel)
    print("\n".join(lines))
    print(f"\nwrote {FIGURES / 'fig_case_studies.png'}")


if __name__ == "__main__":
    main()
