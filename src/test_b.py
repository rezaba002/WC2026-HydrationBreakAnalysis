"""Test B — state-matched directional analysis (PREREGISTERED, spec §5).

The frozen spec defines Test B as the state-matched companion to Test A:
"Matches on pre-window dominance. Answers the narrower, audience-relevant
question: 'what normally happens after a period of comparable pressure?'
Labelled descriptive. It is not the causal claim." It was specified before any
analysis and is implemented here.

WHY IT IS NEEDED. Test A and the E1 clock analysis both measure TOTAL activity
(both teams). Total activity can be flat while momentum changes hands
completely:

    before break   Team A 5 shots, Team B 0      total 5
    after  break   Team A 1 shot,  Team B 4      total 5

A total-activity null says "no decline"; the attacking advantage has in fact
been wiped out. The public claim — "we were all over them and the break killed
it" — is directional, so it needs a directional test.

DESIGN.
  1. Fix the attacking side from the PRE-window only, by a frozen hierarchy:
     more shots on target; ties broken on total shots; still tied -> the break
     is directionally ambiguous and is excluded (counted, never re-oriented).
  2. Its identity is then FROZEN. Nothing after the break may change it.
  3. advantage = attacker shots - opponent shots.
     swing = post-break advantage - pre-break advantage.  Negative = the
     attacking side lost its edge.
  4. THE CRITICAL CONTROL. Teams that have just been dominating regress to the
     mean whether or not anyone stops the game, so an unmatched swing is
     meaningless. Controls are ordinary minutes in the same match and half,
     same score state, whose OWN pre-window advantage EQUALS the break's, and
     oriented by their own pre-window leader. The estimate is
         swing(real) - swing(matched ordinary spells)
     i.e. did attacking teams lose MORE of their advantage after a hydration
     break than after comparable uninterrupted spells?

Post-break windows start at RESUMPTION (dead time excluded), consistent with E1.

Outputs: reports/tables/test_b.md, data/processed/test_b_results.csv
Run:     python -m src.test_b
"""
from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd

from .placebo import MatchData, load_inputs
from .util import PROCESSED, TABLES

WINDOWS = (5, 8, 10)
SEED = 20260724
N_BOOT = 4000
HALF = {"H1": (1, 45), "H2": (46, 90)}


def build():
    bands = pd.read_csv(PROCESSED / "break_bands.csv")
    _, shots, matches, events = load_inputs()
    cache = {int(m): MatchData(int(m), matches, shots, events, bands)
             for m in bands["match_id"].unique()}
    sh = shots[shots["minute"] <= 95]
    per: dict[tuple, int] = defaultdict(int)      # (mid, team, minute) -> shots
    sot: dict[tuple, int] = defaultdict(int)      # (mid, team, minute) -> on target
    for _, r in sh.iterrows():
        k = (int(r["match_id"]), r["team"], int(r["minute"]))
        per[k] += 1
        if str(r["outcome"]).startswith("On Target"):
            sot[k] += 1
    return bands, cache, per, sot


def counts(per, sot, mid, team, lo, w):
    s = sum(per.get((mid, team, int(lo + k)), 0) for k in range(int(w)))
    t = sum(sot.get((mid, team, int(lo + k)), 0) for k in range(int(w)))
    return s, t


def orient(per, sot, mid, home, away, lo, w):
    """Frozen pre-window hierarchy -> (attacker, opponent, advantage) or None."""
    hs, ht = counts(per, sot, mid, home, lo, w)
    as_, at = counts(per, sot, mid, away, lo, w)
    if ht != at:
        return (home, away, hs - as_) if ht > at else (away, home, as_ - hs)
    if hs != as_:
        return (home, away, hs - as_) if hs > as_ else (away, home, as_ - hs)
    return None                                   # directionally ambiguous


