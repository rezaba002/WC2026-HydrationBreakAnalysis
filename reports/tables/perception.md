# Perception claims vs objective evidence — Core Output 5 (PILOT)

Claims collected: 13 · testable: 11 · indeterminate: 2
**Supported: 6/11 (55%)** — claim direction correct AND swing ≥80th percentile of the same match/half's pseudo-break minutes.

Evaluation was blinded to claim text: only (match, break, team-helped) was read.

| claim | match | brk | team claimed helped | Δ shot diff | null median | pctile | verdict |
|---|---|---|---|---|---|---|---|
| PC-001 | Netherlands v Sweden | 1 | Sweden | +4 | -1.0 | 100 | supported |
| PC-002 | Germany v Curaçao | 1 | Germany | +5 | -2.0 | 100 | supported |
| PC-003 | Switzerland v Bosnia and Herzegovina | 2 | Switzerland | +1 | -2.0 | 100 | supported |
| PC-004 | Austria v Jordan | 2 | Austria | +0 | +1.0 | 47 | not_supported |
| PC-005 | Brazil v Haiti | 1 | Brazil | +0 |  |  | indeterminate |
| PC-006 | England v Croatia | 1 | Croatia | +1 | +2.0 | 50 | not_supported |
| PC-007 | Germany v Curaçao | 1 | Germany | +5 | -2.0 | 100 | supported |
| PC-008 | Saudi Arabia v Uruguay | 2 | Uruguay | +1 | +0.0 | 92 | supported |
| PC-009 | Austria v Jordan | 2 | Austria | +0 | +1.0 | 47 | not_supported |
| PC-010 | Jordan v Algeria | 2 | Algeria |  |  |  | indeterminate |
| PC-011 | Brazil v Morocco | 1 | Brazil | -4 |  |  | not_supported |
| PC-012 | England v Congo DR | 1 | England | +0 | +1.0 | 38 | not_supported |
| PC-013 | England v Congo DR | 2 | England | +4 | -3.0 | 100 | supported |

## Pilot findings

- Claim supply is NOT the bottleneck the handoff feared: 13 usable
  claims came from four outlets in one collection pass, with 12 rejections
  logged. Reaching ~40 is realistic.

- **The headline is the denominator, not the hit rate.** Claims were made about only **11 of 203 breaks (5%)**. Within that tiny, self-selected set the claims are often right (6/11 supported) — which is exactly the mechanism: pundits are not fabricating, they are describing real swings drawn from the tail of a distribution, then the tournament-wide story is written from that tail. The other ~95% of breaks, where nothing happened, generated no commentary and no memory.

- Claims cluster on a single narrative: the break rescued the favourite from
  an underdog's spell (Germany-Curacao, Brazil-Morocco, Austria-Jordan,
  Uruguay-Saudi Arabia, England-DR Congo). Small nations supply the harmed side
  in nearly every case.
- One claim (PC-010) concerns match 44, our documented exclusion — a public
  claim exists about a match no dataset we hold can adjudicate.
- Verification status is `fetch_extracted` for every row: quotes were pulled
  by automated page-fetch, NOT read manually. **Manual verbatim confirmation
  against each source URL is required before publication.**

## Caveats
- Pilot n is small; percentages are indicative, not final.
- The support rule uses shot differential (per CHANGELOG A2, no per-shot xG).
  Several claims cite xG or touches; those are not the coded outcome.
- Two matches carry claims from two independent outlets (PC-002/PC-007,
  PC-004/PC-009). Kept separate deliberately: the unit is the claim.
