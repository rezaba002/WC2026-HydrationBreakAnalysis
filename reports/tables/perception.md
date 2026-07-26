# Perception claims vs objective evidence — Core Output 5

Claims collected: 22 · source-verified: 19 · unverified: 3

**HEADLINE — unique claimed breaks (verified): 7/12 (58%) supported.** This is the statistically independent measure: repeated coverage of one incident counts once.

Claim-level, for comparison: 8/16 (50%). The two differ because heavily covered incidents contribute several rows, which can pull the claim-level rate either way — here it pulls it DOWN, since the most-covered break (England–DR Congo break 1, three separate claims) is not supported.

Support = claim direction correct AND swing ≥80th percentile of the same match/half's pseudo-break minutes.

(All claims incl. unverified: 10/19 (53%) — shown for completeness, not for citation.)

Every claim was re-read against its source URL on 2026-07-25. Quotes that could
not be located at their cited source are marked UNVERIFIED and excluded from the
headline: PC-020 (podcast never located), PC-021 (ESPN 403), PC-022 (cited page
contains no such quote). Two corrections were applied: PC-006's break number
(1→2) and PC-014's claim text. See `data/manual/perception_claims.csv`.

Evaluation was blinded to claim text: only (match, break, team-helped) was read.

| claim | ok | match | brk | team claimed helped | Δ shot diff | null median | pctile | verdict |
|---|---|---|---|---|---|---|---|---|
| PC-001 | ✓ | Netherlands v Sweden | 1 | Sweden | +4 | -1.0 | 100 | supported |
| PC-002 | ✓ | Germany v Curaçao | 1 | Germany | +5 | -3.0 | 100 | supported |
| PC-003 | ✓ | Switzerland v Bosnia and Herzegovina | 2 | Switzerland | +1 | -2.0 | 100 | supported |
| PC-004 | ✓ | Austria v Jordan | 2 | Austria | +0 | +1.0 | 27 | not_supported |
| PC-005 | ✓ | Brazil v Haiti | 1 | Brazil | +0 |  |  | indeterminate |
| PC-006 | ✓ | England v Croatia | 2 | Croatia | +3 | +4.0 | 44 | not_supported |
| PC-007 | ✓ | Germany v Curaçao | 1 | Germany | +5 | -3.0 | 100 | supported |
| PC-008 | ✓ | Saudi Arabia v Uruguay | 2 | Uruguay | +1 | +0.0 | 100 | supported |
| PC-009 | ✓ | Austria v Jordan | 2 | Austria | +0 | +1.0 | 27 | not_supported |
| PC-010 | ✓ | Jordan v Algeria | 2 | Algeria |  |  |  | indeterminate |
| PC-011 | ✓ | Brazil v Morocco | 1 | Brazil | -4 |  |  | not_supported |
| PC-012 | ✓ | England v Congo DR | 1 | England | +0 | +1.0 | 43 | not_supported |
| PC-013 | ✓ | England v Congo DR | 2 | England | +4 | -5.0 | 100 | supported |
| PC-014 | ✓ | Norway v England | 1 | Norway | -1 | +0.0 | 0 | not_supported |
| PC-015 | ✓ | England v Congo DR | 1 | England | +0 | +1.0 | 43 | not_supported |
| PC-016 | ✓ | England v Congo DR | 1 | England | +0 | +1.0 | 43 | not_supported |
| PC-017 | ✓ | England v Croatia | 1 | Croatia | +1 |  |  | indeterminate |
| PC-018 | ✓ | Panama v England | 1 | Panama | +2 | +1.0 | 100 | supported |
| PC-019 | ✓ | Panama v England | 2 | Panama | +8 | -7.0 | 100 | supported |
| PC-020 | — | Germany v Curaçao | 1 | Germany | +5 | -3.0 | 100 | supported |
| PC-021 | — | Switzerland v Bosnia and Herzegovina | 2 | Switzerland | +1 | -2.0 | 100 | supported |
| PC-022 | — | Brazil v Morocco | 1 | Brazil | -4 |  |  | not_supported |

## Pilot findings

- Claim supply is NOT the bottleneck the handoff feared: 22 usable
  claims came from four outlets in one collection pass, with 12 rejections
  logged. Reaching ~40 is realistic.

- **The headline is the denominator, not the hit rate.** The stratified random sweep put public claims on **4 of 48 sampled breaks (8.3%, 95% CI 3.3-19.6%)**; across all collection this file holds claims on 15 of 203 breaks. Within that small, self-selected set the claims are supported about half the time — pundits are not fabricating, they are describing real swings drawn from the tail of a distribution, and the tournament-wide story is then written from that tail. The large majority of breaks generated no public narrative at all, whether or not ordinary volatility produced a swing afterwards.

- Claims cluster on a single narrative: the break rescued the favourite from
  an underdog's spell (Germany-Curacao, Brazil-Morocco, Austria-Jordan,
  Uruguay-Saudi Arabia, England-DR Congo). Small nations supply the harmed side
  in nearly every case.
- One claim (PC-010) concerns match 44, our documented exclusion — a public
  claim exists about a match no dataset we hold can adjudicate.
- Verification: all 22 claims were re-read against their source URLs
  on 2026-07-25. 19 were confirmed; 3 could not be
  and are excluded from every figure above (PC-020, PC-021, PC-022).

## Caveats
- n is small; percentages are indicative, not final.
- The support rule uses shot differential (per CHANGELOG A2, no per-shot xG).
  Several claims cite xG or touches; those are not the coded outcome.
- Several breaks carry claims from multiple independent outlets. Rows are kept
  separate (the collection unit is the claim), which is exactly why the headline
  above is the deduplicated BREAK-level rate.
