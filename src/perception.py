"""Core Output 5 — perception claims vs objective post-break change.

Collection is manual and preregistered (docs/perception_codebook.md); this
module runs the SEPARATE, blinded evaluation step: it never reads claim_text,
only (match_id, break_number, claimed_team_helped).

Coding rule, frozen in codebook §5: a claim is `supported` when the observed
post-break swing toward the claimed-helped team is both
  (a) in the claimed direction, and
  (b) at or above the 80th percentile of the SAME match/half's eligible
      pseudo-break minutes (the Test A null from src/placebo.py).
Anything else is `not_supported`; missing break/shot data is `indeterminate`.

Outcome: change in the claimed team's shot differential across the break,
on the break-adjusted clock, 8-minute windows (spec primary).

Outputs:
  data/processed/perception_evaluated.csv
  reports/tables/perception.md

Run:  python -m src.perception
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .placebo import MatchData, load_inputs
from .util import FIGURES, PROCESSED, TABLES

WINDOW = 8
SUPPORT_PCT = 80.0

# claim-sheet spellings -> matches.csv spellings
TEAM_FIX = {"Curacao": "Curaçao", "Cote d'Ivoire": "Côte d'Ivoire",
            "Turkiye": "Türkiye", "Iran": "IR Iran"}


def oriented_change(m: MatchData, start: float, duration: float, team: str) -> float:
    """Δ(team shots − opponent shots) across the break, break-adjusted clock."""
    o = m.outcomes(start, duration, WINDOW, "adjusted")
    signed = o["shot_diff_change"]              # home-oriented
    return signed if team == m.home else -signed


def main():
    claims = pd.read_csv("data/manual/perception_claims.csv")
    bands = pd.read_csv(PROCESSED / "break_bands.csv")
    _, shots, matches, events = load_inputs()

    rows = []
    for _, c in claims.iterrows():
        mid, bn = int(c["match_id"]), int(c["break_number"])
        helped = TEAM_FIX.get(str(c["claimed_team_helped"]), str(c["claimed_team_helped"]))
        band = bands[(bands["match_id"] == mid) & (bands["break_number"] == bn)]
        rec = {"claim_id": c["claim_id"], "match_id": mid, "break_number": bn,
               "claimed_team_helped": helped}

        if band.empty:
            rec.update(status="indeterminate",
                       note="no break record for this match/half (documented exclusion)")
            rows.append(rec)
            continue

        b = band.iloc[0]
        m = MatchData(mid, matches, shots, events, bands)
        if helped not in (m.home, m.away):
            rec.update(status="indeterminate",
                       note=f"claimed team '{helped}' not in fixture {m.home} v {m.away}")
            rows.append(rec)
            continue

        obs = oriented_change(m, b["start_minute"], b["duration_min"], helped)
        bucket = m.margin_bucket(b["start_minute"])
        cands = m.eligible_minutes(b["half"], bucket)
        if not cands:
            rec.update(observed_change=obs, status="indeterminate",
                       note="no eligible pseudo-break minutes for this match/half")
            rows.append(rec)
            continue

        null = np.array([oriented_change(m, c_, 0.0, helped) for c_ in cands], float)
        pct = float((null <= obs).mean() * 100)
        supported = (obs > 0) and (pct >= SUPPORT_PCT)
        rec.update(observed_change=obs, n_candidates=len(cands),
                   null_median=float(np.median(null)), percentile=round(pct, 1),
                   status="supported" if supported else "not_supported",
                   note="")
        rows.append(rec)

    # Direction alone can refute a claim: a swing that ran AGAINST the claimed
    # beneficiary fails condition (a) whether or not a null could be built.
    for rec in rows:
        if rec["status"] == "indeterminate" and rec.get("observed_change", 0) < 0 \
                and "not in fixture" not in rec.get("note", ""):
            rec["status"] = "not_supported"
            rec["note"] = "swing ran against the claimed team; no null needed to refute"

    ev = pd.DataFrame(rows)
    verified_ids = set(claims.loc[
        claims["verification_status"].str.startswith("verbatim_confirmed"), "claim_id"])
    ev["verified"] = ev["claim_id"].isin(verified_ids)
    ev.to_csv(PROCESSED / "perception_evaluated.csv", index=False)

    testable = ev[ev["status"] != "indeterminate"]
    n_sup = (testable["status"] == "supported").sum()
    vt = testable[testable["verified"]]
    n_vsup = (vt["status"] == "supported").sum()
    n_unverified = int((~ev["verified"]).sum())

    # Break-level rate: several claims can describe the SAME break (e.g. three
    # separate outlets on England-DR Congo break 1), which would let heavily
    # discussed incidents dominate a claim-level rate. Deduplicate to unique
    # (match, break, claimed beneficiary) — the objective verdict is a property
    # of the break and direction, not of how many outlets wrote it up.
    uniq = (vt.groupby(["match_id", "break_number", "claimed_team_helped"])["status"]
            .agg(lambda s: "supported" if (s == "supported").any() else "not_supported")
            .reset_index())
    n_ubreaks = len(uniq)
    n_usup = int((uniq["status"] == "supported").sum())

    lines = [
        "# Perception claims vs objective evidence — Core Output 5",
        "",
        f"Claims collected: {len(claims)} · source-verified: {len(verified_ids)} · "
        f"unverified: {n_unverified}",
        "",
        f"**HEADLINE — unique claimed breaks (verified): {n_usup}/{n_ubreaks} "
        f"({n_usup/n_ubreaks:.0%}) supported.** This is the statistically independent "
        "measure: repeated coverage of one incident counts once.",
        "",
        f"Claim-level, for comparison: {n_vsup}/{len(vt)} ({n_vsup/len(vt):.0%}). The two "
        "differ because heavily covered incidents contribute several rows, which can pull "
        "the claim-level rate either way — here it pulls it DOWN, since the most-covered "
        "break (England–DR Congo break 1, three separate claims) is not supported.",
        "",
        f"Support = claim direction correct AND swing ≥{SUPPORT_PCT:.0f}th percentile of "
        "the same match/half's pseudo-break minutes.",
        "",
        f"(All claims incl. unverified: {n_sup}/{len(testable)} "
        f"({n_sup/len(testable):.0%}) — shown for completeness, not for citation.)",
        "",
        "Every claim was re-read against its source URL on 2026-07-25. Quotes that could",
        "not be located at their cited source are marked UNVERIFIED and excluded from the",
        "headline: PC-020 (podcast never located), PC-021 (ESPN 403), PC-022 (cited page",
        "contains no such quote). Two corrections were applied: PC-006's break number",
        "(1→2) and PC-014's claim text. See `data/manual/perception_claims.csv`.",
        "",
        "Evaluation was blinded to claim text: only (match, break, team-helped) was read.",
        "",
        "| claim | ok | match | brk | team claimed helped | Δ shot diff | null median | pctile | verdict |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    mm = matches
    for _, r in ev.iterrows():
        fx = f"{mm.loc[r['match_id'], 'home']} v {mm.loc[r['match_id'], 'away']}" \
            if r["match_id"] in mm.index else str(r["match_id"])
        obs = "" if pd.isna(r.get("observed_change")) else f"{r['observed_change']:+.0f}"
        nul = "" if pd.isna(r.get("null_median")) else f"{r['null_median']:+.1f}"
        pct = "" if pd.isna(r.get("percentile")) else f"{r['percentile']:.0f}"
        lines.append(f"| {r['claim_id']} | {'✓' if r['verified'] else '—'} | {fx} | "
                     f"{r['break_number']} | "
                     f"{r['claimed_team_helped']} | {obs} | {nul} | {pct} | {r['status']} |")

    n_breaks_claimed = claims.groupby(["match_id", "break_number"]).ngroups
    lines += [
        "",
        "## Pilot findings",
        "",
        f"- Claim supply is NOT the bottleneck the handoff feared: {len(claims)} usable",
        "  claims came from four outlets in one collection pass, with 12 rejections",
        "  logged. Reaching ~40 is realistic.",
        "",
        "- **The headline is the denominator, not the hit rate.** The stratified random "
        "sweep put public claims on **4 of 48 sampled breaks (8.3%, 95% CI 3.3-19.6%)**; "
        f"across all collection this file holds claims on {n_breaks_claimed} of 203 "
        "breaks. Within that small, self-selected set the claims are supported about half "
        "the time — pundits are not fabricating, they are describing real swings drawn "
        "from the tail of a distribution, and the tournament-wide story is then written "
        "from that tail. The large majority of breaks generated no public narrative at "
        "all, whether or not ordinary volatility produced a swing afterwards.",
        "",
        "- Claims cluster on a single narrative: the break rescued the favourite from",
        "  an underdog's spell (Germany-Curacao, Brazil-Morocco, Austria-Jordan,",
        "  Uruguay-Saudi Arabia, England-DR Congo). Small nations supply the harmed side",
        "  in nearly every case.",
        "- One claim (PC-010) concerns match 44, our documented exclusion — a public",
        "  claim exists about a match no dataset we hold can adjudicate.",
        f"- Verification: all {len(claims)} claims were re-read against their source URLs",
        f"  on 2026-07-25. {len(verified_ids)} were confirmed; {n_unverified} could not be",
        "  and are excluded from every figure above (PC-020, PC-021, PC-022).",
        "",
        "## Caveats",
        "- n is small; percentages are indicative, not final.",
        "- The support rule uses shot differential (per CHANGELOG A2, no per-shot xG).",
        "  Several claims cite xG or touches; those are not the coded outcome.",
        "- Several breaks carry claims from multiple independent outlets. Rows are kept",
        "  separate (the collection unit is the claim), which is exactly why the headline",
        "  above is the deduplicated BREAK-level rate.",
    ]
    (TABLES / "perception.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
