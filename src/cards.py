"""APPENDIX — exploratory yellow-card-rate analysis.

Every other result rests on shots. This adds one non-shot outcome that is
time-stamped and dense enough to test at all.

WHAT CARDS DO NOT MEASURE. A booking is not a measurement of tempo, rhythm or
"game control". It is a referee decision, driven by referee thresholds and
game-management style, tactical fouling, dissent, score state, match
importance, and cards administered late for an earlier incident. Any of those
can move card rates without the run of play changing, and the run of play can
change without any card. Treat this as a weak, indirect signal — an appendix,
never evidence about positional structure or tactical control.

Yellow cards are the only additional event type in the 2026 layer that is both
time-stamped and dense enough to test:

    time-resolved 2026 data   shots 2554 · substitutions 1914 ·
                              GOALS 308 · YELLOW CARDS 253 ·
                              red cards 15 · VAR 15
    everything else (line height, team length, build-up phases, line breaks,
    passing networks, defensive pressure, possession, physical) is ONE VALUE
    PER TEAM PER MATCH — verified across ~300 PMSR pages — so it cannot
    support any before/after comparison.

WHY GOALS ARE NOT USED HERE, despite being time-stamped and more numerous.
The matched control pool excludes candidate minutes within 3 minutes of a goal
(a preregistered Test A screen, so that control windows are not contaminated by
goal effects). Control windows are therefore goal-DEPLETED by construction:
0.054 goals per window against 0.227 in real break windows. That 4x gap is an
artefact of the screen, not an effect of breaks, and comparing the two would
manufacture a dramatic false positive. Red cards and VAR reviews are likewise
excluded from the control pool AND too rare (15 each). Yellow cards are not
screened, and their rates are comparable across arms (0.158 vs 0.167), so they
are the one outcome this design can carry.

Estimator matches Test B / E1: each break is differenced against the MEAN of
its own control pool (equal weight per break), and the paired differences are
bootstrapped by match.

Outputs: reports/tables/cards.md
Run:     python -m src.cards
"""
from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd

from .placebo import MatchData, _parse_minute, load_inputs
from .util import FIFA, PROCESSED, TABLES

WINDOWS = (5, 8, 10)
SEED = 20260724
N_BOOT = 4000
HALF = {"H1": (1, 45), "H2": (46, 90)}


def build():
    bands = pd.read_csv(PROCESSED / "break_bands.csv")
    _, shots, matches, events = load_inputs()
    cache = {int(m): MatchData(int(m), matches, shots, events, bands)
             for m in bands["match_id"].unique()}
    ev = pd.read_csv(FIFA / "match_events.csv", encoding="utf-8-sig")
    ev = ev[ev["event_type"] == "Yellow Card"].copy()
    ev["pos"] = ev["minute"].map(_parse_minute)
    pos = defaultdict(list)
    for _, r in ev.iterrows():
        pos[int(r["match_id"])].append(r["pos"])
    return bands, cache, {k: np.sort(v) for k, v in pos.items()}


def rate(pos, mid, lo, w):
    a = pos.get(mid)
    if a is None:
        return 0.0
    return float(np.searchsorted(a, lo + w) - np.searchsorted(a, lo)) / w


def analyse(bands, cache, pos):
    rng = np.random.default_rng(SEED)
    rows = []
    for w in WINDOWS:
        recs, pools = [], []
        for _, b in bands.iterrows():
            mid = int(b["match_id"])
            m = cache[mid]
            call, dur = b["start_minute"], b["duration_min"]
            lo, hi = HALF[b["half"]]
            if not (call - w >= lo - 1 and call + dur + w <= hi):
                continue
            cands = m.eligible_minutes(b["half"], m.margin_bucket(call), window=w)
            if not cands:
                continue
            pre = rate(pos, mid, call - w, w)
            post = rate(pos, mid, call + dur, w)
            recs.append({"match_id": mid, "pre": pre, "post": post,
                         "delta": post - pre, "n_ctrl": len(cands)})
            pools.append([rate(pos, mid, c, w) - rate(pos, mid, c - w, w)
                          for c in cands])

        df = pd.DataFrame(recs)
        ctrl = np.array([np.mean(p) for p in pools])
        d = df["delta"].to_numpy() - ctrl
        by_match = defaultdict(list)
        for i, r in enumerate(df.itertuples()):
            by_match[int(r.match_id)].append(i)
        mids = list(by_match)
        boot = np.empty(N_BOOT)
        for i in range(N_BOOT):
            pick = rng.integers(0, len(mids), len(mids))
            idxs = [j for p in pick for j in by_match[mids[p]]]
            boot[i] = d[idxs].mean()
        rows.append({
            "w": w, "n": len(df), "n_matches": df["match_id"].nunique(),
            "pre": df["pre"].mean(), "post": df["post"].mean(),
            "delta_real": df["delta"].mean(), "delta_ctrl": float(ctrl.mean()),
            "D": float(d.mean()),
            "D_lo": float(np.percentile(boot, 2.5)),
            "D_hi": float(np.percentile(boot, 97.5)),
        })
    return rows


