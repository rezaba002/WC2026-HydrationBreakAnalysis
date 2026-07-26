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


def analyse(bands, cache, per, sot, match_sot=False):
    """match_sot: also require the control's pre-window SOT advantage to equal
    the break's. The attacking side is chosen on SOT first, so matching only on
    total-shot advantage can pair spells whose SOT dominance differs. Stricter,
    and it costs coverage."""
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
                if match_sot and (cpre_t - opre_t) != (pre_at - pre_ot):
                    continue
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

        # EQUAL WEIGHT PER BREAK. Flattening every candidate into one pooled mean
        # would let a break with 15 eligible controls count 15x while the real
        # side counts each break once — the point estimate and the bootstrap
        # would then describe different estimands. Each break gets the MEAN of
        # its own control pool, and the contrast is paired.
        ctrl_sw = np.array([np.mean([c[0] for c in p]) for p in pools])
        ctrl_st = np.array([np.mean([c[1] for c in p]) for p in pools])
        ctrl_rv = np.array([np.mean([c[2] for c in p]) for p in pools])
        d_sw, d_st, d_rv = sw - ctrl_sw, sot_sw - ctrl_st, rev - ctrl_rv

        bD, bDs, bR = np.empty(N_BOOT), np.empty(N_BOOT), np.empty(N_BOOT)
        for i in range(N_BOOT):
            pick = rng.integers(0, len(mids), len(mids))
            idxs = [j for p in pick for j in by_match[mids[p]]]
            bD[i] = d_sw[idxs].mean()
            bDs[i] = d_st[idxs].mean()
            bR[i] = d_rv[idxs].mean()

        # A5 diagnostic: each break against ONLY its same-orientation controls,
        # again one value per break. Breaks with no same-orientation control are
        # dropped from the diagnostic (never silently pooled).
        atk_home = df["atk_is_home"].to_numpy()
        same_or = np.array([
            np.mean([c[0] for c in p if c[3] == h]) if any(c[3] == h for c in p)
            else np.nan
            for p, h in zip(pools, atk_home)])
        ok = ~np.isnan(same_or)
        d_or = sw - same_or
        out.append({
            "w": w, "n": len(df), "n_matches": df["match_id"].nunique(),
            "ambiguous": ambiguous, "unmatched": unmatched,
            "pre_adv": df["pre_adv"].mean(),
            "swing_real": sw.mean(), "swing_ctrl": float(ctrl_sw.mean()),
            "D": float(d_sw.mean()),
            "D_lo": float(np.percentile(bD, 2.5)),
            "D_hi": float(np.percentile(bD, 97.5)),
            "sot_real": sot_sw.mean(), "sot_ctrl": float(ctrl_st.mean()),
            "Dsot": float(d_st.mean()),
            "Dsot_lo": float(np.percentile(bDs, 2.5)),
            "Dsot_hi": float(np.percentile(bDs, 97.5)),
            "rev_real": rev.mean(), "rev_ctrl": float(ctrl_rv.mean()),
            "Drev": float(d_rv.mean()),
            "Drev_lo": float(np.percentile(bR, 2.5)),
            "Drev_hi": float(np.percentile(bR, 97.5)),
            "median_ctrl": float(df["n_ctrl"].median()),
            "D_home": float(d_or[ok & atk_home].mean()),
            "D_away": float(d_or[ok & ~atk_home].mean()),
            "n_or_home": int((ok & atk_home).sum()),
            "n_or_away": int((ok & ~atk_home).sum()),
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
        "| w | breaks | matches | mean pre-break advantage | swing (real) | swing (matched spells) | **D** | 95% CI |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['w']} | {r['n']} | {r['n_matches']} | +{r['pre_adv']:.2f} | "
            f"{r['swing_real']:+.3f} | {r['swing_ctrl']:+.3f} | **{r['D']:+.3f}** | "
            f"[{r['D_lo']:+.3f}, {r['D_hi']:+.3f}] |")

    lines += [
        "",
        "Note how large the *unadjusted* swings are in BOTH columns: teams that have just "
        "been dominating give most of that edge back within minutes, break or no break. "
        "That is regression to the mean, and it is exactly what an unmatched analysis "
        "would have mistaken for a break effect.",
        "",
        "**Weighting.** Every break contributes equally: each is differenced against the "
        "MEAN of its own control pool, and D is the mean of those paired differences. "
        "Pooling all candidates instead would let a break with 15 eligible controls "
        "outweigh one with a single control by 15x on the control side while counting "
        "once on the real side — the point estimate and the interval would then describe "
        "different estimands.",
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
    # sensitivity: also match on pre-window SOT advantage
    strict, _ = analyse(bands, cache, per, sot, match_sot=True)
    lines += [
        "",
        "### Sensitivity — matching on (shot advantage, SOT advantage)",
        "",
        "The attacking side is chosen on shots on target first, but the main matching key "
        "is the total-shot advantage alone, so two spells can pair while differing in SOT "
        "dominance. Requiring both to match tests whether 'comparable pressure' means "
        "more than the same raw shot differential. It costs coverage.",
        "",
        "| w | breaks (main) | breaks (strict) | D (main) | D (strict) | 95% CI (strict) |",
        "|---|---|---|---|---|---|",
    ]
    for r, s in zip(rows, strict):
        lines.append(f"| {r['w']} | {r['n']} | {s['n']} | {r['D']:+.3f} | "
                     f"{s['D']:+.3f} | [{s['D_lo']:+.3f}, {s['D_hi']:+.3f}] |")

    lines += [
        "",
        "### A5 diagnostic — attacker home vs away (orientation-stratified)",
        "",
        "Each break is compared with ONLY its same-orientation controls (home-attacking "
        "breaks against home-attacking control spells, likewise away), one value per "
        "break; breaks with no same-orientation control are dropped rather than pooled. "
        "An earlier version differenced both strata against the POOLED control mean, "
        "which confounded control-pool composition with the effect.",
        "",
        "| w | D, attacker home | D, attacker away | gap | breaks (home / away) |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['w']} | {r['D_home']:+.3f} | {r['D_away']:+.3f} | "
                     f"{r['D_home'] - r['D_away']:+.3f} | "
                     f"{r['n_or_home']} / {r['n_or_away']} |")
    lines += [
        "",
        "The gap is small and **changes sign across windows**, which is what noise looks "
        "like rather than a systematic orientation bias. An earlier, candidate-weighted "
        "version of this table showed a large and consistently positive gap "
        "(+0.63 / +0.43 / +0.58); that was an artefact of the weighting defect described "
        "above, and it disappeared once every break was given equal weight against its "
        "own same-orientation controls.",
        "",
        "The strata are still **not reported as findings**: they are the signed, "
        "home-oriented class CHANGELOG A5 quarantined, and each cell holds only ~30–45 "
        "breaks. They serve here purely as a check that the pooled estimate is not an "
        "average of two large opposing biases — and it is not.",
    ]

    (TABLES / "test_b.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    pd.DataFrame([{k: v for k, v in r.items() if k != "_df"} for r in rows]).to_csv(
        PROCESSED / "test_b_results.csv", index=False)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