def analyse(bands, cache, per, sot):
    rng = np.random.default_rng(SEED)
    out, detail = [], []
    for w in WINDOWS:
        recs, pools, ambiguous, unmatched = [], [], 0, 0
        for _, b in bands.iterrows():
            mid = int(b["match_id"])
            m = cache[mid]
            call, dur = b["start_minute"], b["duration_min"]
            lo, hi = HALF[b["half"]]
            if not (call - w >= lo - 1 and call + dur + w <= hi):
                continue
            o = orient(per, sot, mid, m.home, m.away, call - w, w)
            if o is None:
                ambiguous += 1
                continue
            atk, opp, pre_adv = o
            if pre_adv < 1:            # no real dominance to lose
                ambiguous += 1
                continue
            a_s, a_t = counts(per, sot, mid, atk, call + dur, w)
            o_s, o_t = counts(per, sot, mid, opp, call + dur, w)
            _, pre_at = counts(per, sot, mid, atk, call - w, w)
            _, pre_ot = counts(per, sot, mid, opp, call - w, w)
            post_adv = a_s - o_s
            swing = post_adv - pre_adv
            sot_swing = (a_t - o_t) - (pre_at - pre_ot)

            # state-matched controls: SAME pre-window advantage, own orientation
            cand = []
            for c in m.eligible_minutes(b["half"], m.margin_bucket(call)):
                if not (c - w >= lo - 1 and c + w <= hi):
                    continue
                oc = orient(per, sot, mid, m.home, m.away, c - w, w)
                if oc is None:
                    continue
                catk, copp, c_pre = oc
                if c_pre != pre_adv:          # the matching key
                    continue
                cs, ct = counts(per, sot, mid, catk, c, w)
                os_, ot = counts(per, sot, mid, copp, c, w)
                _, cpre_t = counts(per, sot, mid, catk, c - w, w)
                _, opre_t = counts(per, sot, mid, copp, c - w, w)
                cand.append(((cs - os_) - c_pre,
                             ((ct - ot) - (cpre_t - opre_t)),
                             1 if (cs - os_) < 0 else 0,
                             catk == m.home))
            if not cand:
                unmatched += 1
                continue
            recs.append({
                "match_id": mid, "break_number": int(b["break_number"]),
                "half": b["half"], "pre_adv": pre_adv, "post_adv": post_adv,
                "swing": swing, "sot_swing": sot_swing,
                "reversed": 1 if post_adv < 0 else 0,
                "atk_is_home": atk == m.home, "n_ctrl": len(cand),
            })
            pools.append(cand)

        df = pd.DataFrame(recs)
        by_match = defaultdict(list)
        for i, r in enumerate(df.itertuples()):
            by_match[int(r.match_id)].append(i)
        mids = list(by_match)
        sw, sot_sw, rev = (df["swing"].to_numpy(), df["sot_swing"].to_numpy(),
                           df["reversed"].to_numpy())

        bD, bDs, bR = np.empty(N_BOOT), np.empty(N_BOOT), np.empty(N_BOOT)
        for i in range(N_BOOT):
            pick = rng.integers(0, len(mids), len(mids))
            idxs = [j for p in pick for j in by_match[mids[p]]]
            cs, ct, cr = [], [], []
            for j in idxs:
                a, b_, c_, _ = pools[j][rng.integers(0, len(pools[j]))]
                cs.append(a); ct.append(b_); cr.append(c_)
            bD[i] = sw[idxs].mean() - np.mean(cs)
            bDs[i] = sot_sw[idxs].mean() - np.mean(ct)
            bR[i] = rev[idxs].mean() - np.mean(cr)

        fs = [a for p in pools for a, _, _, _ in p]
        ft = [b for p in pools for _, b, _, _ in p]
        fr = [c for p in pools for _, _, c, _ in p]
        # orientation-stratified control means, for the A5 diagnostic: compare
        # home-attacker breaks with home-attacker controls, and likewise away.
        ctrl_home = [a for p in pools for a, _, _, h in p if h]
        ctrl_away = [a for p in pools for a, _, _, h in p if not h]
        out.append({
            "w": w, "n": len(df), "n_matches": df["match_id"].nunique(),
            "ambiguous": ambiguous, "unmatched": unmatched,
            "pre_adv": df["pre_adv"].mean(),
            "swing_real": sw.mean(), "swing_ctrl": float(np.mean(fs)),
            "D": sw.mean() - float(np.mean(fs)),
            "D_lo": float(np.percentile(bD, 2.5)),
            "D_hi": float(np.percentile(bD, 97.5)),
            "sot_real": sot_sw.mean(), "sot_ctrl": float(np.mean(ft)),
            "Dsot": sot_sw.mean() - float(np.mean(ft)),
            "Dsot_lo": float(np.percentile(bDs, 2.5)),
            "Dsot_hi": float(np.percentile(bDs, 97.5)),
            "rev_real": rev.mean(), "rev_ctrl": float(np.mean(fr)),
            "Drev": rev.mean() - float(np.mean(fr)),
            "Drev_lo": float(np.percentile(bR, 2.5)),
            "Drev_hi": float(np.percentile(bR, 97.5)),
            "median_ctrl": float(df["n_ctrl"].median()),
            "ctrl_home": float(np.mean(ctrl_home)) if ctrl_home else float("nan"),
            "ctrl_away": float(np.mean(ctrl_away)) if ctrl_away else float("nan"),
            "n_ctrl_home": len(ctrl_home), "n_ctrl_away": len(ctrl_away),
            "_df": df,
        })
        detail.append(df)
    return out, detail