def main():
    bands, cache, pos = build()
    rows = analyse(bands, cache, pos)

    lines = [
        "# Appendix — exploratory yellow-card-rate analysis",
        "",
        "**A weak, indirect signal. Not a measure of tempo, rhythm or game control.**",
        "A booking is a referee decision, driven by referee thresholds and game-management "
        "style, tactical fouling, dissent, score state, match importance, and cards given "
        "late for an earlier incident. Card rates can move without the run of play "
        "changing, and the run of play can change without any card. This is included only "
        "because it is the one non-shot outcome in the 2026 layer that is both "
        "time-stamped and dense enough to test at all.",
        "",
        "Rates are yellow cards per minute, both teams. Post-break windows start at "
        "resumption. Each break is differenced against the mean of its own matched "
        "control pool (equal weight per break); paired differences bootstrapped by match.",
        "",
        "| w | breaks | matches | pre rate | post rate | change (real) | change (matched) | **D** | 95% CI |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['w']} | {r['n']} | {r['n_matches']} | {r['pre']:.3f} | "
            f"{r['post']:.3f} | {r['delta_real']:+.4f} | {r['delta_ctrl']:+.4f} | "
            f"**{r['D']:+.4f}** | [{r['D_lo']:+.4f}, {r['D_hi']:+.4f}] |")

    zero = all(r["D_lo"] < 0 < r["D_hi"] for r in rows)
    lines += [
        "",
        ("**Every interval includes zero.** Booking rates after breaks are "
         "indistinguishable from those after matched ordinary minutes. Given the "
         "sparsity (~0.16 cards per 8-minute window) only a very large shift would be "
         "detectable, so this is weak evidence of no difference in booking rates — NOT "
         "a finding that the breaks left the character of the game unchanged."
         if zero else
         "**At least one interval excludes zero — see the table.**"),
        "",
        "## Why goals are NOT an outcome here",
        "",
        "Goals are time-stamped and more numerous than cards (308 vs 253), so they look "
        "like the better outcome. They cannot be used with this control pool. Test A's "
        "preregistered screen excludes candidate minutes within 3 minutes of a goal, so "
        "control windows are goal-depleted **by construction**:",
        "",
        "| | goals per 8-min window |",
        "|---|---|",
        "| real break windows | 0.227 |",
        "| matched control windows | 0.054 |",
        "",
        "That four-fold gap is the screen, not the breaks. Reporting it would have "
        "produced a dramatic false positive. Red cards and VAR reviews are excluded from "
        "the control pool for the same reason and are additionally far too rare (15 "
        "each). Yellow cards are not screened, and their base rates are comparable across "
        "arms, which is why they are the one additional outcome this design can carry.",
        "",
        "## Why there is no build-up or positional version of this table",
        "",
        "The FIFA post-match reports do contain rich tactical data — line height, team "
        "length, build-up phases, line breaks, passing networks, defensive pressure. "
        "Every page of six reports (~300 pages) was scanned for a half split, minute bin "
        "or per-period breakdown: **none exists**. Those metrics are one value per team "
        "per match, so a before/after-break comparison is not a difficult analysis, it is "
        "an undefined one. StatsBomb's 2018/2022 data does carry true event coordinates, "
        "but those tournaments had no universal breaks.",
        "",
        "## Limits",
        "",
        "- **Appendix status.** Exploratory, descriptive, and a weak proxy: cards measure "
        "referee decisions, not the run of play. Not evidence about positional structure "
        "or tactical control.",
        "- Sparse: ~0.16 cards per 8-minute window, so intervals are wide and only a "
        "large effect would be detectable.",
        "- Yellow cards only. Reds and VAR are too rare and are control-screened.",
        "- Confounded by referee thresholds, tactical fouling, dissent, score state and "
        "match importance, none of which are adjusted for here.",
    ]
    (TABLES / "cards.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