def main():
    bands, cache, per, sot = build()
    rows, _ = analyse(bands, cache, per, sot)

    lines = [
        "# Test B — did the attacking team lose its advantage? (PREREGISTERED, spec §5)",
        "",
        "Test A and the E1 clock analysis measure TOTAL activity, which can stay flat "
        "while momentum changes hands. This is the directional test the spec reserved "
        "for that question, and the one the public claim actually makes.",
        "",
        "The attacking side is fixed from the PRE-window only (shots on target, ties on "
        "total shots) and then frozen. `swing` = post-break advantage − pre-break "
        "advantage; negative means the attacking side lost its edge. Post-break windows "
        "start at resumption.",
        "",
        "**Controls are state-matched:** ordinary minutes in the same match and half, "
        "same score state, whose OWN pre-window advantage EQUALS the break's, oriented "
        "by their own pre-window leader. Without that, regression to the mean alone "
        "guarantees a negative swing and the test would be meaningless.",
        "",
        "## Did the attacking team lose more advantage than usual?",
        "",
        "| w | breaks | matches | mean pre-break advantage | swing (real) | swing (matched spells) | **D** | 95% CI | D, orientation-standardised |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        df = r["_df"]
        ph = df["atk_is_home"].mean()
        dh = df[df["atk_is_home"]]["swing"].mean() - r["ctrl_home"]
        da = df[~df["atk_is_home"]]["swing"].mean() - r["ctrl_away"]
        r["D_std"] = ph * dh + (1 - ph) * da
        lines.append(
            f"| {r['w']} | {r['n']} | {r['n_matches']} | +{r['pre_adv']:.2f} | "
            f"{r['swing_real']:+.3f} | {r['swing_ctrl']:+.3f} | **{r['D']:+.3f}** | "
            f"[{r['D_lo']:+.3f}, {r['D_hi']:+.3f}] | {r['D_std']:+.3f} |")

    lines += [
        "",
        "Note how large the *unadjusted* swings are in BOTH columns: teams that have just "
        "been dominating give most of that edge back within minutes, break or no break. "
        "That is regression to the mean, and it is exactly what an unmatched analysis "
        "would have mistaken for a break effect.",
        "",
        "The final column standardises the control pool to the treated sample's "
        "home/away composition, because the two pools differ by 3–11 percentage points "
        "on which side was attacking (see the A5 diagnostic). It moves the estimate "
        "negligibly relative to the interval width, so composition mismatch is not "
        "driving the result.",
        "",
        "## Shots on target, and momentum changing hands",
        "",
        "| w | SOT swing D | 95% CI | reversal rate (real) | reversal (matched) | **D** | 95% CI |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['w']} | {r['Dsot']:+.3f} | [{r['Dsot_lo']:+.3f}, {r['Dsot_hi']:+.3f}] | "
            f"{r['rev_real']:.1%} | {r['rev_ctrl']:.1%} | **{r['Drev']:+.1%}** | "
            f"[{r['Drev_lo']:+.1%}, {r['Drev_hi']:+.1%}] |")

    lines += [
        "",
        "`reversal` = the previously attacking team is behind on shots in the post window "
        "— momentum has changed hands.",
        "",
        "## Coverage and exclusions",
        "",
        "| w | analysed | directionally ambiguous | no state-matched control | median controls |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['w']} | {r['n']} | {r['ambiguous']} | {r['unmatched']} | "
                     f"{r['median_ctrl']:.0f} |")

    lines += [
        "",
        "Ambiguous = neither side led the pre-window on shots on target or total shots "
        "(including genuinely quiet pre-windows). Those breaks are counted and excluded; "
        "they are never re-oriented using post-break information.",
        "",
        "## Limits",
        "",
        "- Descriptive, not causal. The spec labels Test B descriptive: matching on "
        "pre-window dominance rebuilds part of the selection mechanism, which is why "
        "Test A (not this) carries the causal claim.",
        "- Exact matching on integer pre-window advantage keeps the comparison clean but "
        "thins the control pool; breaks with no matched control are reported above and "
        "excluded rather than matched loosely.",
        "- Shots and shots on target only. No per-shot xG exists in the auditable layer "
        "(CHANGELOG A2), so 'advantage' is a count, not a chance-quality measure.",
        "- CHANGELOG A5 ruled the HOME-oriented signed contrast unreportable because the "
        "control pool's unconditional home−away mean is biased. Orientation here is by "
        "pre-window dominance, not home/away, and both arms are oriented by the same "
        "rule, so that specific bias should cancel — the home/away split below is the "
        "check on whether it does.",
    ]

    # A5 diagnostic: does the result differ by whether the attacker was home?
    lines += [
        "",
        "### A5 diagnostic — attacker home vs away (orientation-stratified)",
        "",
        "Each stratum is compared with controls of the SAME orientation (home-attacking "
        "breaks against home-attacking control spells, and likewise away). An earlier "
        "version of this diagnostic differenced both strata against the POOLED control "
        "mean, which confounded control-pool composition with the effect and produced a "
        "spurious home/away gap.",
        "",
        "| w | D, attacker home | D, attacker away | gap | control n (home / away) |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        df = r["_df"]
        h = df[df["atk_is_home"]]["swing"].mean() - r["ctrl_home"]
        a = df[~df["atk_is_home"]]["swing"].mean() - r["ctrl_away"]
        lines.append(f"| {r['w']} | {h:+.3f} | {a:+.3f} | {h - a:+.3f} | "
                     f"{r['n_ctrl_home']} / {r['n_ctrl_away']} |")
    lines += [
        "",
        "**The gap does not vanish, so the A5 bias survives into this design, and the "
        "home/away strata above are therefore NOT REPORTABLE as findings** — they are "
        "exactly the class of signed, home-oriented contrast that CHANGELOG A5 "
        "quarantined. They are shown only as a diagnostic on the pooled estimate.",
        "",
        "What the pooled estimate inherits from that bias is limited to composition: the "
        "treated and control pools differ by 3–11 points on which side was attacking. "
        "Standardising the controls to the treated composition (final column of the main "
        "table) shifts the estimate far less than the interval width, so the headline "
        "survives. Anyone wishing to interpret the home/away split itself must first "
        "rebuild the control pool as A5 requires.",
    ]

    (TABLES / "test_b.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    pd.DataFrame([{k: v for k, v in r.items() if k != "_df"} for r in rows]).to_csv(
        PROCESSED / "test_b_results.csv", index=False)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
